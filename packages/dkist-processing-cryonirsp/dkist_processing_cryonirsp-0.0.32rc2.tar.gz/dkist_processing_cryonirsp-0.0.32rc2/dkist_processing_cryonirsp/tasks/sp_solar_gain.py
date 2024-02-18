"""Cryo SP solar gain task."""
import numpy as np
import scipy.ndimage as spnd
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration import logger

from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase

__all__ = ["SPSolarGainCalibration"]


class SPSolarGainCalibration(CryonirspTaskBase):
    """Task class for generating Solar Gain images for each beam.

    NB: This class does not extend GainCalibrationBase, because it is highly customized
    and incorporates several correction steps as well as solar spectrum removal.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    record_provenance = True

    def run(self):
        """
        For each beam.

            - Do dark, lamp, and geometric corrections
            - Compute the characteristic spectra
            - Re-apply the spectral curvature to the characteristic spectra
            - Re-apply angle and state offset distortions to the characteristic spectra
            - Remove the distorted characteristic solar spectra from the original spectra
            - Write master solar gain

        Returns
        -------
        None

        """
        target_exposure_times = self.constants.solar_gain_exposure_times

        with self.apm_step(f"Computing SP gain calibrations for {target_exposure_times=}"):
            for exposure_time in target_exposure_times:
                for beam in range(1, self.constants.num_beams + 1):
                    with self.apm_processing_step(
                        f"Perform initial corrections for {beam = } and {exposure_time = }"
                    ):
                        spectral_corrected_solar_array = self._do_initial_corrections(
                            beam=beam, exposure_time=exposure_time
                        )
                    with self.apm_processing_step(
                        f"Compute the characteristic spectrum for {beam = } and {exposure_time = }"
                    ):
                        char_spectrum = self._compute_char_spectrum(
                            array=spectral_corrected_solar_array,
                        )
                    with self.apm_processing_step(
                        f"Re-apply the spectral and geometric distortions for {beam = } and {exposure_time = }"
                    ):
                        distorted_char_spectrum = self._distort_char_spectrum(char_spectrum)
                    with self.apm_processing_step(
                        f"Remove the solar spectrum for {beam = } and {exposure_time = }"
                    ):
                        # This is the final gain image, as we do not normalize
                        final_gain = self._remove_solar_signal(
                            char_solar_spectra=distorted_char_spectrum,
                            beam=beam,
                            exposure_time=exposure_time,
                        )
                    with self.apm_writing_step(
                        f"Writing the final solar gain array for {beam = } and {exposure_time = }"
                    ):
                        self._write_solar_gain_calibration(
                            gain_array=final_gain,
                            beam=beam,
                            exposure_time=exposure_time,
                        )

            with self.apm_processing_step("Computing and logging quality metrics"):
                no_of_raw_solar_frames: int = self.scratch.count_all(
                    tags=[
                        CryonirspTag.linearized(),
                        CryonirspTag.frame(),
                        CryonirspTag.task_solar_gain(),
                    ],
                )
                self.quality_store_task_type_counts(
                    task_type=TaskName.solar_gain.value, total_frames=no_of_raw_solar_frames
                )

    def _do_initial_corrections(self, beam: int, exposure_time: float) -> np.ndarray:
        """Perform dark, bad pixel, and lamp corrections on the input solar gain data."""
        # Do the basic dark and bad pixel corrections
        basic_corrected_solar_array = self._do_dark_and_bad_pixel_corrections(beam, exposure_time)
        # Gain correct using the lamp gain. This removes internal optical effects.
        lamp_array = self.intermediate_frame_load_lamp_gain_array(beam=beam)
        lamp_corrected_solar_array = next(
            divide_arrays_by_array(basic_corrected_solar_array, lamp_array)
        )
        # Do the rotation and spectral corrections
        spectral_corrected_solar_array = self._do_geometric_corrections(
            lamp_corrected_solar_array, beam
        )
        return spectral_corrected_solar_array

    def _do_dark_and_bad_pixel_corrections(self, beam: int, exposure_time: float) -> np.ndarray:
        """Perform dark and bad pixel corrections on the input solar gain data."""
        # Load the necessary files
        dark_array = self.intermediate_frame_load_dark_array(beam=beam, exposure_time=exposure_time)
        # Compute the avg solar array
        linearized_solar_arrays = self.linearized_frame_gain_array_generator(
            beam=beam, exposure_time=exposure_time, gain_type=TaskName.solar_gain.value
        )
        avg_solar_array = average_numpy_arrays(linearized_solar_arrays)
        # Dark correct it
        dark_corrected_solar_array = next(subtract_array_from_arrays(avg_solar_array, dark_array))
        # Correct for bad pixels
        bad_pixel_map = self.intermediate_frame_load_bad_pixel_map(beam=beam)
        bad_pixel_corrected_solar_array = self.corrections_correct_bad_pixels(
            dark_corrected_solar_array, bad_pixel_map
        )
        # Save as intermediate result for final gain computation
        self.intermediate_frame_write_arrays(
            arrays=bad_pixel_corrected_solar_array,
            beam=beam,
            task="SC_DARK_BP_CORRECTED_ONLY",
            exposure_time=exposure_time,
        )
        return bad_pixel_corrected_solar_array

    def _do_geometric_corrections(self, lamp_corrected_array: np.ndarray, beam: int) -> np.ndarray:
        """Perform geometric corrections on the input solar gain data."""
        # Get the parameters and save them to self for use later on...
        self.angle = self.intermediate_frame_load_angle(beam=beam)
        self.state_offset = self.intermediate_frame_load_state_offset(beam=beam)
        self.spec_shift = self.intermediate_frame_load_spec_shift(beam=beam)
        # Correct for rotation and state offset. This does not correct for spectral curvature!
        geo_corrected_solar_array = next(
            self.corrections_correct_geometry(lamp_corrected_array, self.state_offset, self.angle)
        )
        # Remove the spectral curvature
        spectral_corrected_solar_array = next(
            self.corrections_remove_spec_shifts(geo_corrected_solar_array, self.spec_shift)
        )
        return spectral_corrected_solar_array

    def _compute_char_spectrum(self, array: np.ndarray) -> np.ndarray:
        """Estimate the characteristic solar spectrum from the corrected solar gain data."""
        # Normalize data row by row
        pct = self.parameters.solar_characteristic_spatial_normalization_percentile
        array_row_norm = array / np.nanpercentile(array, pct, axis=1)[:, None]
        # Compute characteristic spectrum
        char_spec_1d = np.nanmedian(array_row_norm, axis=0)
        # Expand the 1D median along the columns (along the slit)
        median_char_spec_2d = np.tile(char_spec_1d, (array_row_norm.shape[0], 1))
        return median_char_spec_2d

    def _distort_char_spectrum(self, char_spec: np.ndarray) -> np.ndarray:
        """Re-apply the geometric distortions, that were previously removed, to the characteristic spectrum."""
        # Re-distort the characteristic spectrum in the reverse order from the earlier correction
        # 1. Add spectral curvature back
        reshifted_spectrum = next(
            self.corrections_remove_spec_shifts(arrays=char_spec, spec_shift=-self.spec_shift)
        )
        # 2. Add state offset and angular rotation back
        distorted_spectrum = next(
            self.corrections_distort_geometry(
                reshifted_spectrum,
                -self.state_offset,
                -self.angle,
            )
        )
        return distorted_spectrum

    def _geo_corrected_data(self, beam: int, exposure_time: float) -> np.ndarray:
        """Read the intermediate dark and bad-pixel corrected solar data saved previously."""
        array_generator = self.intermediate_frame_load_intermediate_arrays(
            tags=[
                CryonirspTag.task("SC_DARK_BP_CORRECTED_ONLY"),
                CryonirspTag.beam(beam),
                CryonirspTag.exposure_time(exposure_time),
            ]
        )
        return next(array_generator)

    def _remove_solar_signal(
        self,
        char_solar_spectra: np.ndarray,
        beam: int,
        exposure_time: float,
    ) -> np.ndarray:
        """Remove the (distorted) characteristic solar spectra from the input solar data."""
        logger.info(f"Removing characteristic solar spectra from {beam=} and {exposure_time=}")
        input_gain = self._geo_corrected_data(beam=beam, exposure_time=exposure_time)
        array_with_solar_signal_removed = input_gain / char_solar_spectra
        return array_with_solar_signal_removed

    def _write_solar_gain_calibration(
        self, gain_array: np.ndarray, beam: int, exposure_time: float
    ) -> None:
        """Write the final gain array as a file."""
        logger.info(f"Writing final SolarGain for {beam=}")
        self.intermediate_frame_write_arrays(
            arrays=gain_array,
            beam=beam,
            task_tag=CryonirspTag.task_solar_gain(),
            exposure_time=exposure_time,
        )

        # These lines are here to help debugging and can be removed if really necessary
        filename = next(
            self.read(
                tags=[
                    CryonirspTag.intermediate(),
                    CryonirspTag.beam(beam),
                    CryonirspTag.task_solar_gain(),
                    CryonirspTag.exposure_time(exposure_time),
                ]
            )
        )
        logger.info(f"Wrote solar gain for {beam=} and {exposure_time=} to {filename}")
