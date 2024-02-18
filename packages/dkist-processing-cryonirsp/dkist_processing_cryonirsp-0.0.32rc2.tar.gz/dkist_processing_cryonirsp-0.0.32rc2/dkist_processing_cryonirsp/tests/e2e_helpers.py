import shutil
from pathlib import Path

import asdf
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_service_configuration import logger

from dkist_processing_cryonirsp.models.tags import CryonirspTag


class SaveTaskTags(WorkflowTaskBase):
    @property
    def task_str(self) -> str:
        return "TASK"

    @property
    def relative_save_file(self) -> str:
        return "default_sav.asdf"

    def run(self):
        file_tag_dict = dict()
        path_list = self.read(tags=[CryonirspTag.task(self.task_str), CryonirspTag.intermediate()])
        save_dir = self.scratch.workflow_base_path / Path(self.relative_save_file).stem
        save_dir.mkdir(exist_ok=True)
        for p in path_list:
            copied_path = shutil.copy(str(p), save_dir)
            tags = self.tags(p)
            file_tag_dict[copied_path] = tags

        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        tree = {"file_tag_dict": file_tag_dict}
        af = asdf.AsdfFile(tree)
        af.write_to(full_save_file)
        logger.info(f"Saved {self.task_str} to {full_save_file}")


class LoadTaskTags(WorkflowTaskBase):
    @property
    def relative_save_file(self) -> str:
        return "default_sav.asdf"

    def run(self):
        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        with asdf.open(full_save_file) as af:
            for f, t in af.tree["file_tag_dict"].items():
                self.tag(path=f, tags=t)
        logger.info(f"Loaded database entries from {full_save_file}")


class SaveGeometricCal(WorkflowTaskBase):
    def run(self) -> None:
        relative_save_file = "geometric_cal.asdf"
        file_tag_dict = dict()
        path_list = list(
            self.read(tags=[CryonirspTag.task_geometric_angle(), CryonirspTag.intermediate()])
        )
        path_list += list(
            self.read(tags=[CryonirspTag.task_geometric_offset(), CryonirspTag.intermediate()])
        )
        path_list += list(
            self.read(
                tags=[CryonirspTag.task_geometric_sepectral_shifts(), CryonirspTag.intermediate()]
            )
        )
        save_dir = self.scratch.workflow_base_path / Path(relative_save_file).stem
        save_dir.mkdir(exist_ok=True)
        for p in path_list:
            copied_path = shutil.copy(str(p), save_dir)
            tags = self.tags(p)
            file_tag_dict[copied_path] = tags

        full_save_file = self.scratch.workflow_base_path / relative_save_file
        tree = {"file_tag_dict": file_tag_dict}
        af = asdf.AsdfFile(tree)
        af.write_to(full_save_file)
        logger.info(f"Saved Geometric Calibration to {full_save_file}")


class LoadGeometricCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "geometric_cal.asdf"


class SaveDarkCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.dark.value

    @property
    def relative_save_file(self) -> str:
        return "dark_cal.asdf"


class LoadDarkCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "dark_cal.asdf"


class SaveLampCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.lamp_gain.value

    @property
    def relative_save_file(self) -> str:
        return "lamp_cal.asdf"


class LoadLampCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "lamp_cal.asdf"


class SaveSolarCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.solar_gain.value

    @property
    def relative_save_file(self) -> str:
        return "solar_cal.asdf"


class LoadSolarCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "solar_cal.asdf"


class SaveInstPolCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.demodulation_matrices.value

    @property
    def relative_save_file(self) -> str:
        return "inst_pol_cal.asdf"


class LoadInstPolCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "inst_pol_cal.asdf"
