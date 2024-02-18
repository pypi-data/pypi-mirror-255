#!/usr/bin/env python
""" Data management script for production
    create DFC MetaData structure put and register files in DFC
    should work for corsika, simtel and EventDisplay output
"""

__RCSID__ = "$Id$"

# generic imports
import os
import glob
import json

# DIRAC imports
import DIRAC
from DIRAC.Core.Base.Script import Script

Script.parseCommandLine()

# Specific DIRAC imports
from DIRAC.DataManagementSystem.Client.DataManager import DataManager


def main():
    """simple wrapper to put and register all production files

    Keyword arguments:
    args -- a list of arguments in order []
    """
    args = Script.getPositionalArgs()
    #lfn = "/vo.cta.in2p3.fr/MC/PROD6/Paranal/gamma-diffuse/sim_telarray/3788/Data/003xxx/gamma_20deg_0deg_run003760___cta-prod6-paranal-2147m-Paranal-divergent-div0.0043-dark_cone10.simtel.zst"
    lfn = "/vo.cta.in2p3.fr/user/a/arrabito/test_file.txt"
    dm = DataManager()
    res = dm.getReplicas(lfn)
    print(res)
    res = dm.getReplicasForJobs(lfn)
    print(res)


    DIRAC.exit()


####################################################
if __name__ == "__main__":
    main()
