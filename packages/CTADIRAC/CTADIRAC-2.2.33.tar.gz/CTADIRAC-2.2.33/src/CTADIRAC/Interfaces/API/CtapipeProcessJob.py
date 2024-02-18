import json
from CTADIRAC.Interfaces.API.CTAJob import CTAJob


class CtapipeProcessJob(CTAJob):
    """Job extension class for ctapipe stage1 modeling processing"""

    def __init__(self) -> None:
        super().__init__(we_type="ctapipeprocessing")
        self.setName("ctapipe_process")
        self.setType("DL0_Reprocessing")
        self.data_level = 2

    def register_log(self, i_step, meta_data_json) -> None:
        log_file_pattern = "./Data/*.log_and_prov.tgz"
        file_meta_data = {}
        file_meta_data_json = json.dumps(file_meta_data)
        output_data_type = self.output_log_type
        log_step = self.setExecutable(
            "cta-prod-managedata",
            arguments=f"'{meta_data_json}' '{file_meta_data_json}' {self.base_path} "
            f"'{log_file_pattern}' {self.package} {self.program_category} '{self.catalogs}' {output_data_type}",
            logFile="LogManagement_Log.txt",
        )
        log_step["Value"]["name"] = f"Step{i_step}_LogManagement"
        log_step["Value"]["descr_short"] = "Save log to SE and register them in DFC"

    def run_ctapipe_process(self, i_step) -> None:
        proc_step = self.setExecutable(
            "./dirac_ctapipe-process_wrapper",
            arguments=f"--out_ext {self.output_extension} {self.options}",
            logFile="ctapipe_process_Log.txt",
        )
        proc_step["Value"]["name"] = f"Step{i_step}_ctapipe_process"
        proc_step["Value"]["descr_short"] = "Run ctapipe process"

    def run_dedicated_software(self, i_step) -> None:
        self.run_ctapipe_process(i_step)
