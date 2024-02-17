"""Test the linearity correction task."""
from datetime import datetime

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tests.conftest import FakeGQLClient

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.linearity_correction import LinearityCorrection
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import generate_fits_frame
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeadersValidNonLinearizedFrames


@pytest.fixture(scope="function")
def linearity_correction(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    init_cryonirsp_constants_db,
    arm_id,
    frames_in_ramp,
    filter_name,
):
    #                    time        y   x
    dataset_shape = (frames_in_ramp, 10, 10)
    #              z   y   x
    array_shape = (1, 10, 10)
    time_delta = 0.1
    start_time = datetime.now()
    constants_db = CryonirspConstantsDb(
        TIME_OBS_LIST=(str(start_time),),
        ARM_ID=arm_id,
        ROI_1_SIZE_X=array_shape[2],
        ROI_1_SIZE_Y=array_shape[1],
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with LinearityCorrection(
        recipe_run_id=recipe_run_id,
        workflow_name="linearity_correction",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(param_path=tmp_path)
            assign_input_dataset_doc_to_task(task, param_class())
            ds = CryonirspHeadersValidNonLinearizedFrames(
                arm_id=arm_id,
                camera_readout_mode="FastUpTheRamp",
                dataset_shape=dataset_shape,
                array_shape=array_shape,
                time_delta=time_delta,
                roi_x_origin=0,
                roi_y_origin=0,
                roi_x_size=array_shape[2],
                roi_y_size=array_shape[1],
                date_obs=start_time.isoformat("T"),
                exposure_time=time_delta,
            )
            # Initial header creation...
            header_generator = (
                spec122_validator.validate_and_translate_to_214_l0(
                    d.header(), return_type=fits.HDUList
                )[0].header
                for d in ds
            )
            # Patch the headers for non-linearized Cryo data...
            header_list = []
            exp_time = 0.0
            counter = 0
            for header in header_generator:
                # Set the integrated exposure time for this NDR
                # This is a range from 0 to 90 in 10 steps
                header["XPOSURE"] = 100 * counter * time_delta
                # Set the current frame in ramp, 1-based
                header["CNCNDR"] = counter + 1
                header["CNFILTNP"] = filter_name
                header_list.append(header)
                counter += 1
            # Step on the old one with the new one
            header_generator = (header for header in header_list)
            # Iterate through the headers and create the frames...
            for _ in header_list:
                hdul = generate_fits_frame(header_generator=header_generator, shape=array_shape)
                # Now tweak the data...
                for hdu in hdul:
                    header = hdu.header
                    exp_time = header["XPOSURE"]
                    # Create a simple perfectly linear ramp
                    hdu.data.fill(exp_time)
                    task.write(
                        data=hdul,
                        tags=[
                            CryonirspTag.input(),
                            CryonirspTag.frame(),
                            CryonirspTag.curr_frame_in_ramp(header["CNCNDR"]),
                            # All frames in a ramp have the same date-obs
                            CryonirspTag.time_obs(str(start_time)),
                            Tag.readout_exp_time(exp_time),
                        ],
                        encoder=fits_hdulist_encoder,
                    )
            task.constants._update({CryonirspBudName.camera_readout_mode.value: "FastUpTheRamp"})
            yield task, filter_name
        finally:
            task._purge()


@pytest.mark.parametrize(
    "filter_name",
    [pytest.param("G358", id="G358"), pytest.param("OPEN", id="OPEN")],
)
@pytest.mark.parametrize(
    "frames_in_ramp",
    [pytest.param(10, id="Full ramp"), pytest.param(1, id="Bad ramp")],
)
@pytest.mark.parametrize(
    "arm_id",
    [pytest.param("CI", id="CI"), pytest.param("SP", id="SP")],
)
@pytest.mark.parametrize(
    "num_chunks",
    [pytest.param(1, id="1 chunk"), pytest.param(2, id="2 chunks")],
)
def test_linearity_correction(
    linearity_correction, mocker, arm_id, frames_in_ramp, num_chunks, filter_name
):
    """
    Given: A LinearityCorrection task
    When: Calling the task instance with known input data
    Then: The non-linearized frames are linearized and produce the correct results.
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    if num_chunks == 2:
        mocker.patch(
            "dkist_processing_cryonirsp.tasks.linearity_correction.LinearityCorrection._compute_linear_chunk_size",
            new=lambda self, frame_size, num_frames_in_ramp: frame_size // 2,
        )
    # Given
    task, filter_name = linearity_correction
    # When
    task()
    # Then
    tags = [
        CryonirspTag.linearized(),
        CryonirspTag.frame(),
    ]
    # We used a perfect linear ramp from 0 to 90, where the ramp value is equal to the exposure time in ms
    # The algorithm normalizes the linearized frame by the exposure time in seconds, so the expected value is:
    # 90 / (90 / 1000) = 1000 / attenuation, where attenuation is the multiplicative attenuation due to the
    # filter in use
    attenuation = 10 ** (task.parameters.linearization_filter_attenuation_dict[filter_name])
    expected_data = np.ones((10, 10)) * 1000.0 / attenuation
    files_found = list(task.read(tags=tags))
    if frames_in_ramp > 1:
        assert len(files_found) == 1
        hdul = fits.open(files_found[0])
        data = hdul[0].data
        assert np.allclose(data, expected_data)
    else:
        assert len(files_found) == 0
