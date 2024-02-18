"""Buds to parse exposure time."""
from collections import namedtuple
from typing import Hashable

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.flower_pot import Thorn
from dkist_processing_common.models.tags import EXP_TIME_ROUND_DIGITS
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.task import parse_header_ip_task_with_gains
from dkist_processing_common.parsers.time import TaskExposureTimesBud

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspRampFitsAccess


class CryonirspTaskExposureTimesBud(TaskExposureTimesBud):
    """
    Overload of common TaskExposureTimesBud to allow for custom Cryonirsp parsing of ip_task_type.

    Parameters
    ----------
    stem_name : str
        The name of the stem of the tag
    ip_task_type : str
        Instrument program task type
    """

    def setter(self, fits_obj: CryonirspL0FitsAccess):
        """
        Set the value of the bud.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        # This is where it's different than the common `TaskExposureTimesBud`
        ip_task_type = parse_header_ip_task_with_gains(fits_obj)
        if ip_task_type.lower() == self.ip_task_type.lower():
            raw_exp_time = getattr(fits_obj, self.metadata_key)
            return round(raw_exp_time, 6)
        return SpilledDirt


class CryonirspTimeObsBud(Stem):
    """
    Produce a tuple of all time_obs values present in the dataset.

    The time_obs is a unique identifier for all raw frames in a single ramp. Hence, this list identifies all
    the ramps that must be processed in a data set.
    """

    def __init__(self):
        super().__init__(stem_name=CryonirspBudName.time_obs_list.value)

    def setter(self, fits_obj: CryonirspRampFitsAccess):
        """
        Set the time_obs for this fits object.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The time_obs value associated with this fits object
        """
        return fits_obj.time_obs

    def getter(self, key: Hashable) -> tuple:
        """
        Get the sorted tuple of time_obs values.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        A tuple of exposure times
        """
        time_obs_tup = tuple(sorted(set(self.key_to_petal_dict.values())))
        return time_obs_tup


_DARK_AND_POLCAL_TASK_TYPES = (TaskName.dark.value, TaskName.polcal.value)


class CryonirspNonDarkAndNonPolcalTaskExposureTimesBud(Stem):
    """Produce a tuple of all exposure times present in the dataset for a specific ip task types that are neither DARK nor POLCAL."""

    def __init__(self):
        super().__init__(
            stem_name=CryonirspBudName.non_dark_and_non_polcal_task_exposure_times.value
        )
        self.metadata_key = "fpa_exposure_time_ms"

    def setter(self, fits_obj: CryonirspL0FitsAccess) -> float | SpilledDirt:
        """
        Set the task exposure time for this fits object.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The exposure time associated with this fits object
        """
        if fits_obj.ip_task_type.upper() not in _DARK_AND_POLCAL_TASK_TYPES:
            raw_exposure_time = getattr(fits_obj, self.metadata_key)
            return round(raw_exposure_time, EXP_TIME_ROUND_DIGITS)
        return SpilledDirt

    def getter(self, key: Hashable) -> Hashable:
        """
        Get the list of exposure times.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        A tuple of exposure times
        """
        exposure_times = tuple(sorted(set(self.key_to_petal_dict.values())))
        return exposure_times


class CryonirspPickyDarkExposureTimesBud(Stem):
    """Parse exposure times to ensure existence of the necessary DARK exposure times."""

    ExposureTime = namedtuple("ExposureTime", ["is_dark", "exposure_time"])

    def __init__(self):
        super().__init__(stem_name=CryonirspBudName.picky_dark_exposure_times.value)
        self.metadata_key = "fpa_exposure_time_ms"

    def setter(self, fits_obj: CryonirspL0FitsAccess) -> tuple | SpilledDirt:
        """
        Set the task exposure time and whether it is a DARK task for this fits object.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        A tuple of a boolean indicating if the task type is dark and the exposure time associated with this fits object
        """
        raw_exposure_time = getattr(fits_obj, self.metadata_key)
        exposure_time = round(raw_exposure_time, EXP_TIME_ROUND_DIGITS)
        if fits_obj.ip_task_type.upper() == TaskName.dark.value:
            return self.ExposureTime(is_dark=True, exposure_time=exposure_time)
        if fits_obj.ip_task_type.upper() not in _DARK_AND_POLCAL_TASK_TYPES:
            return self.ExposureTime(is_dark=False, exposure_time=exposure_time)
        # Polcal falls through
        return SpilledDirt

    def getter(self, key: Hashable) -> Thorn:
        """
        Parse all exposure times and raise an error if any non-dark exposure time is missing from the set of dark exposure times.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        Thorn
        """
        exposure_times = list(self.key_to_petal_dict.values())
        dark_exposure_times = {
            exp_time.exposure_time for exp_time in exposure_times if exp_time.is_dark
        }
        other_exposure_times = {
            exp_time.exposure_time for exp_time in exposure_times if not exp_time.is_dark
        }
        other_exposure_times_missing_from_dark_exposure_times = (
            other_exposure_times - dark_exposure_times
        )
        if other_exposure_times_missing_from_dark_exposure_times:
            raise ValueError(
                f"Exposure times required in the set of dark frames not found. Missing times = {other_exposure_times_missing_from_dark_exposure_times}"
            )
        return Thorn
