"""Workflows for trial runs (i.e., not Production)."""
from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialDatasetInventory
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TrialTeardown
from dkist_processing_core import ResourceQueue
from dkist_processing_core import Workflow

from dkist_processing_cryonirsp.tasks import BadPixelMapCalibration
from dkist_processing_cryonirsp.tasks import CIAssembleCryonirspMovie
from dkist_processing_cryonirsp.tasks import CIBeamBoundariesCalibration
from dkist_processing_cryonirsp.tasks import (
    CIInstrumentPolarizationCalibration,
)
from dkist_processing_cryonirsp.tasks import CIMakeCryonirspMovieFrames
from dkist_processing_cryonirsp.tasks import CIScienceCalibration
from dkist_processing_cryonirsp.tasks import CISolarGainCalibration
from dkist_processing_cryonirsp.tasks import CIWriteL1Frame
from dkist_processing_cryonirsp.tasks import DarkCalibration
from dkist_processing_cryonirsp.tasks import LampGainCalibration
from dkist_processing_cryonirsp.tasks import LinearityCorrection
from dkist_processing_cryonirsp.tasks import ParseL0CryonirspLinearizedData
from dkist_processing_cryonirsp.tasks import ParseL0CryonirspRampData
from dkist_processing_cryonirsp.tasks import SPAssembleCryonirspMovie
from dkist_processing_cryonirsp.tasks import SPBeamBoundariesCalibration
from dkist_processing_cryonirsp.tasks import SPGeometricCalibration
from dkist_processing_cryonirsp.tasks import (
    SPInstrumentPolarizationCalibration,
)
from dkist_processing_cryonirsp.tasks import SPMakeCryonirspMovieFrames
from dkist_processing_cryonirsp.tasks import SPScienceCalibration
from dkist_processing_cryonirsp.tasks import SPSolarGainCalibration
from dkist_processing_cryonirsp.tasks import SPWriteL1Frame
from dkist_processing_cryonirsp.tasks import TransferCryoTrialData

full_trial_ci_pipeline = Workflow(
    category="cryonirsp",
    input_data="l0",
    output_data="l1",
    detail="ci-full-trial",
    workflow_package=__package__,
)
full_trial_ci_pipeline.add_node(task=TransferL0Data, upstreams=None)
full_trial_ci_pipeline.add_node(task=ParseL0CryonirspRampData, upstreams=TransferL0Data)
full_trial_ci_pipeline.add_node(
    task=LinearityCorrection,
    resource_queue=ResourceQueue.HIGH_MEMORY,
    upstreams=ParseL0CryonirspRampData,
)
full_trial_ci_pipeline.add_node(task=ParseL0CryonirspLinearizedData, upstreams=LinearityCorrection)
full_trial_ci_pipeline.add_node(
    task=BadPixelMapCalibration, upstreams=ParseL0CryonirspLinearizedData
)
full_trial_ci_pipeline.add_node(task=CIBeamBoundariesCalibration, upstreams=BadPixelMapCalibration)
full_trial_ci_pipeline.add_node(task=DarkCalibration, upstreams=CIBeamBoundariesCalibration)
full_trial_ci_pipeline.add_node(task=LampGainCalibration, upstreams=DarkCalibration)
full_trial_ci_pipeline.add_node(task=CISolarGainCalibration, upstreams=LampGainCalibration)
full_trial_ci_pipeline.add_node(
    task=CIInstrumentPolarizationCalibration, upstreams=CISolarGainCalibration
)
full_trial_ci_pipeline.add_node(
    task=CIScienceCalibration, upstreams=CIInstrumentPolarizationCalibration
)
full_trial_ci_pipeline.add_node(task=CIWriteL1Frame, upstreams=CIScienceCalibration)
full_trial_ci_pipeline.add_node(task=CIMakeCryonirspMovieFrames, upstreams=CIWriteL1Frame)
full_trial_ci_pipeline.add_node(task=CIAssembleCryonirspMovie, upstreams=CIMakeCryonirspMovieFrames)
full_trial_ci_pipeline.add_node(
    task=CreateTrialDatasetInventory, upstreams=CIWriteL1Frame, pip_extras=["inventory"]
)
full_trial_ci_pipeline.add_node(task=CreateTrialAsdf, upstreams=CIWriteL1Frame, pip_extras=["asdf"])
full_trial_ci_pipeline.add_node(
    task=TransferCryoTrialData,
    upstreams=[CreateTrialDatasetInventory, CreateTrialAsdf, CIAssembleCryonirspMovie],
)
full_trial_ci_pipeline.add_node(task=TrialTeardown, upstreams=TransferCryoTrialData)

non_science_ci_pipeline = Workflow(
    category="cryonirsp",
    input_data="l0",
    output_data="l1",
    detail="ci-non-science-trial",
    workflow_package=__package__,
)
non_science_ci_pipeline.add_node(task=TransferL0Data, upstreams=None)
non_science_ci_pipeline.add_node(task=ParseL0CryonirspRampData, upstreams=TransferL0Data)
non_science_ci_pipeline.add_node(
    task=LinearityCorrection,
    resource_queue=ResourceQueue.HIGH_MEMORY,
    upstreams=ParseL0CryonirspRampData,
)
non_science_ci_pipeline.add_node(task=ParseL0CryonirspLinearizedData, upstreams=LinearityCorrection)
non_science_ci_pipeline.add_node(
    task=BadPixelMapCalibration, upstreams=ParseL0CryonirspLinearizedData
)
non_science_ci_pipeline.add_node(task=CIBeamBoundariesCalibration, upstreams=BadPixelMapCalibration)
non_science_ci_pipeline.add_node(task=DarkCalibration, upstreams=CIBeamBoundariesCalibration)
non_science_ci_pipeline.add_node(task=LampGainCalibration, upstreams=DarkCalibration)
non_science_ci_pipeline.add_node(task=CISolarGainCalibration, upstreams=LampGainCalibration)
non_science_ci_pipeline.add_node(
    task=CIInstrumentPolarizationCalibration, upstreams=CISolarGainCalibration
)
non_science_ci_pipeline.add_node(
    task=TransferCryoTrialData, upstreams=CIInstrumentPolarizationCalibration
)
non_science_ci_pipeline.add_node(task=TrialTeardown, upstreams=TransferCryoTrialData)

full_trial_sp_pipeline = Workflow(
    category="cryonirsp",
    input_data="l0",
    output_data="l1",
    detail="sp-full-trial",
    workflow_package=__package__,
)
full_trial_sp_pipeline.add_node(task=TransferL0Data, upstreams=None)
full_trial_sp_pipeline.add_node(task=ParseL0CryonirspRampData, upstreams=TransferL0Data)
full_trial_sp_pipeline.add_node(
    task=LinearityCorrection,
    resource_queue=ResourceQueue.HIGH_MEMORY,
    upstreams=ParseL0CryonirspRampData,
)
full_trial_sp_pipeline.add_node(task=ParseL0CryonirspLinearizedData, upstreams=LinearityCorrection)
full_trial_sp_pipeline.add_node(
    task=BadPixelMapCalibration, upstreams=ParseL0CryonirspLinearizedData
)
full_trial_sp_pipeline.add_node(task=SPBeamBoundariesCalibration, upstreams=BadPixelMapCalibration)
full_trial_sp_pipeline.add_node(task=DarkCalibration, upstreams=SPBeamBoundariesCalibration)
full_trial_sp_pipeline.add_node(task=LampGainCalibration, upstreams=DarkCalibration)
full_trial_sp_pipeline.add_node(task=SPGeometricCalibration, upstreams=LampGainCalibration)
full_trial_sp_pipeline.add_node(task=SPSolarGainCalibration, upstreams=SPGeometricCalibration)
full_trial_sp_pipeline.add_node(
    task=SPInstrumentPolarizationCalibration, upstreams=SPSolarGainCalibration
)
full_trial_sp_pipeline.add_node(
    task=SPScienceCalibration, upstreams=SPInstrumentPolarizationCalibration
)
full_trial_sp_pipeline.add_node(task=SPWriteL1Frame, upstreams=SPScienceCalibration)
full_trial_sp_pipeline.add_node(task=SPMakeCryonirspMovieFrames, upstreams=SPWriteL1Frame)
full_trial_sp_pipeline.add_node(task=SPAssembleCryonirspMovie, upstreams=SPMakeCryonirspMovieFrames)
full_trial_sp_pipeline.add_node(
    task=CreateTrialDatasetInventory, upstreams=SPWriteL1Frame, pip_extras=["inventory"]
)
full_trial_sp_pipeline.add_node(task=CreateTrialAsdf, upstreams=SPWriteL1Frame, pip_extras=["asdf"])
full_trial_sp_pipeline.add_node(
    task=TransferCryoTrialData,
    upstreams=[CreateTrialDatasetInventory, CreateTrialAsdf, SPAssembleCryonirspMovie],
)
full_trial_sp_pipeline.add_node(task=TrialTeardown, upstreams=TransferCryoTrialData)

non_science_sp_pipeline = Workflow(
    category="cryonirsp",
    input_data="l0",
    output_data="l1",
    detail="sp-non-science-trial",
    workflow_package=__package__,
)
non_science_sp_pipeline.add_node(task=TransferL0Data, upstreams=None)
non_science_sp_pipeline.add_node(task=ParseL0CryonirspRampData, upstreams=TransferL0Data)
non_science_sp_pipeline.add_node(
    task=LinearityCorrection,
    resource_queue=ResourceQueue.HIGH_MEMORY,
    upstreams=ParseL0CryonirspRampData,
)
non_science_sp_pipeline.add_node(task=ParseL0CryonirspLinearizedData, upstreams=LinearityCorrection)
non_science_sp_pipeline.add_node(
    task=BadPixelMapCalibration, upstreams=ParseL0CryonirspLinearizedData
)
non_science_sp_pipeline.add_node(task=SPBeamBoundariesCalibration, upstreams=BadPixelMapCalibration)
non_science_sp_pipeline.add_node(task=DarkCalibration, upstreams=SPBeamBoundariesCalibration)
non_science_sp_pipeline.add_node(task=LampGainCalibration, upstreams=DarkCalibration)
non_science_sp_pipeline.add_node(task=SPGeometricCalibration, upstreams=LampGainCalibration)
non_science_sp_pipeline.add_node(task=SPSolarGainCalibration, upstreams=SPGeometricCalibration)
non_science_sp_pipeline.add_node(
    task=SPInstrumentPolarizationCalibration, upstreams=SPSolarGainCalibration
)
non_science_sp_pipeline.add_node(
    task=TransferCryoTrialData, upstreams=SPInstrumentPolarizationCalibration
)
non_science_sp_pipeline.add_node(task=TrialTeardown, upstreams=TransferCryoTrialData)
