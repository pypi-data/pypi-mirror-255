"""
  Simple Wrapper on the Job class to handle EvnDisp Analysis
  for the Prod5b 2020 analysis from container
  https://forge.in2p3.fr/issues/42322
"""

__RCSID__ = "$Id$"

from CTADIRAC.Interfaces.API.CTAJob import CTAJob, MetadataDict


class EvnDispSingJob(CTAJob):
    def __init__(self) -> None:
        super().__init__(we_type="evndispsingjob", cpu_time=432000)
        self.setName("Evndisplay_CalibReco")
        self.setType("EvnDispProcessing")
        self.package = "evndisplay"
        self.version = "eventdisplay-cta-dl1-prod5.v06"
        self.container = True
        self.program_category = "calibimgreco"
        self.prog_name = "evndisp"
        self.configuration_id = 8
        self.output_data_level = 1
        self.base_path = "/vo.cta.in2p3.fr/MC/PROD5b/"
        self.ts_task_id = 0
        self.group_size = 1
        self.data_output_pattern = "./Data/*.simtel.DL1.root"

    def set_output_metadata(self, metadata: MetadataDict = {}) -> None:
        super().set_output_metadata(metadata)
        self.output_metadata["merged"] = 0

    def run_event_disp_software(self, i_step):
        ev_step = self.setExecutable(
            "./dirac_sing_evndisp.sh", logFile="EvnDisp_Log.txt"
        )
        ev_step["Value"]["name"] = f"Step{i_step}_EvnDisplay"
        ev_step["Value"]["descr_short"] = "Run EvnDisplay"

    def run_dedicated_software(self, i_step) -> None:
        self.run_event_disp_software(i_step)
