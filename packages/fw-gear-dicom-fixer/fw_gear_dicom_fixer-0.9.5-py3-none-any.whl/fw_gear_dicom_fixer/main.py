"""Main module."""

import hashlib
import logging
import traceback
import typing as t
import warnings
import zipfile
from collections import defaultdict
from pathlib import Path

from fw_file.dicom import DICOM, DICOMCollection
from fw_file.dicom.utils import sniff_dcm
from fw_file.dicom.validation import get_standard
from pydicom.datadict import keyword_for_tag

from .fixers import apply_fixers, decode_dcm, is_dcm, standardize_transfer_syntax
from .metadata import add_missing_uid, update_modified_dicom_info

log = logging.getLogger(__name__)


# Constant for max length of the events for a given tag
MAX_EVENT_LENGTH = 10


def run(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    dicom_path: Path,
    out_dir: Path,
    transfer_syntax: bool,
    unique: bool,
    zip_single: str,
) -> t.Optional[t.Dict[str, t.List[str]]]:
    """Run dicom fixer.

    Args:
        dicom_path (str): Path to directory containing dicom files.
        out_dir (Path): Path to directory to store outputs.
        transfer_syntax (bool): Change transfer syntax to explicit.
        unique (bool): Remove duplicates.
        zip_single (str): Zip a single dicom output.

    Returns:
        dict: Events dictionary with DICOM tags as keys, and sets of
            replace events as values. If None, indicates gear failure.
    """
    events: t.Dict[str, t.Set[str]] = defaultdict(set)
    log.info("Loading dicom")
    sops: t.Set[str] = set()
    hashes: t.Set[str] = set()
    to_del: t.List[int] = []
    updated_transfer_syntax = False
    gear_fail = False
    # First check dicom signature since zip file signature is more likely to
    # have false positives [GEAR-2841]
    if sniff_dcm(dicom_path):
        dcms = DICOMCollection(dicom_path, filter_fn=is_dcm, force=True)
    elif zipfile.is_zipfile(str(dicom_path)):
        dcms = DICOMCollection.from_zip(dicom_path, filter_fn=is_dcm, force=True)
    else:
        raise RuntimeError(
            "Invalid file type passed in, not a DICOM nor a Zip Archive."
        )
    # Download and cache the DICOM standard as needed before we start reading
    # decoding dicoms.
    get_standard()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        coll_len = len(dcms)
        if not coll_len:
            log.info("No valid dicoms found, exiting.")
            return
        decis = int(coll_len / 10) or 1
        log.info(f"Processing {coll_len} files in collection")
        for i, dcm in enumerate(dcms):
            if i % decis == 0:
                log.info(f"{i}/{coll_len} ({100*i/coll_len:.2f}%)")
            filename = dcm.filepath.split("/")[-1]
            if unique:
                dcm_hash, sop_instance = get_uniqueness(dcm)
                if dcm_hash in hashes or sop_instance in sops:
                    log.warning(f"Found duplicate dicom at {filename}")
                    to_del.append(i)
                    continue
                hashes.add(dcm_hash)
                sops.add(sop_instance)
            decode_dcm(dcm)
            if transfer_syntax:
                try:
                    updated_transfer_syntax = standardize_transfer_syntax(dcm)
                except AttributeError:
                    gear_fail = True
                    fail_reason = "Decompression failed due to large file size"
            # Update events from decoding
            dcm.read_context.trim()
            for element in dcm.read_context.data_elements:
                if element.events:
                    tagname = str(element.tag).replace(",", "")
                    kw = keyword_for_tag(element.tag)
                    if kw:
                        tagname = kw
                    events[tagname].update([str(ev) for ev in element.events])
            fix_evts = apply_fixers(dcm)

            # Handle post-decoding events from fixers (patient sex, incorrect
            # units, etc.)
            for fix in fix_evts:
                events[fix.field].add(repr(fix))
            update_modified_dicom_info(dcm, fix_evts)
    if unique:
        if to_del:
            log.info(f"Removing {len(to_del)} duplicates")
            # Remove from the end to avoid shifting indexes on deletion
            for d in reversed(sorted(to_del)):
                del dcms[d]
        else:
            log.info("No duplicate frames found.")
    unique_warnings = handle_warnings(w)
    for msg, count in unique_warnings.items():
        log.warning(f"{msg} x {count} across archive")
    uid_modifications = add_missing_uid(dcms)

    # Add uid modifications to output events
    for uid, evts in uid_modifications.items():
        events[uid] = events[uid].union(set(evts))

    out_events = trim_events(events)
    out_name = get_output_filename(dicom_path, dcms, zip_single)

    fix_events = len(out_events) > 0 and any(len(ev) > 0 for ev in out_events.values())
    removed_duplicates = unique and len(to_del)
    changed_file_name = out_name != dicom_path.name

    if updated_transfer_syntax:
        out_events.update({"TransferSyntaxUID": [updated_transfer_syntax]})
    if gear_fail:
        out_events.update({"Gear Fail": [fail_reason]})
    write_criteria = [
        fix_events,
        uid_modifications,
        updated_transfer_syntax,
        removed_duplicates,
        changed_file_name,
    ]

    if any(write_criteria):
        msg = (
            "Writing output because: " + "Fixes applied, "
            if fix_events
            else "" + "Added UID(s), "
            if uid_modifications
            else "" + "Update transfer syntax, "
            if updated_transfer_syntax
            else "" + "Removed duplicate frames, "
            if removed_duplicates
            else "" + "Changed file name, "
            if changed_file_name
            else ""
        )
        msg = msg[:-2] + "."
        log.info(msg)
        try:
            # Remove zip suffix
            if out_name.endswith(".zip"):
                dcms.to_zip(out_dir / out_name)
            else:
                dcms[0].save(out_dir / out_name)
            log.info(f"Wrote output to {out_dir / out_name}")
        except Exception as exc:  # pylint: disable=broad-except
            trace = traceback.format_exc()
            msg = f"Got exception saving dicom(s): {str(exc)}\n{trace}"
            # Ensure no output is uploaded
            (out_dir / out_name).unlink(missing_ok=True)
            log.error(msg)
            return None

    return out_events


def get_output_filename(in_file, dcms, zip_single):
    """Write output file.

    Base on input and zip_single, will do one of the following:
        - always zip single dicoms (yes)
        - never zip single dicoms (no)
        - choose to zip single dicoms or not based on input (zip/dcm) (match)

    Args:
        in_file (Path): Path to input file.
        dcms (DICOMCollection): Input Dicom collection.
        zip_single (str): 'no', 'yes' or 'match', see description above.
    """
    # Remove zip suffix
    dest = in_file.name.replace(".zip", "")
    if zip_single == "yes":
        # Always zip
        dest += ".zip"
        return dest
    if zip_single == "no":
        if len(dcms) > 1:
            # Still zip if collection has more than 1 file
            dest += ".zip"
            return dest
        # Otherwise no zip
        return dest
    if len(dcms) > 1:
        # Still zip if collection has more than 1 file
        dest += ".zip"
        return dest
    # Match
    return in_file.name


def handle_warnings(
    warning_list: t.List[warnings.WarningMessage],
) -> t.Dict[t.Union[Warning, str], int]:
    """Find unique warnings and their counts from a list of warnings.

    Returns:
        Dictionary of warnings/str as key and int counts as value
    """
    warnings_dict: t.Dict[t.Union[Warning, str], int] = {}
    for warning in warning_list:
        msg = str(warning.message)
        if msg in warnings_dict:
            warnings_dict[msg] += 1
        else:
            warnings_dict[msg] = 1
    return warnings_dict


def get_uniqueness(dcm: DICOM) -> t.Tuple[str, str]:
    """Get uniqueness of a dicom by InstanceNumber and hash of file.

    Args:
        dcm (DICOM): _description_

    Returns:
        t.Tuple[str, int]: _description_
    """
    path = dcm.filepath
    digest = ""
    with open(path, "rb") as fp:
        md5Hash = hashlib.md5(fp.read())
        digest = md5Hash.hexdigest()
    return digest, dcm.get("SOPInstanceUID", "")


def trim_events(events: t.Dict[str, t.Set[str]]) -> t.Dict[str, t.List[str]]:
    """Trim events down.

    Not all information in events is relevant, so for fields with many unique
    replacements, we can trim those down to just a few for the user to get a sense
    of what was changed.
    """
    new_evts: t.Dict[str, t.List[str]] = {}
    for tag in events.keys():
        evts = sorted(list(events[tag]))
        num_evts = len(evts)
        if num_evts > MAX_EVENT_LENGTH:
            top_n = int(MAX_EVENT_LENGTH / 2)
            evts = [
                *evts[:top_n],
                f"...{num_evts - MAX_EVENT_LENGTH} more items...",
                *evts[(num_evts - top_n) :],
            ]
        new_evts[tag] = evts
    return new_evts
