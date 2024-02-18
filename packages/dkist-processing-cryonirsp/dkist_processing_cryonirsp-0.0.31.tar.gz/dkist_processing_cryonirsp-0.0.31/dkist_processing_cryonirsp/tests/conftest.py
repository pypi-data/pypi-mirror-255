import json
import os
from collections.abc import Iterable
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import is_dataclass
from pathlib import Path
from random import randint
from typing import Callable
from typing import Type
from typing import TypeVar

import numpy as np
import pytest
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator import spec122_validator
from dkist_header_validator.translator import sanitize_to_spec214_level1
from dkist_header_validator.translator import translate_spec122_to_spec214_l0
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.tasks import WorkflowTaskBase

from dkist_processing_cryonirsp.models.constants import CryonirspConstants
from dkist_processing_cryonirsp.models.parameters import CryonirspParameters
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tests.header_models import CryonirspCIHeaders
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeaders


def generate_fits_frame(header_generator: Iterable, shape=None) -> fits.HDUList:
    shape = shape or (1, 10, 10)
    generated_header = next(header_generator)
    translated_header = translate_spec122_to_spec214_l0(generated_header)
    del translated_header["COMMENT"]
    hdu = fits.PrimaryHDU(data=np.ones(shape=shape) * 150, header=fits.Header(translated_header))
    return fits.HDUList([hdu])


def generate_full_cryonirsp_fits_frame(
    header_generator: Iterable, data: np.ndarray | None = None
) -> fits.HDUList:
    if data is None:
        data = np.ones(shape=(1, 2000, 2560))
    data[0, 1000:, :] *= np.arange(1000)[:, None][::-1, :]  # Make beam 2 different and flip it
    generated_header = next(header_generator)
    translated_header = translate_spec122_to_spec214_l0(generated_header)
    del translated_header["COMMENT"]
    hdu = fits.PrimaryHDU(data=data, header=fits.Header(translated_header))
    return fits.HDUList([hdu])


def generate_214_l0_fits_frame(
    s122_header: fits.Header, data: np.ndarray | None = None
) -> fits.HDUList:
    """Convert S122 header into 214 L0"""
    if data is None:
        data = np.ones((1, 10, 10))
    translated_header = translate_spec122_to_spec214_l0(s122_header)
    del translated_header["COMMENT"]
    hdu = fits.PrimaryHDU(data=data, header=fits.Header(translated_header))
    return fits.HDUList([hdu])


def generate_214_l1_fits_frame(
    s122_header: fits.Header, data: np.ndarray | None = None
) -> fits.HDUList:
    """Convert S122 header into 214 L1 only.

    This does NOT include populating all L1 headers, just removing 214 L0 only headers

    NOTE: The stuff you care about will be in hdulist[1]
    """
    l0_s214_hdul = generate_214_l0_fits_frame(s122_header, data)
    l0_header = l0_s214_hdul[0].header
    l0_header["DNAXIS"] = 5
    l0_header["DAAXES"] = 2
    l0_header["DEAXES"] = 3
    l1_header = sanitize_to_spec214_level1(input_headers=l0_header)
    hdu = fits.CompImageHDU(header=l1_header, data=l0_s214_hdul[0].data)

    return fits.HDUList([fits.PrimaryHDU(), hdu])


@pytest.fixture()
def init_cryonirsp_constants_db():
    def constants_maker(recipe_run_id: int, constants_obj):
        if is_dataclass(constants_obj):
            constants_obj = asdict(constants_obj)
        constants = CryonirspConstants(recipe_run_id=recipe_run_id, task_name="test")
        constants._update(constants_obj)
        return

    return constants_maker


@dataclass
class CryonirspConstantsDb:
    ARM_ID: str = "SP"
    NUM_MODSTATES: int = 10
    NUM_MAP_SCANS: int = 2
    NUM_BEAMS: int = 2
    NUM_CS_STEPS: int = 18
    NUM_SPECTRAL_BINS: int = 1
    NUM_SPATIAL_BINS: int = 1
    NUM_SCAN_STEPS: int = 1
    NUM_SPATIAL_STEPS: int = 1
    NUM_MEAS: int = 1
    INSTRUMENT: str = "CRYO-NIRSP"
    AVERAGE_CADENCE: float = 10.0
    MINIMUM_CADENCE: float = 10.0
    MAXIMUM_CADENCE: float = 10.0
    VARIANCE_CADENCE: float = 0.0
    WAVELENGTH: float = 1082.0
    LAMP_GAIN_EXPOSURE_TIMES: tuple[float] = (100.0,)
    SOLAR_GAIN_EXPOSURE_TIMES: tuple[float] = (1.0,)
    OBSERVE_EXPOSURE_TIMES: tuple[float] = (0.01,)
    POLCAL_EXPOSURE_TIMES: tuple[float] | tuple = ()
    NON_DARK_AND_NON_POLCAL_TASK_EXPOSURE_TIMES: tuple[float] = (
        100.0,
        1.0,
        0.01,
    )
    SPECTRAL_LINE: str = "CRSP Ca II H"
    MODULATOR_SPIN_MODE: str = "Continuous"
    STOKES_PARAMS: tuple[str] = (
        "I",
        "Q",
        "U",
        "V",
    )
    TIME_OBS_LIST: tuple[str] = ()
    CONTRIBUTING_PROPOSAL_IDS: tuple[str] = (
        "PROPID1",
        "PROPID2",
    )
    CONTRIBUTING_EXPERIMENT_IDS: tuple[str] = (
        "EXPERID1",
        "EXPERID2",
        "EXPERID3",
    )
    # These are SP defaults...
    AXIS_1_TYPE: str = "AWAV"
    AXIS_2_TYPE: str = "HPLT-TAN"
    AXIS_3_TYPE: str = "HPLN-TAN"
    ROI_1_ORIGIN_X: int = 0
    ROI_1_ORIGIN_Y: int = 0
    ROI_1_SIZE_X: int = 2048
    ROI_1_SIZE_Y: int = 2048
    PICKY_DARK_EXPOSURE_TIMES: tuple[float] = (
        5.0,
        6.0,
        7.0,
        10.0,
        99.0,
    )


@pytest.fixture()
def recipe_run_id():
    return randint(0, 99999)


@pytest.fixture()
def cryonirsp_ci_headers() -> fits.Header:
    """
    A header with some common by-frame CI keywords
    """
    ds = CryonirspCIHeaders(dataset_shape=(2, 10, 10), array_shape=(1, 10, 10), time_delta=1)
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]

    return header_list[0]


@pytest.fixture()
def calibrated_ci_cryonirsp_headers(cryonirsp_ci_headers) -> fits.Header:
    """
    Same as cryonirsp_ci_headers but with a DATE-END key.

    Because now that's added during ScienceCal
    """
    cryonirsp_ci_headers["DATE-END"] = (
        Time(cryonirsp_ci_headers["DATE-BEG"], format="isot", precision=6)
        + TimeDelta(float(cryonirsp_ci_headers["TEXPOSUR"]) / 1000, format="sec")
    ).to_value("isot")

    return cryonirsp_ci_headers


@pytest.fixture()
def cryonirsp_headers() -> fits.Header:
    """
    A header with some common by-frame keywords
    """
    ds = CryonirspHeaders(dataset_shape=(2, 10, 10), array_shape=(1, 10, 10), time_delta=1)
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]

    return header_list[0]


@pytest.fixture()
def calibrated_cryonirsp_headers(cryonirsp_headers) -> fits.Header:
    """
    Same as cryonirsp_headers but with a DATE-END key.

    Because now that's added during ScienceCal
    """
    cryonirsp_headers["DATE-END"] = (
        Time(cryonirsp_headers["DATE-BEG"], format="isot", precision=6)
        + TimeDelta(float(cryonirsp_headers["TEXPOSUR"]) / 1000, format="sec")
    ).to_value("isot")

    return cryonirsp_headers


@dataclass
class WavelengthParameter:
    values: tuple
    wavelength: tuple = (1074.5, 1074.7, 1079.8, 1083)  # This must always be in order

    def __hash__(self):
        return hash((self.values, self.wavelength))


@dataclass
class FileParameter:
    """For parameters that are files on disk."""

    param_path: str
    is_file: bool = True
    objectKey: str = "not_used_because_its_already_converted"
    bucket: str = "not_used_because_we_dont_transfer"
    # Note: we have these as already-parsed file parameter (i.e., no "__file__") mainly because it allows us to have
    #       parameter files that are outside of the workflow basepath (where they would not be able to be tagged with
    #       PARAMETER_FILE). This is a pattern that we see in grogu testing.
    #       A downside of this approach is that we are slightly more fragile to changes in the underlying __file__ parsing
    #       in `*-common`. Apologies to any future devs who run into this problem. To fix it you'll need to make
    #       downstream fixtures aware of the actual files so they can be tagged prior to the instantiation of the
    #       Parameter object on some Task.


# These constants are used to prevent name errors in _create_parameter_files
# and in CryonirspTestingParameters
LINEARIZATION_THRESHOLDS_CI = "cryonirsp_linearization_thresholds_ci.npy"
LINEARIZATION_THRESHOLDS_SP = "cryonirsp_linearization_thresholds_sp.npy"
LINEARIZATION_POLYFIT_COEFFS_CI = "cryonirsp_linearization_polyfit_coeffs_ci.npy"
LINEARIZATION_POLYFIT_COEFFS_SP = "cryonirsp_linearization_polyfit_coeffs_sp.npy"


def _create_parameter_files(param_path: Path) -> None:
    thresh = np.ones((10, 10), dtype=np.float32) * 100.0
    polyfit = np.array([1, 0, 0, 0], dtype=np.float32)
    np.save(os.path.join(param_path, LINEARIZATION_THRESHOLDS_CI), thresh)
    np.save(os.path.join(param_path, LINEARIZATION_THRESHOLDS_SP), thresh)
    np.save(os.path.join(param_path, LINEARIZATION_POLYFIT_COEFFS_CI), polyfit)
    np.save(os.path.join(param_path, LINEARIZATION_POLYFIT_COEFFS_SP), polyfit)


TestingParameters = TypeVar("TestingParameters", bound="CryonirspTestingParameters")


def cryonirsp_testing_parameters_factory(
    param_path: Path | str = "", create_files: bool = True
) -> TestingParameters:
    """Create the InputDatasetParameterValue objects and write the parameter files."""
    if isinstance(param_path, str):
        param_path = Path(param_path)
    absolute_path = param_path.absolute()

    if create_files:
        _create_parameter_files(absolute_path)

    @dataclass
    class CryonirspTestingParameters:
        cryonirsp_polcal_num_spatial_bins: int = 1
        cryonirsp_polcal_num_spectral_bins: int = 1
        cryonirsp_polcal_pac_fit_mode: str = "use_M12"
        cryonirsp_polcal_pac_init_set: str = "OCCal_VIS"
        cryonirsp_geo_upsample_factor: float = 100.0
        cryonirsp_geo_max_shift: float = 40.0
        cryonirsp_geo_poly_fit_order: int = 3
        cryonirsp_geo_spatial_gradient_displacement: int = 4
        cryonirsp_geo_strip_spatial_size_fraction: float = 0.5
        cryonirsp_geo_strip_spectral_size_fraction: float = 0.05
        cryonirsp_geo_strip_spectral_offset_size_fraction: float = 0.25
        cryonirsp_solar_characteristic_spatial_normalization_percentile: float = 80.0
        cryonirsp_max_cs_step_time_sec: float = 30.0
        cryonirsp_beam_boundaries_smoothing_disk_size: int = 3
        cryonirsp_beam_boundaries_upsample_factor: int = 10
        cryonirsp_beam_boundaries_sp_beam_transition_region_size_fraction: float = 0.05
        cryonirsp_bad_pixel_map_median_filter_size_sp: list[int] = field(
            default_factory=lambda: [20, 1]
        )
        cryonirsp_bad_pixel_map_median_filter_size_ci: list[int] = field(
            default_factory=lambda: [5, 5]
        )
        cryonirsp_bad_pixel_map_threshold_factor: float = 5.0
        cryonirsp_corrections_bad_pixel_median_filter_size: int = 8
        cryonirsp_linearization_thresholds_ci: FileParameter = field(
            default_factory=lambda: FileParameter(
                param_path=str(absolute_path / LINEARIZATION_THRESHOLDS_CI)
            )
        )
        cryonirsp_linearization_polyfit_coeffs_ci: FileParameter = field(
            default_factory=lambda: FileParameter(
                param_path=str(absolute_path / LINEARIZATION_POLYFIT_COEFFS_CI)
            )
        )
        cryonirsp_linearization_thresholds_sp: FileParameter = field(
            default_factory=lambda: FileParameter(
                param_path=str(absolute_path / LINEARIZATION_THRESHOLDS_SP)
            )
        )
        cryonirsp_linearization_polyfit_coeffs_sp: FileParameter = field(
            default_factory=lambda: FileParameter(
                param_path=str(absolute_path / LINEARIZATION_POLYFIT_COEFFS_SP)
            )
        )
        cryonirsp_linearization_max_memory_gb: float = 4.0
        cryonirsp_linearization_optical_density_filter_attenuation_g278: WavelengthParameter = (
            WavelengthParameter(values=(-1.64, -1.64, -1.64, -1.64))
        )
        cryonirsp_linearization_optical_density_filter_attenuation_g358: WavelengthParameter = (
            WavelengthParameter(values=(-3.75, -3.75, -3.75, -3.75))
        )
        cryonirsp_linearization_optical_density_filter_attenuation_g408: WavelengthParameter = (
            WavelengthParameter(values=(-4.26, -4.26, -4.26, -4.26))
        )

    return CryonirspTestingParameters


@pytest.fixture(scope="session")
def testing_wavelength() -> float:
    return 1079.6


@pytest.fixture(scope="session")
def input_dataset_document_simple_parameters_part():
    def get_input_dataset_parameters_part(parameters):
        parameters_list = []

        value_id = randint(1000, 2000)
        for pn, pv in asdict(parameters).items():
            values = [
                {
                    "parameterValueId": value_id,
                    "parameterValue": json.dumps(pv),
                    "parameterValueStartDate": "1946-11-20",  # Remember Duane Allman
                }
            ]
            parameter = {"parameterName": pn, "parameterValues": values}
            parameters_list.append(parameter)
        return parameters_list

    return get_input_dataset_parameters_part


@pytest.fixture(scope="session")
def assign_input_dataset_doc_to_task(
    input_dataset_document_simple_parameters_part,
    testing_wavelength,
):
    def update_task(task, parameters):
        doc_path = task.scratch.workflow_base_path / "dataset_doc.json"
        with open(doc_path, "w") as f:
            f.write(json.dumps(input_dataset_document_simple_parameters_part(parameters)))
        task.tag(doc_path, CryonirspTag.input_dataset_parameters())
        task.parameters = CryonirspParameters(
            task.input_dataset_parameters,
            wavelength=testing_wavelength,
            arm_id=getattr(task.constants, "arm_id", None),
        )

    return update_task


def _write_frames_to_task(
    task: Type[WorkflowTaskBase],
    frame_generator: Spec122Dataset,
    change_translated_headers: Callable[[fits.Header], fits.Header] = lambda x: x,
    tag_ramp_frames: Callable[[fits.Header], list[str]] = lambda x: [],
    extra_tags: list[str] | None = None,
    tag_func: Callable[[CryonirspHeaders], list[str]] = lambda x: [],
):
    if not extra_tags:
        extra_tags = []
    tags = [CryonirspTag.frame()] + extra_tags

    num_frames = 0

    frame = next(frame_generator)

    header = frame.header()
    data = frame.data
    frame_tags = tags + tag_func(frame)
    translated_header = fits.Header(translate_spec122_to_spec214_l0(header))
    translated_header = change_translated_headers(translated_header)
    ramp_tags = tag_ramp_frames(translated_header)
    frame_tags = frame_tags + ramp_tags

    task.write(data=data, header=translated_header, tags=frame_tags, encoder=fits_array_encoder)
    num_frames += 1

    return num_frames
