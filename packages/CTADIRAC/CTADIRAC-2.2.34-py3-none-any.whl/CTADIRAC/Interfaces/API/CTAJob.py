# Job.py
import json
from collections import OrderedDict
from typing import Literal

from DIRAC.Interfaces.API.Job import Job


class MetadataDict(OrderedDict):
    MCCampaign: str
    array_layout: str
    catalogs: str
    configuration_id: str
    data_level: int
    group_size: int
    merged: int
    nsb: list
    options: str
    output_extension: str
    outputType: Literal["Data", "Log", "Model"]
    particle: str
    phiP: int
    prog_name: str
    site: str
    sct: bool
    thetaP: int
    type: str
    version: str

    predefined_keys: list[str] = [
        "MCCampaign",
        "array_layout",
        "catalogs",
        "configuration_id",
        "data_level",
        "group_size",
        "merged",
        "nsb",
        "options",
        "output_extension",
        "outputType",
        "particle",
        "phiP",
        "prog_name",
        "sct",
        "site",
        "thetaP",
        "type",
        "version",
    ]

    def __setitem__(self, key, value) -> None:
        if key not in self.predefined_keys and "_prog" not in key:
            raise KeyError(f"Key '{key}' is not allowed in MetadataDict")
        super().__setitem__(key, value)


class CTAJob(Job):
    """Base Job class for CTA DL1 -> DL2 jobs"""

    def __init__(self, we_type: str, cpu_time: float = 432000) -> None:
        Job.__init__(self)
        self.we_type: str = we_type
        self.setOutputSandbox(["*Log.txt"])
        self.setCPUTime(cpu_time)
        self.setName("ctapipe")
        self.input_limit = None
        self.output_metadata = MetadataDict()
        self.output_file_metadata = MetadataDict()
        self.catalogs: str = json.dumps(["DIRACFileCatalog", "TSCatalog"])
        self.prog_name = "ctapipe-process"
        self.program_category = "analysis"
        self.software_category = "stage1"
        self.package = "ctapipe"
        self.version = "v0.10.0"
        self.compiler = "gcc48_default"
        self.configuration_id = 1
        self.data_level = 1
        self.MCCampaign = "ProdTest"
        self.options = ""
        self.data_output_pattern = "./Data/*.h5"
        self.output_type = "Data"
        self.output_data_type = "Data"
        self.output_log_type = "Log"

    def set_output_metadata(self, metadata: MetadataDict = {}) -> None:
        """Set output metadata
        Parameters:
        metadata -- metadata dictionary from telescope simulation
        """
        self.output_metadata["array_layout"] = metadata["array_layout"]
        self.output_metadata["site"] = metadata["site"]
        try:
            self.output_metadata["particle"] = metadata["particle"]
        except (KeyError, TypeError):
            pass
        try:
            phi_p = metadata["phiP"]["="]
        except (KeyError, TypeError):
            phi_p = metadata["phiP"]
        self.output_metadata["phiP"] = phi_p
        try:
            theta_p = metadata["thetaP"]["="]
        except (KeyError, TypeError):
            theta_p = metadata["thetaP"]
        self.output_metadata["thetaP"] = theta_p
        if metadata.get("sct"):
            self.output_metadata["sct"] = metadata["sct"]
        else:
            self.output_metadata["sct"] = "False"
        self.output_metadata[self.program_category + "_prog"] = self.prog_name
        self.output_metadata[self.program_category + "_prog_version"] = self.version
        self.output_metadata["data_level"] = self.data_level
        self.output_metadata["outputType"] = self.output_type
        self.output_metadata["configuration_id"] = self.configuration_id
        self.output_metadata["MCCampaign"] = self.MCCampaign

    def init_debug_step(self, i_step) -> None:
        ls_step = self.setExecutable("/bin/ls -alhtr", logFile="LS_Init_Log.txt")
        ls_step["Value"]["name"] = f"Step{i_step}_LS_Init"
        ls_step["Value"]["descr_short"] = "list files in working directory"

    def software_step(self, i_step) -> None:
        sw_step = self.setExecutable(
            "cta-prod-setup-software",
            arguments=f"-p {self.package} -v {self.version} -a {self.software_category} -g {self.compiler}",
            logFile="SetupSoftware_Log.txt",
        )
        sw_step["Value"]["name"] = f"Step{i_step}_SetupSoftware"
        sw_step["Value"]["descr_short"] = "Setup software"

    def run_dedicated_software(self, i_step) -> None:
        """To be redifined in subclasses"""
        pass

    def set_metadata_and_register_data(self, i_step) -> str:
        meta_data_json: str = json.dumps(self.output_metadata)
        file_meta_data_json: str = json.dumps(self.output_file_metadata)
        output_data_type = self.output_data_type
        dm_step = self.setExecutable(
            "cta-prod-managedata",
            arguments=f"'{meta_data_json}' '{file_meta_data_json}' {self.base_path} "
            f"'{self.data_output_pattern}' {self.package} {self.program_category} '{self.catalogs}' {output_data_type}",
            logFile="DataManagement_Log.txt",
        )
        dm_step["Value"]["name"] = f"Step{i_step}_DataManagement"
        dm_step["Value"][
            "descr_short"
        ] = "Save data files to SE and register them in DFC"
        return meta_data_json

    def mid_debug(self, i_step) -> None:
        ls_step = self.setExecutable("/bin/ls -Ralhtr", logFile="LS_End_Log.txt")
        ls_step["Value"]["name"] = f"Step{i_step}_LS_End"
        ls_step["Value"][
            "descr_short"
        ] = "list files in working directory and sub-directory"

    def register_log(self, i_step, meta_data_json) -> None:
        """To be redifined in subclasses"""
        pass

    def failover_step(self, i_step):
        failover_step = self.setExecutable(
            "/bin/ls -l", modulesList=["Script", "FailoverRequest"]
        )
        failover_step["Value"]["name"] = f"Step{i_step}_Failover"
        failover_step["Value"]["descr_short"] = "Tag files as unused if job failed"

    def end_debug_step(self, i_step):
        ls_step = self.setExecutable("/bin/ls -Ralhtr", logFile="LS_End_Log.txt")
        ls_step["Value"]["name"] = f"Step{i_step}_LSHOME_End"
        ls_step["Value"]["descr_short"] = "list files in Home directory"

    def set_executable_sequence(self, debug=False) -> None:
        i_step = 0
        if debug:
            self.init_debug_step(i_step)
            i_step += 1

        self.software_step(i_step)
        i_step += 1

        self.run_dedicated_software(i_step)
        i_step += 1

        if debug:
            self.mid_debug(i_step)
            i_step += 1

        meta_data_json: str = self.set_metadata_and_register_data(i_step)
        i_step += 1

        self.register_log(i_step, meta_data_json)
        i_step += 1

        self.failover_step(i_step)
        i_step += 1

        if debug:
            self.end_debug_step(i_step)
            i_step += 1
