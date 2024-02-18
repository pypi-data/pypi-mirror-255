"""DICOM and Flywheel metadata functions."""
import logging
import sys
import typing as t
from collections import Counter

from fw_file.dicom import DICOM, DICOMCollection
from fw_file.dicom.config import IMPLEMENTATION_CLASS_UID, IMPLEMENTATION_VERSION_NAME
from fw_file.dicom.reader import ReplaceEvent
from fw_file.dicom.utils import generate_uid
from pydicom.datadict import dictionary_VR, tag_for_keyword

log = logging.getLogger(__name__)


def update_modified_dicom_info(
    dcm: DICOM, evts: t.Optional[t.List[ReplaceEvent]] = None
) -> None:
    """Add OriginalAttributesSequence and Implementation information.

    Args:
        dcm (DICOM): DICOM to update.
    """
    add_implementation(dcm)
    if evts:
        for evt in evts:
            tag, VR = None, None
            try:
                tag = tag_for_keyword(evt.field)
                VR = dictionary_VR(evt.field)
            except ValueError:
                pass
            if not tag or not VR:
                log.debug(
                    f"Tag and VR not found for {evt.field}. Not adding to"
                    "ModifiedAttributesSequence"
                )
                continue
            value = evt.old
            dcm.read_context.add_modified_elem((tag, VR, value))

    dcm.update_orig_attrs()


def add_implementation(dcm: DICOM) -> None:
    """Write implementation information to a dicom.

    Args:
        dcm (DICOM): DICOM to update.
    """
    i_class_uid = dcm.dataset.raw.file_meta.get("ImplementationClassUID")
    i_version_name = dcm.dataset.raw.file_meta.get("ImplementationVersionName")

    if not i_class_uid or i_class_uid != IMPLEMENTATION_CLASS_UID:
        log.debug(f"Adding ImplementationClassUID: {IMPLEMENTATION_CLASS_UID}")
        setattr(dcm, "ImplementationClassUID", IMPLEMENTATION_CLASS_UID)

    if not i_version_name or i_version_name != IMPLEMENTATION_VERSION_NAME:
        log.debug(f"Addding ImplementationVersionName: {IMPLEMENTATION_VERSION_NAME}")
        setattr(dcm, "ImplementationVersionName", IMPLEMENTATION_VERSION_NAME)


def add_missing_uid(dcms: DICOMCollection) -> t.Dict[str, t.List]:
    """Check for and add missing SeriesInstanceUID.

    Args:
        dcms (DICOMCollection): Dicom to check.

    Returns:
        dict of modifications.

    Raises:
        ValueError: When multiple SeriesInstanceUIDs are present across archive
    """
    mods = dict()
    series_uid = None
    try:
        series_uid = dcms.get("SeriesInstanceUID")
    except ValueError:
        counts = Counter(dcms.bulk_get("SeriesInstanceUID"))
        log.error(
            f"Multiple SeriesInstanceUIDs found: \n{counts} " "\nPlease run splitter."
        )
        sys.exit(1)

    sops = dcms.bulk_get("SOPInstanceUID")
    if not all(sops):
        log.info("Populating missing SOPInstanceUIDs.")
        count = 0
        for dcm in dcms:
            if not dcm.get("SOPInstanceUID"):
                setattr(dcm, "SOPInstanceUID", generate_uid())
                count += 1
        mods["SOPInstanceUID"] = [f"Added x {count}"]

    sop_classes = dcms.bulk_get("SOPClassUID")
    if not all(sop_classes):
        log.info("Attempting to populate missing SOPClassUIDs.")
        count = 0
        for dcm in dcms:
            media_class = dcm.dataset.raw.file_meta.get("MediaStorageSOPClassUID")
            if not dcm.get("SOPClassUID") and media_class:
                setattr(dcm, "SOPClassUID", media_class)
                count += 1
        mods["SOPClassUID"] = [f"Added x {count}"]

    if not series_uid:
        log.info("Populating missing SeriesInstanceUID.")
        series_uid = generate_uid()
        dcms.set("SeriesInstanceUID", series_uid)
        mods["SeriesInstanceUID"] = [f"Added {series_uid}"]

    return mods
