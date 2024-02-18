from copy import deepcopy
from CTADIRAC.Interfaces.API.CTAJob import CTAJob, MetadataDict


class CtapipeApplyModelsJob(CTAJob):
    """Job extension class for ctapipe apply models"""

    def __init__(self) -> None:
        super().__init__(we_type="ctapipeapplymodels")
        self.setName("ctapipe_apply-models")
        self.setType("ApplyModel")
        self.prog_name = "ctapipe-apply-models"
        self.data_level = 2

    def download_model_by_query(self, i_step) -> None:
        model_metadata: MetadataDict = deepcopy(self.output_metadata)
        model_metadata.update(self.output_file_metadata)
        model_metadata.pop("particle")
        if "split" in model_metadata:
            model_metadata.pop("split")
        if "energy_model.pkl" in self.options:
            model_metadata["analysis_prog"] = "ctapipe-train-energy-regressor"
            argument_list = []
            for key, value in model_metadata.items():
                argument_list.append(key + "=" + str(value))
            get_step0 = self.setExecutable(
                "cta-prod-get-file-by-query",
                arguments=f"{' '.join(argument_list)}",
                logFile="DownloadEnergyModel_Log.txt",
            )
            get_step0["Value"]["name"] = f"Step{i_step}_DownloadEnergyModel"
            get_step0["Value"]["descr_short"] = "Download Energy Model"
            i_step += 1

        if "classifier_model.pkl" in self.options:
            model_metadata["analysis_prog"] = "ctapipe-train-particle-classifier"
            argument_list = []
            for key, value in model_metadata.items():
                argument_list.append(key + "=" + str(value))
            get_step1 = self.setExecutable(
                "cta-prod-get-file-by-query",
                arguments=f"{' '.join(argument_list)}",
                logFile="DownloadClassifierModel_Log.txt",
            )
            get_step1["Value"]["name"] = f"Step{i_step}_DownloadClassifierModel"
            get_step1["Value"]["descr_short"] = "Download Classifier Model"

    def run_dedicated_software(self, i_step) -> None:
        self.download_model_by_query(i_step)
