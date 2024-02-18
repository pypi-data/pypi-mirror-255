import re
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Callable
from typing import Type

import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tests.conftest import FakeGQLClient

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.optical_density_filters import (
    ALLOWABLE_OPTICAL_DENSITY_FILTERS,
)
from dkist_processing_cryonirsp.parsers.polarimetric_check import PolarimetricCheckingUniqueBud
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspLinearizedData
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspRampData
from dkist_processing_cryonirsp.tests.conftest import _write_frames_to_task
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeaders
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeadersValidNonLinearizedFrames
from dkist_processing_cryonirsp.tests.header_models import ModulatedDarkHeaders
from dkist_processing_cryonirsp.tests.header_models import ModulatedLampGainHeaders
from dkist_processing_cryonirsp.tests.header_models import ModulatedObserveHeaders
from dkist_processing_cryonirsp.tests.header_models import ModulatedPolcalHeaders
from dkist_processing_cryonirsp.tests.header_models import ModulatedSolarGainHeaders


def write_dark_frames_to_task(
    task: Type[WorkflowTaskBase],
    exp_time_ms: float,
    array_shape=(2, 2, 1),
    tags: list[str] | None = None,
):
    frame_generator = ModulatedDarkHeaders(array_shape=array_shape, exp_time_ms=exp_time_ms)

    num_frames = _write_frames_to_task(task=task, frame_generator=frame_generator, extra_tags=tags)

    return num_frames


def write_lamp_gain_frames_to_task(
    task: Type[WorkflowTaskBase],
    exp_time_ms: float = 10.0,
    array_shape=(2, 2, 1),
    tags: list[str] | None = None,
    tag_func: Callable[[CryonirspHeaders], list[str]] = lambda x: [],
):
    frame_generator = ModulatedLampGainHeaders(array_shape=array_shape, exp_time_ms=exp_time_ms)

    num_frames = _write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        extra_tags=tags,
        tag_func=tag_func,
    )

    return num_frames


def write_solar_gain_frames_to_task(
    task: Type[WorkflowTaskBase],
    exp_time_ms: float = 5.0,
    array_shape=(2, 2, 1),
    tags: list[str] | None = None,
):
    frame_generator = ModulatedSolarGainHeaders(array_shape=array_shape, exp_time_ms=exp_time_ms)

    num_frames = _write_frames_to_task(task=task, frame_generator=frame_generator, extra_tags=tags)

    return num_frames


def write_polcal_frames_to_task(
    task: Type[WorkflowTaskBase],
    num_modstates: int,
    num_map_scans: int,
    extra_headers: dict,
    exp_time_ms: float = 7.0,
    array_shape=(2, 2, 1),
    tags: list[str] | None = None,
):
    num_frames = 0

    for map_scan in range(1, num_map_scans + 1):
        for mod_state in range(1, num_modstates + 1):
            frame_generator = ModulatedPolcalHeaders(
                num_modstates=num_modstates,
                modstate=mod_state,
                array_shape=array_shape,
                exp_time_ms=exp_time_ms,
                extra_headers=extra_headers,
            )

            _write_frames_to_task(task=task, frame_generator=frame_generator, extra_tags=tags)
            num_frames += 1

    return num_frames


def write_observe_frames_to_task(
    task: Type[WorkflowTaskBase],
    num_modstates: int,
    num_scan_steps: int,
    num_map_scans: int,
    num_sub_repeats: int,
    arm_id: str,
    change_translated_headers: Callable[[fits.Header | None], fits.Header] = lambda x: x,
    exp_time_ms: float = 6.0,
    array_shape=(2, 2, 1),
    tags: list[str] | None = None,
):
    num_frames = 0

    start_time = datetime.now()
    frame_delta_time = timedelta(seconds=10)
    for map_scan in range(1, num_map_scans + 1):
        for mod_state in range(1, num_modstates + 1):
            for scan_step in range(1, num_scan_steps + 1):
                for repeat in range(1, num_sub_repeats + 1):
                    frame_generator = ModulatedObserveHeaders(
                        start_date=start_time.isoformat(),
                        num_modstates=num_modstates,
                        modstate=mod_state,
                        num_map_scans=num_map_scans,
                        map_scan=map_scan,
                        num_sub_repeats=num_sub_repeats,
                        sub_repeat_num=repeat,
                        array_shape=array_shape,
                        exp_time_ms=exp_time_ms,
                        num_scan_steps=num_scan_steps,
                        scan_step=scan_step,
                        num_meas=1,
                        arm_id=arm_id,
                    )
                    start_time += frame_delta_time

                    _write_frames_to_task(
                        task=task,
                        frame_generator=frame_generator,
                        extra_tags=tags,
                        change_translated_headers=change_translated_headers,
                    )

                    num_frames += 1

    return num_frames


def write_non_linearized_frames(
    task: Type[WorkflowTaskBase],
    arm_id: str,
    start_time: str,
    camera_readout_mode: str,
    change_translated_headers: Callable[[fits.Header | None], fits.Header] = lambda x: x,
    tags: list[str] | None = None,
):
    frame_generator = CryonirspHeadersValidNonLinearizedFrames(
        arm_id=arm_id,
        camera_readout_mode=camera_readout_mode,
        dataset_shape=(2, 2, 2),
        array_shape=(1, 2, 2),
        time_delta=10,
        roi_x_origin=0,
        roi_y_origin=0,
        roi_x_size=2,
        roi_y_size=2,
        date_obs=start_time,
        exposure_time=0.01,
    )

    def tag_ramp_frames(translated_header):
        ramp_tags = [
            CryonirspTag.curr_frame_in_ramp(translated_header["CNCNDR"]),
        ]

        return ramp_tags

    for frame in frame_generator:
        _write_frames_to_task(
            task=task,
            frame_generator=frame,
            change_translated_headers=change_translated_headers,
            extra_tags=tags,
            tag_ramp_frames=tag_ramp_frames,
        )


def make_linearized_test_frames(
    task,
    arm_id: str,
    dark_exp_times: list[float],
    num_modstates: int,
    num_scan_steps: int,
    change_translated_headers: Callable[[fits.Header | None], fits.Header] = lambda x: x,
    num_map_scans: int = 1,
    num_sub_repeats: int = 1,
    extra_headers: dict | None = None,
):
    num_dark = 0
    num_polcal = 0
    num_obs = 0
    lin_tag = [CryonirspTag.linearized()]

    for exp_time in dark_exp_times:
        num_dark += write_dark_frames_to_task(task, exp_time_ms=exp_time, tags=lin_tag)
    num_lamp = write_lamp_gain_frames_to_task(task, tags=lin_tag)
    num_solar = write_solar_gain_frames_to_task(task, tags=lin_tag)

    num_polcal += write_polcal_frames_to_task(
        task,
        num_modstates=num_modstates,
        num_map_scans=num_map_scans,
        tags=lin_tag,
        extra_headers=extra_headers,
    )
    num_obs += write_observe_frames_to_task(
        task,
        arm_id=arm_id,
        num_scan_steps=num_scan_steps,
        num_map_scans=num_map_scans,
        num_sub_repeats=num_sub_repeats,
        num_modstates=num_modstates,
        tags=lin_tag,
        change_translated_headers=change_translated_headers,
    )

    return num_dark, num_lamp, num_solar, num_polcal, num_obs


def make_non_linearized_test_frames(
    task,
    change_translated_headers: Callable[[fits.Header | None], fits.Header] = lambda x: x,
):
    arm_id = "SP"
    camera_readout_mode = "FastUpTheRamp"

    start_time = datetime(1946, 11, 20).isoformat("T")

    extra_tags = [
        CryonirspTag.input(),
        # All frames in a ramp have the same date-obs
        CryonirspTag.time_obs(str(start_time)),
    ]

    write_non_linearized_frames(
        task,
        start_time=start_time,
        arm_id=arm_id,
        camera_readout_mode=camera_readout_mode,
        tags=extra_tags,
        change_translated_headers=change_translated_headers,
    )


@pytest.fixture
def parse_linearized_task(tmp_path, recipe_run_id, assign_input_dataset_doc_to_task, mocker):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    with ParseL0CryonirspLinearizedData(
        recipe_run_id=recipe_run_id,
        workflow_name="parse_cryonirsp_input_data",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(param_path=tmp_path)
            assign_input_dataset_doc_to_task(task, param_class())
            yield task
        finally:
            task._purge()


@pytest.fixture
def parse_non_linearized_task(tmp_path, recipe_run_id, assign_input_dataset_doc_to_task, mocker):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    with ParseL0CryonirspRampData(
        recipe_run_id=recipe_run_id,
        workflow_name="parse_cryonirsp_input_data",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(param_path=tmp_path)
            assign_input_dataset_doc_to_task(task, param_class())
            yield task
        finally:
            task._purge()


def test_parse_cryonirsp_non_linearized_data(parse_non_linearized_task):
    """
    Given: A ParseCryonirspRampData task
    When: Calling the task instance
    Then: All tagged files exist and individual task tags are applied
    """

    task = parse_non_linearized_task
    make_non_linearized_test_frames(task)

    task()

    filepaths = list(task.read(tags=[CryonirspTag.input(), CryonirspTag.frame()]))
    cncndr_list = []
    for i, filepath in enumerate(filepaths):
        assert filepath.exists()
        hdul = fits.open(filepath)
        cncndr_list.append(hdul[0].header["CNCNDR"])
    assert len(filepaths) == 2
    assert sorted(cncndr_list) == [1, 2]
    assert task.constants._db_dict[CryonirspBudName.camera_readout_mode.value] == "FastUpTheRamp"
    assert task.constants._db_dict[CryonirspBudName.arm_id.value] == "SP"
    assert len(task.constants._db_dict[CryonirspBudName.time_obs_list]) == 1
    assert task.constants._db_dict[CryonirspBudName.wavelength.value] == 1082.7
    assert task.constants._db_dict[CryonirspBudName.time_obs_list][0] == datetime(
        1946, 11, 20
    ).isoformat("T")


def test_parse_cryonirsp_non_linearized_data_bad_filter_name(parse_non_linearized_task):
    """
    Given: A ParseCryonirspRampData task with a bad filter name in the headers
    When: Calling the task instance
    Then: The task fails with a ValueError exception
    """

    task = parse_non_linearized_task

    def insert_bad_filter_name_into_header(translated_header: fits.Header):
        translated_header["CNFILTNP"] = "BAD_FILTER_NAME"
        return translated_header

    make_non_linearized_test_frames(
        task, change_translated_headers=insert_bad_filter_name_into_header
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Unknown Optical Density Filter Name(s): bad_filter_names = {'BAD_FILTER_NAME'}"
        ),
    ):
        task()


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_data(parse_linearized_task, arm_id):
    """
    Given: A ParseCryonirspInputData task
    When: Calling the task instance
    Then: All tagged files exist and individual task tags are applied
    """

    task = parse_linearized_task

    lamp_exp_time = 10.0
    solar_exp_time = 5.0
    obs_exp_time = 6.0
    polcal_exp_time = 7.0
    unused_exp_time = 99.0
    dark_exp_times = [lamp_exp_time, solar_exp_time, obs_exp_time, polcal_exp_time, unused_exp_time]

    num_dark, num_lamp, num_solar, num_polcal, num_obs = make_linearized_test_frames(
        task,
        arm_id,
        dark_exp_times,
        num_modstates=8,
        num_scan_steps=3,
        num_map_scans=1,
        num_sub_repeats=1,
    )

    task()

    assert (
        len(list(task.read(tags=[CryonirspTag.linearized(), CryonirspTag.task_dark()]))) == num_dark
    )

    assert (
        len(
            list(
                parse_linearized_task.read(
                    tags=[CryonirspTag.linearized(), CryonirspTag.task_lamp_gain()]
                )
            )
        )
        == num_lamp
    )

    assert (
        len(
            list(
                parse_linearized_task.read(
                    tags=[CryonirspTag.linearized(), CryonirspTag.task_solar_gain()]
                )
            )
        )
        == num_solar
    )

    assert (
        len(
            list(
                parse_linearized_task.read(
                    tags=[CryonirspTag.linearized(), CryonirspTag.task_polcal()]
                )
            )
        )
        == num_polcal
    )

    assert (
        len(
            list(
                parse_linearized_task.read(
                    tags=[CryonirspTag.linearized(), CryonirspTag.task_observe()]
                )
            )
        )
        == num_obs
    )


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_data_mismatched_darks(parse_linearized_task, arm_id):
    """
    Given: A parse task with dark data that have mismatched exposure times
    When: Calling the Parse task
    Then: Raise the correct error
    """

    task = parse_linearized_task

    lamp_exp_time = 10.0
    solar_exp_time = 5.0
    obs_exp_time = 6.0
    polcal_exp_time = 7.0
    unused_exp_time = 99.0
    dark_exp_times = [
        lamp_exp_time + 1,
        solar_exp_time + 1,
        obs_exp_time + 1,
        polcal_exp_time + 1,
        unused_exp_time + 1,
    ]

    make_linearized_test_frames(
        task,
        arm_id,
        dark_exp_times,
        num_modstates=8,
        num_scan_steps=3,
        num_map_scans=2,
        num_sub_repeats=1,
    )

    with pytest.raises(
        ValueError, match="Exposure times required in the set of dark frames not found.*"
    ):
        task()


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_data_multi_num_scan_steps(parse_linearized_task, arm_id):
    """
    Given: A parse task with data that has muliple num_scan_step values
    When: Calling the Parse task
    Then: Raise the correct error
    """

    task = parse_linearized_task

    lamp_exp_time = 10.0
    solar_exp_time = 5.0
    obs_exp_time = 6.0
    polcal_exp_time = 7.0
    unused_exp_time = 99.0
    dark_exp_times = [lamp_exp_time, solar_exp_time, obs_exp_time, polcal_exp_time, unused_exp_time]

    def make_multi_num_scans(translated_header: fits.Header):
        translated_header["CNNUMSCN"] = translated_header["CNCURSCN"] % 3
        return translated_header

    make_linearized_test_frames(
        task,
        arm_id,
        dark_exp_times,
        num_modstates=8,
        num_scan_steps=4,
        num_map_scans=4,
        num_sub_repeats=2,
        change_translated_headers=make_multi_num_scans,
    )

    with pytest.raises(ValueError, match="Multiple NUM_SCAN_STEPS values found.*"):
        task()


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_incomplete_final_map(parse_linearized_task, arm_id):
    """
    Given: A parse task with data that has complete raster scans along with an incomplete raster scan
    When: Calling the Parse task
    Then: The correct number of scan steps and maps are found
    """

    task = parse_linearized_task

    lamp_exp_time = 10.0
    solar_exp_time = 5.0
    obs_exp_time = 6.0
    polcal_exp_time = 7.0
    unused_exp_time = 99.0
    dark_exp_times = [lamp_exp_time, solar_exp_time, obs_exp_time, polcal_exp_time, unused_exp_time]

    num_scan_steps = 5
    num_map_scans = 4
    num_modstates = 3
    num_sub_repeats = 2

    # Make all test frames except for last map scan
    make_linearized_test_frames(
        task,
        arm_id,
        dark_exp_times,
        num_modstates=num_modstates,
        num_scan_steps=num_scan_steps,
        num_map_scans=num_map_scans - 1,
        num_sub_repeats=num_sub_repeats,
    )

    # Make incomplete final map scan
    for map_scan in range(num_map_scans, num_map_scans + 1):  # Only make final map
        for mod_state in range(1, num_modstates + 1):
            for scan_step in range(1, num_scan_steps):  # One scan_step is missing in the last map
                for repeat in range(1, num_sub_repeats + 1):
                    frame_generator = ModulatedObserveHeaders(
                        num_modstates=num_modstates,
                        modstate=mod_state,
                        num_map_scans=num_map_scans,
                        map_scan=map_scan,
                        num_sub_repeats=num_sub_repeats,
                        sub_repeat_num=repeat,
                        array_shape=(1, 2, 2),
                        exp_time_ms=6.0,
                        num_scan_steps=num_scan_steps,
                        scan_step=scan_step,
                        num_meas=1,
                        arm_id=arm_id,
                    )

                    _write_frames_to_task(
                        task=task,
                        frame_generator=frame_generator,
                        extra_tags=[CryonirspTag.linearized()],
                    )

    task()
    assert task.constants._db_dict[CryonirspBudName.num_scan_steps.value] == num_scan_steps
    assert task.constants._db_dict[CryonirspBudName.num_map_scans.value] == num_map_scans - 1


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_incomplete_raster_scan(parse_linearized_task, arm_id):
    """
    Given: A parse task with data that has an incomplete raster scan
    When: Calling the parse task
    Then: The correct number of scan steps and maps are found
    """

    task = parse_linearized_task

    lamp_exp_time = 10.0
    solar_exp_time = 5.0
    obs_exp_time = 6.0
    polcal_exp_time = 7.0
    unused_exp_time = 99.0
    dark_exp_times = [lamp_exp_time, solar_exp_time, obs_exp_time, polcal_exp_time, unused_exp_time]

    num_scan_steps = 4
    num_map_scans = 1
    num_modstates = 2
    num_sub_repeats = 2

    def make_incomplete_raster_scan_headers(translated_header):
        translated_header["CNCURSCN"] = translated_header["CNCURSCN"] % (num_scan_steps - 1) + 1
        return translated_header

    make_linearized_test_frames(
        task,
        arm_id,
        dark_exp_times,
        num_modstates=num_modstates,
        num_scan_steps=num_scan_steps,
        num_map_scans=num_map_scans,
        num_sub_repeats=num_sub_repeats,
        change_translated_headers=make_incomplete_raster_scan_headers,
    )

    task()

    assert task.constants._db_dict[CryonirspBudName.num_scan_steps.value] == num_scan_steps - 1
    assert task.constants._db_dict[CryonirspBudName.num_map_scans.value] == num_map_scans


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_polcal_task_types(parse_linearized_task, arm_id):
    """
    Given: A Parse task with associated polcal files that include polcal gain and dark
    When: Tagging the task of each file
    Then: Polcal gain and darks are identified and tagged correctly
    """

    task = parse_linearized_task

    lamp_exp_time = 10.0
    solar_exp_time = 5.0
    obs_exp_time = 6.0
    polcal_exp_time = 7.0
    unused_exp_time = 99.0
    dark_exp_times = [lamp_exp_time, solar_exp_time, obs_exp_time, polcal_exp_time, unused_exp_time]

    num_scan_steps = 0
    num_map_scans = 7
    num_modstates = 8
    num_sub_repeats = 1

    polcal_dark_headers = {"PAC__008": "DarkShutter", "PAC__006": "clear", "PAC__004": "clear"}
    polcal_gain_headers = {"PAC__008": "FieldStopFoo", "PAC__006": "clear", "PAC__004": "clear"}
    polcal_data_headers = {
        "PAC__008": "FieldStopFoo",
        "PAC__006": "SiO2 SAR",
        "PAC__004": "Sapphire Polarizer",
    }

    extra_headers = [polcal_dark_headers, polcal_gain_headers, polcal_data_headers]

    for headers in extra_headers:
        make_linearized_test_frames(
            task,
            arm_id,
            dark_exp_times,
            num_modstates=num_modstates,
            num_scan_steps=num_scan_steps,
            num_map_scans=num_map_scans,
            num_sub_repeats=num_sub_repeats,
            extra_headers=headers,
        )

    task()

    assert (
        task.scratch.count_all(tags=[CryonirspTag.task("POLCAL_DARK")])
        == num_map_scans * num_modstates
    )
    assert (
        task.scratch.count_all(tags=[CryonirspTag.task("POLCAL_GAIN")])
        == num_map_scans * num_modstates
    )
    assert (
        task.scratch.count_all(tags=[CryonirspTag.task("POLCAL")])
        == (num_map_scans * num_modstates) * 3
    )


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_data_constants(parse_linearized_task, arm_id):
    """
    Given: A ParseCryonirspInputData task
    When: Calling the task instance
    Then: Constants are in the constants object as expected
    """

    task = parse_linearized_task

    lamp_exp_time = 10.0
    solar_exp_time = 5.0
    obs_exp_time = 6.0
    polcal_exp_time = 7.0
    unused_exp_time = 99.0
    dark_exp_times = [lamp_exp_time, solar_exp_time, obs_exp_time, polcal_exp_time, unused_exp_time]

    make_linearized_test_frames(
        task,
        arm_id,
        dark_exp_times,
        num_modstates=8,
        num_scan_steps=3,
        num_map_scans=2,
        num_sub_repeats=2,
    )

    task()

    assert task.constants._db_dict[CryonirspBudName.num_modstates.value] == 8
    assert task.constants._db_dict[CryonirspBudName.num_map_scans.value] == 2
    assert task.constants._db_dict[CryonirspBudName.num_scan_steps.value] == 3
    assert task.constants._db_dict[CryonirspBudName.modulator_spin_mode.value] == "Continuous"

    assert task.constants._db_dict["DARK_EXPOSURE_TIMES"] == [5.0, 6.0, 7.0, 10.0, 99.0]
    assert task.constants._db_dict["LAMP_GAIN_EXPOSURE_TIMES"] == [10.0]
    assert task.constants._db_dict["SOLAR_GAIN_EXPOSURE_TIMES"] == [5.0]
    assert task.constants._db_dict["POLCAL_EXPOSURE_TIMES"] == [0.01]
    assert task.constants._db_dict["OBSERVE_EXPOSURE_TIMES"] == [6.0]

    assert task.constants._db_dict["INSTRUMENT"] == "CRYO-NIRSP"
    assert task.constants._db_dict["AVERAGE_CADENCE"] == 10
    assert task.constants._db_dict["MAXIMUM_CADENCE"] == 10
    assert task.constants._db_dict["MINIMUM_CADENCE"] == 10
    assert task.constants._db_dict["VARIANCE_CADENCE"] == 0


def test_parse_cryonirsp_linearized_data_internal_scan_loops_as_map_scan_and_scan_step(
    parse_linearized_task,
):
    """
    Given: A parse task for an SP dataset where the internal scan loops are being used as a proxy for
           map scans and scan steps.
    When: Calling the task instance
    Then: All tagged files exist and individual task tags are applied. Specifically test that the
          internal scan loop parameters map to num_map_scans and num_scan_steps.
    """

    task = parse_linearized_task

    lamp_exp_time = 10.0
    solar_exp_time = 5.0
    obs_exp_time = 6.0
    polcal_exp_time = 7.0
    unused_exp_time = 99.0
    dark_exp_times = [lamp_exp_time, solar_exp_time, obs_exp_time, polcal_exp_time, unused_exp_time]

    num_map_scans = 1
    num_scan_steps = 6
    num_alt_maps = 2
    num_alt_scan_steps = 3

    def make_dual_scan_loop_headers(translated_header):
        translated_header[
            "CNP2DSS"
        ] = 0.0  # This triggers the parsing of the dual internal scan loops
        translated_header["CNP1DNSP"] = num_alt_scan_steps  # inner loop -- becomes num scan steps
        translated_header["CNP2DNSP"] = num_alt_maps  # outer loop -- becomes num map scans
        translated_header["CNP1DCUR"] = (translated_header["CNCURSCN"] - 1) % num_alt_scan_steps + 1
        translated_header["CNP2DCUR"] = (
            translated_header["CNCURSCN"] - 1
        ) // num_alt_scan_steps + 1
        return translated_header

    num_dark, num_lamp, num_solar, num_polcal, num_obs = make_linearized_test_frames(
        task,
        "SP",
        dark_exp_times,
        num_modstates=1,
        num_scan_steps=num_scan_steps,
        num_map_scans=num_map_scans,
        change_translated_headers=make_dual_scan_loop_headers,
    )

    task()

    assert task.constants._db_dict[CryonirspBudName.num_scan_steps.value] == num_alt_scan_steps
    assert task.constants._db_dict[CryonirspBudName.num_map_scans.value] == num_alt_maps


def test_optical_density_filter_names(parse_non_linearized_task):
    task = parse_non_linearized_task
    # List of filter attenuation parameters defined in CryonirspParameters:
    defined_filter_params = {
        item[-4:].upper()
        for item in dir(task.parameters)
        if item.startswith("_linearization_optical_density_filter_attenuation_")
    }
    # List of filters in the filter map:
    filter_map_params = {k for k in task.parameters.linearization_filter_attenuation_dict.keys()}
    # Make sure all filter parameters match the allowable list
    assert not defined_filter_params.symmetric_difference(ALLOWABLE_OPTICAL_DENSITY_FILTERS)
    # Make sure all filter map keys match the allowable list
    assert not filter_map_params.symmetric_difference(ALLOWABLE_OPTICAL_DENSITY_FILTERS)


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_not_polarimetric_obs(parse_linearized_task, arm_id):
    """
    Given: A ParseCryonirspInputData task
    When: Calling the task instance with non-polarimetric observe frames as input
    Then: PolarimetricCheckingUniqueBud has set the constants correctly
    """

    task = parse_linearized_task

    lin_tag = [CryonirspTag.linearized()]
    lamp_exp_time = 10.0
    solar_exp_time = 5.0
    obs_exp_time = 6.0
    polcal_exp_time = 7.0
    unused_exp_time = 99.0
    dark_exp_times = [lamp_exp_time, solar_exp_time, obs_exp_time, polcal_exp_time, unused_exp_time]

    num_steps = 3
    num_map_scans = 2
    num_sub_repeats = 2

    for exp_time in dark_exp_times:
        write_dark_frames_to_task(task, exp_time_ms=exp_time, tags=lin_tag)
    write_lamp_gain_frames_to_task(task, tags=lin_tag)
    write_solar_gain_frames_to_task(task, tags=lin_tag)

    write_polcal_frames_to_task(
        task, num_modstates=8, num_map_scans=num_map_scans, tags=lin_tag, extra_headers=dict()
    )
    write_observe_frames_to_task(
        task,
        arm_id=arm_id,
        num_scan_steps=num_steps,
        num_map_scans=num_map_scans,
        num_sub_repeats=num_sub_repeats,
        num_modstates=1,
        tags=lin_tag,
    )

    task()

    assert task.constants._db_dict[CryonirspBudName.num_modstates.value] == 1
    assert task.constants._db_dict[CryonirspBudName.modulator_spin_mode.value] == "Continuous"


@pytest.fixture
def dummy_fits_obj():
    @dataclass
    class DummyFitsObj:
        ip_task_type: str
        number_of_modulator_states: int
        modulator_spin_mode: str

    return DummyFitsObj


def test_polarimetric_checking_unique_bud(dummy_fits_obj):
    """
    Given: A PolarimetricCheckingUniqueBud
    When: Ingesting various polcal and observe frames
    Then: The Bud functions as expected
    """
    pol_frame1 = dummy_fits_obj(
        ip_task_type="POLCAL", number_of_modulator_states=8, modulator_spin_mode="Continuous"
    )
    pol_frame2 = dummy_fits_obj(
        ip_task_type="POLCAL", number_of_modulator_states=3, modulator_spin_mode="Continuous"
    )

    obs_frame1 = dummy_fits_obj(
        ip_task_type="OBSERVE", number_of_modulator_states=8, modulator_spin_mode="Continuous"
    )
    obs_frame2 = dummy_fits_obj(
        ip_task_type="OBSERVE", number_of_modulator_states=2, modulator_spin_mode="Continuous"
    )

    nonpol_obs_frame1 = dummy_fits_obj(
        ip_task_type="OBSERVE", number_of_modulator_states=1, modulator_spin_mode="Continuous"
    )
    nonpol_obs_frame2 = dummy_fits_obj(
        ip_task_type="OBSERVE", number_of_modulator_states=1, modulator_spin_mode="Bad"
    )

    # Test failures in `is_polarimetric
    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", obs_frame1)
    Bud.update("key2", obs_frame2)
    with pytest.raises(
        ValueError, match="Observe frames have more than one value of NUM_MODSTATES."
    ):
        Bud.is_polarimetric()

    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", nonpol_obs_frame1)
    Bud.update("key2", nonpol_obs_frame2)
    with pytest.raises(
        ValueError, match="Observe frames have more than one value of MODULATOR_SPIN_MODE."
    ):
        Bud.is_polarimetric()

    # Test correct operation of `is_polarimetric`
    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", nonpol_obs_frame1)
    assert not Bud.is_polarimetric()

    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", obs_frame1)
    assert Bud.is_polarimetric()

    # Test non-unique polcal values
    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", obs_frame1)
    Bud.update("key2", pol_frame1)
    Bud.update("key3", pol_frame2)
    with pytest.raises(ValueError, match="Polcal frames have more than one value of NUM_MODSTATES"):
        Bud.getter("key1")

    # Test for correct error if polcal and observe frames have different values for polarimetric data
    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", obs_frame1)
    Bud.update("key2", pol_frame2)
    with pytest.raises(ValueError, match="Polcal and Observe frames have different values for"):
        Bud.getter("key1")

    # Test that polcal and observe frames having different values doesn't matter for non-polarimetric datra
    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "modulator_spin_mode")
    Bud.update("key1", nonpol_obs_frame2)
    Bud.update("key2", pol_frame2)
    assert Bud.getter("key1") == "Bad"
