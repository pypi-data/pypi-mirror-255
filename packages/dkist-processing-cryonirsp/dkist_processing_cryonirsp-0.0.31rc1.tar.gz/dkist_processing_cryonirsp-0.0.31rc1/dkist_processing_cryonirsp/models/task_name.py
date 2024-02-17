"""List of intermediate task names."""
from enum import Enum


class CryonirspTaskName(str, Enum):
    """Controlled list of CryoNirsp task tag names."""

    beam_boundaries = "BEAM_BOUNDARIES"
    bad_pixel_map = "BAD_PIXEL_MAP"
    polcal_dark = "POLCAL_DARK"
    polcal_gain = "POLCAL_GAIN"
