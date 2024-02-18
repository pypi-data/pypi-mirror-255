#!/usr/bin/env python
"""
Launch a transformation from CWL workflow descriptions

Usage:
    cta-prod-submit-from-cwl-workflow <name of the Transformation> <path of the directory containing CWL files> <CWL file with workflow description> <YAML file with workflow inputs>

Examples:
    cta-prod-submit-from-cwl-workflow Transformation_test ../CWL ../CWL/simulation-run.cwl ../CWL/simulation-run.yml
"""

__RCSID__ = "$Id$"

import re
import json
import itertools
import DIRAC
from DIRAC.Core.Base.Script import Script
from CTADIRAC.Interfaces.API.MCPipeNSBJob import MCPipeNSBJob
from DIRAC.TransformationSystem.Client.Transformation import Transformation
from CTADIRAC.ProductionSystem.CWL.CWLWorkflow import Workflow


def submit_transformation_from_workflow(transfo, transfo_name, cwl_file, yml_file):
    """Build MC Simulation Transformation"""

    # Build Transformation
    transfo.Name = "TransformationTest"
    transfo.setTransformationName(transfo_name)  # this must be unique
    transfo.setType("MCSimulation")
    transfo.setDescription("Prod6 MC Pipe TS")
    transfo.setLongDescription("Prod6 simulation pipeline")  # mandatory

    # Build Workflow
    wf = Workflow()
    wf.load(cwl_file, yml_file)
    cmd_list = wf.run_workflow(yml_file)
    print(wf.inputs)

    # Build Job
    job = MCPipeNSBJob()
    job.setType("MCSimulation")
    job.setOutputSandbox(["*Log.txt"])

    # pre-step
    i_step = 1
    job.package = "corsika_simtelarray"
    job.version = "2022-08-03"
    job.compiler = "gcc83_matchcpu"

    sw_step = job.setExecutable(
            "cta-prod-setup-software",
            arguments="-p %s -v %s -a simulations -g %s"
            % (job.package, job.version, job.compiler),
            logFile="SetupSoftware_Log.txt",
        )
    sw_step["Value"]["name"] = "Step%i_SetupSoftware" % i_step
    sw_step["Value"]["descr_short"] = "Setup software"
    i_step += 1

    # Build steps
    for cmd in cmd_list:
        if "dirac_prod_run" in cmd:
            # dirac_prod_run is not a command, add ./ for executable
            cmd = "./" + cmd
            # Replace static run number with dynamic run number to run with DIRAC
            cmd = re.sub("--run [0-9]+", f"--run {job.run_number}", cmd)
            print(cmd)

        # Run workflow
        step = job.setExecutable(
            str(cmd.split(" ", 1)[0]),
            arguments=str(cmd.split(" ", 1)[1]),
            logFile="Step%i_Log.txt" % i_step,
        )
        step["Value"]["name"] = "Step%i" % i_step
        step["Value"]["descr_short"] = str(cmd.split(" ", 1)[0])
        i_step += 1

    '''site = cmd.split(" ", 1)[1].split(" ")[4]
    particle = cmd.split(" ", 1)[1].split(" ")[5]
    pointing_dir = cmd.split(" ", 1)[1].split(" ")[6]
    zenith_angle = cmd.split(" ", 1)[1].split(" ")[7]'''

    job.set_site(wf.inputs["site"])
    job.set_particle(wf.inputs["particle"])
    job.set_pointing_dir(wf.inputs["pointing_dir"])
    job.zenith_angle = wf.inputs["zenith_angle"]
    job.configuration_id = 15
    job.MCCampaign = "Prod6TestLA"
    #DIRAC.exit(0)


    # post-step: define meta data, upload file on SE and register in catalogs
    job.catalogs = json.dumps(["DIRACFileCatalog", "TSCatalog"])
    job.program_category = "tel_sim"

    job.set_output_metadata()
    md_json = json.dumps(job.output_metadata)
    job.set_moon(["dark"])

    keys = job.output_file_metadata.keys()

    for element in itertools.product(*job.output_file_metadata.values()):
        i_substep = 1
        combination = dict(zip(keys, element))

        # build file meta data
        file_meta_data = {
            "runNumber": job.run_number,
        }
        for key, value in combination.items():
            file_meta_data[key] = value

        file_md_json = json.dumps(file_meta_data)

    data_output_pattern = f"Data/*dark*.simtel.zst"
    dm_step = job.setExecutable(
        "cta-prod-managedata",
        arguments="'%s' '%s' %s '%s' %s %s '%s' Data"
        % (
            md_json,
            file_md_json,
            job.base_path,
            data_output_pattern,
            job.package,
            job.program_category,
            job.catalogs,
        ),
            logFile="DataManagement_dark_Log.txt",
        )
    dm_step["Value"]["name"] = f"Step{i_step}_DataManagement"
    dm_step["Value"][
            "descr_short"
    ] = "Save data files to SE and register them in DFC"
    i_step += 1

    job.setExecutionEnv({"NSHOW": "10"})

    # Submit Transformation
    #print(job.workflow.toXML())
    DIRAC.exit(0)
    #transfo.setBody(MCJob.workflow.toXML())
    #result = transfo.addTransformation()  # transformation is created here
    #if not result["OK"]:
    #    return result
    #transfo.setStatus("Active")
    #transfo.setAgentType("Automatic")
    #return result


def main():
    Script.parseCommandLine()
    argss = Script.getPositionalArgs()
    if len(argss) != 4:
        Script.showHelp()
    transfo_name = argss[0]
    config_dir = argss[1]
    cwl_file = argss[2]
    yml_file = argss[3]
    if config_dir not in cwl_file:
        Script.showHelp()
    transfo = Transformation()
    submit_transformation_from_workflow(
        transfo, transfo_name, cwl_file, yml_file
    )
    '''try:
        if not result["OK"]:
            DIRAC.gLogger.error(result["Message"])
            DIRAC.exit(-1)
        else:
            DIRAC.gLogger.notice("Done")
    except Exception:
        DIRAC.gLogger.exception()
        DIRAC.exit(-1)'''


if __name__ == "__main__":
    main()
