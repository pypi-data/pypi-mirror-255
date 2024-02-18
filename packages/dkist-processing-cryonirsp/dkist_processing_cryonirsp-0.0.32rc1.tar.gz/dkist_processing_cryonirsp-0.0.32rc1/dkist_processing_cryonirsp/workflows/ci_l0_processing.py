"""Cryo CI raw data processing workflow."""
from dkist_processing_common.tasks import AddDatasetReceiptAccount
from dkist_processing_common.tasks import PublishCatalogAndQualityMessages
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import SubmitQuality
from dkist_processing_common.tasks import Teardown
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferL1Data
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
from dkist_processing_cryonirsp.tasks import CryonirspL0QualityMetrics
from dkist_processing_cryonirsp.tasks import CryonirspL1QualityMetrics
from dkist_processing_cryonirsp.tasks import DarkCalibration
from dkist_processing_cryonirsp.tasks import LampGainCalibration
from dkist_processing_cryonirsp.tasks import LinearityCorrection
from dkist_processing_cryonirsp.tasks import ParseL0CryonirspLinearizedData
from dkist_processing_cryonirsp.tasks import ParseL0CryonirspRampData

l0_pipeline = Workflow(
    category="cryonirsp",
    input_data="l0",
    output_data="l1",
    detail="ci",
    workflow_package=__package__,
)
l0_pipeline.add_node(task=TransferL0Data, upstreams=None)
l0_pipeline.add_node(task=ParseL0CryonirspRampData, upstreams=TransferL0Data)
l0_pipeline.add_node(
    task=LinearityCorrection,
    resource_queue=ResourceQueue.HIGH_MEMORY,
    upstreams=ParseL0CryonirspRampData,
)
l0_pipeline.add_node(task=ParseL0CryonirspLinearizedData, upstreams=LinearityCorrection)
l0_pipeline.add_node(task=CryonirspL0QualityMetrics, upstreams=ParseL0CryonirspLinearizedData)
l0_pipeline.add_node(task=BadPixelMapCalibration, upstreams=ParseL0CryonirspLinearizedData)
l0_pipeline.add_node(task=CIBeamBoundariesCalibration, upstreams=BadPixelMapCalibration)
l0_pipeline.add_node(task=DarkCalibration, upstreams=CIBeamBoundariesCalibration)
l0_pipeline.add_node(task=LampGainCalibration, upstreams=DarkCalibration)
l0_pipeline.add_node(task=CISolarGainCalibration, upstreams=LampGainCalibration)
l0_pipeline.add_node(task=CIInstrumentPolarizationCalibration, upstreams=CISolarGainCalibration)
l0_pipeline.add_node(task=CIScienceCalibration, upstreams=CIInstrumentPolarizationCalibration)
l0_pipeline.add_node(task=CIWriteL1Frame, upstreams=CIScienceCalibration)
l0_pipeline.add_node(task=QualityL1Metrics, upstreams=CIWriteL1Frame)
l0_pipeline.add_node(task=CryonirspL1QualityMetrics, upstreams=CIWriteL1Frame)
l0_pipeline.add_node(
    task=SubmitQuality,
    upstreams=[CryonirspL0QualityMetrics, QualityL1Metrics, CryonirspL1QualityMetrics],
)
l0_pipeline.add_node(task=CIMakeCryonirspMovieFrames, upstreams=CIWriteL1Frame)
l0_pipeline.add_node(task=CIAssembleCryonirspMovie, upstreams=CIMakeCryonirspMovieFrames)
l0_pipeline.add_node(
    task=AddDatasetReceiptAccount, upstreams=[CIAssembleCryonirspMovie, SubmitQuality]
)
l0_pipeline.add_node(task=TransferL1Data, upstreams=AddDatasetReceiptAccount)
l0_pipeline.add_node(
    task=PublishCatalogAndQualityMessages,
    upstreams=TransferL1Data,
)
l0_pipeline.add_node(task=Teardown, upstreams=PublishCatalogAndQualityMessages)
