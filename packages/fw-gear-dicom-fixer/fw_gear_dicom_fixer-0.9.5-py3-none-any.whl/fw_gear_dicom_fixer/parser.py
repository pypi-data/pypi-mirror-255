"""Parser module to parse gear config.json."""
import logging
import typing as t
from pathlib import Path

import psutil
from flywheel_gear_toolkit import GearToolkitContext
from fw_file.dicom import get_config
from humanize import naturalsize

from fw_gear_dicom_fixer.utils import calculate_decompressed_size

log = logging.getLogger(__name__)


def parse_config(
    gear_context: GearToolkitContext,
) -> t.Tuple[Path, bool, bool, str]:
    """Parse config.json and return relevant inputs and options."""
    input_path = Path(gear_context.get_input_path("dicom")).resolve()
    transfer_syntax = gear_context.config.get("standardize_transfer_syntax", False)
    force_decompress = gear_context.config.get("force_decompress")
    unique = gear_context.config.get("unique", False)
    zip_single = gear_context.config.get("zip-single-dicom", "match")

    config = get_config()
    config.reading_validation_mode = (
        "2" if gear_context.config.get("strict-validation", True) else "1"
    )
    if gear_context.config.get("dicom-standard", "local") == "current":
        config.standard_rev = "current"

    # Check memory availability and filesize to catch potential OOM kill
    # on decompression if transfer_syntax == True
    fail_status = False
    if transfer_syntax:
        current_memory = psutil.virtual_memory().used
        decompressed_size = calculate_decompressed_size(input_path)
        total_memory = psutil.virtual_memory().total
        if (current_memory + decompressed_size) > (0.7 * total_memory):
            if force_decompress is True:
                log.warning(
                    "DICOM file may be too large for decompression:\n"
                    f"\tEstimated decompressed size: {naturalsize(decompressed_size)}\n"
                    f"\tCurrent memory usage: {naturalsize(current_memory)}\n"
                    f"\tTotal memory: {naturalsize(total_memory)}\n"
                    "force_decompress is set to True, continuing as configured."
                )
            else:
                log.warning(
                    "DICOM file may be too large for decompression:\n"
                    f"\tEstimated decompressed size: {naturalsize(decompressed_size)}\n"
                    f"\tCurrent memory usage: {naturalsize(current_memory)}\n"
                    f"\tTotal memory: {naturalsize(total_memory)}\n"
                    "To avoid gear failure due to OOM, standardize_transfer_syntax "
                    "will be switched to False and the DICOM will not be decompressed. "
                    "To force decompression, re-run gear with `force_decompress=True`."
                )
                transfer_syntax = False
                fail_status = True

    return input_path, transfer_syntax, unique, zip_single, fail_status
