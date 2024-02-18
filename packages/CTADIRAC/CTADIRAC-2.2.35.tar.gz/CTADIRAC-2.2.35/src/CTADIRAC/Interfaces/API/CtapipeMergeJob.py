from CTADIRAC.Interfaces.API.CTAJob import CTAJob, MetadataDict


class CtapipeMergeJob(CTAJob):
    """Job extension class for ctapipe merging"""

    def __init__(self) -> None:
        super().__init__(we_type="merging")
        self.setType("Merging")
        self.setName("ctapipe_merge")
        self.prog_name = "ctapipe-merge"
        self.merged = 0
        self.data_level = 2
        self.output_extension = "merged.DL2.h5"

    def set_output_metadata(self, metadata: MetadataDict = {}) -> None:
        super().set_output_metadata(metadata)
        """For each stage of merging we add +1"""
        try:
            merged = metadata["merged"]["="]
        except (KeyError, TypeError):
            merged = metadata["merged"]
        self.output_metadata["merged"] = merged + 1

    def run_merge(self, i_step):
        merge_step = self.setExecutable(
            "./dirac_ctapipe-merge_wrapper",
            arguments=f"--out_ext {self.output_extension} {self.options}",
            logFile="ctapipe_merge_Log.txt",
        )
        merge_step["Value"]["name"] = f"Step{i_step}_ctapipe_merge"
        merge_step["Value"]["descr_short"] = "Run ctapipe merge"

    def run_dedicated_software(self, i_step) -> None:
        self.run_merge(i_step)
