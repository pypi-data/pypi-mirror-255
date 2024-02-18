#!/usr/bin/env python
"""
Move a service from DIPS to HTTPS using Tornado

Prereq:
The service shloud be already install.
Tornado service must be installed.
The HandlerPath must exists: DIRAC/.../*TornadoHandler.py

Usage:
cta-install-tornado-component <System> <Component> <HandlerPath>
"""
import subprocess as sp
import os
import shutil
import glob

from DIRAC import exit as DIRACexit
from DIRAC.Core.Base.Script import Script

from DIRAC.ConfigurationSystem.Client.CSAPI import CSAPI
from DIRAC import gConfig, gLogger
from DIRAC.FrameworkSystem.Client.ComponentInstaller import gComponentInstaller
from DIRAC.Core.Utilities.Extensions import extensionsByPriority
from DIRAC.ConfigurationSystem.Client.Helpers import CSGlobals


class TornadoComponentInstaller:
    def __init__(self):
        self.setup = CSGlobals.getSetup()
        self.tornadoPort = self._getValue(f"/Systems/Tornado/{self.setup}/Port")
        self.cfgClient = CSAPI()

    def _removeOptionFromCS(self, path):
        """
        Delete options from central CS
        """
        result = self.cfgClient.downloadCSData()
        if not result["OK"]:
            return result
        result = self.cfgClient.delOption(path)
        if not result["OK"]:
            return result
        result = self.cfgClient.commit()
        return result

    def _modifyValue(self, path, new_value):
        result = self.cfgClient.downloadCSData()
        if not result["OK"]:
            return result
        result = self.cfgClient.modifyValue(path, new_value)
        if not result["OK"]:
            return result
        result = self.cfgClient.commit()
        return result

    def _setOption(self, path, value):
        result = self.cfgClient.downloadCSData()
        if not result["OK"]:
            return result
        result = self.cfgClient.setOption(path, value)
        if not result["OK"]:
            return result
        result = self.cfgClient.commit()
        return result

    def _getValue(self, path):
        value = gConfig.getValue(path)
        return value

    def _getSection(self, path):
        section = gConfig.getSections(path)
        return section

    def _getHosts(self):
        hosts = gConfig.getSections("/Registry/Hosts/")
        return hosts

    def valueExists(self, path):
        value = self._getValue(path)
        if value is None:
            return True
        else:
            return False

    def removeComponent(self, system, component, removeLogs):
        res = gComponentInstaller.runsvctrlComponent(system, component, "d")
        if not res["OK"]:
            gLogger.error(res)
        res = gComponentInstaller.unsetupComponent(system, component)
        if not res["OK"]:
            gLogger.error(res)

        if removeLogs:
            for runitCompDir in glob.glob(
                os.path.join(self.runitDir, system, component)
            ):
                try:
                    shutil.rmtree(runitCompDir)
                except Exception:
                    gLogger.exception()

    def checkTornadoHandlerPath(self, handlerPathValue):
        cmd = "pip show DIRAC | grep Location | awk -F' ' '{print $2}'"
        out = sp.getstatusoutput(cmd)
        if out[0] == 0:
            diracLocation = out[1]
        else:
            gLogger.error(out[1])

        handlerPath = f"{diracLocation}/{handlerPathValue}"
        res = sp.getstatusoutput(f"ls {handlerPath}")

        if res[0] == 0:
            gLogger.notice(f"Find HandlerPath: {handlerPathValue}")
            return True
        else:
            gLogger.error(res[1])
            return False

    def installTornadoService(self, system, service, handlerPathValue):
        res = self.checkTornadoHandlerPath(handlerPathValue)
        if not res:
            gLogger.error("Did not find HandlerPath")
            DIRACexit(1)

        servicePath = f"/Systems/{system}/{self.setup}/Services/{service}"
        # change Port value
        portPath = f"{servicePath}/Port"
        currentPort = self._getValue(portPath)
        if not currentPort:
            gLogger.error(f"No Port find for {system}/{service}")
            DIRACexit(1)
        if self._getValue(portPath):
            result = self._removeOptionFromCS(portPath)
            if not result["OK"]:
                gLogger.error(result["Message"])
                DIRACexit(1)
            gLogger.notice(f"Succesfully removed {system}/{service} Port value")

        # add protocol https
        protocolPath = f"{servicePath}/Protocol"
        if self._getValue(protocolPath):
            result = self._modifyValue(protocolPath, "https")
        else:
            result = self._setOption(protocolPath, "https")
        if not result["OK"]:
            gLogger.error(result["Message"])
            DIRACexit(1)
        gLogger.notice(f"Succesfully add {system}/{service} Protocol value")

        # add tornado HandlerPath
        handlerPath = f"{servicePath}/HandlerPath"
        if self._getValue(handlerPath):
            result = self._modifyValue(handlerPath, handlerPathValue)
        else:
            result = self._setOption(handlerPath, handlerPathValue)
        if not result["OK"]:
            gLogger.error(result["Message"])
            DIRACexit(1)
        gLogger.notice(f"Succesfully add {system}/{service} HandlerPath value")

        # change URL port
        urlPath = f"/Systems/{system}/{self.setup}/URLs/{service}"
        urlDIPS = self._getValue(urlPath)
        if urlDIPS:
            urlHTTPS = urlDIPS.replace("dips", "https")
            urlHTTPS = urlHTTPS.replace(currentPort, self.tornadoPort)
            result = self._modifyValue(urlPath, urlHTTPS)
        else:
            hosts = self._getHosts()
            host = hosts[0]
            urlHTTPS = f"https://{host}:{self.tornadoPort}/{system}/{service}"
            result = self._setOption(urlPath, urlHTTPS)
        if not result["OK"]:
            gLogger.error(result["Message"])
            DIRACexit(1)
        gLogger.notice(f"Succesfully change {system}/{service} URL value")

        # remove component:
        self.removeComponent(system, service, False)
        gLogger.notice(f"Succesfully remove {system}/{service} startup and runit")
        # restart tornado service:
        result = gComponentInstaller.runsvctrlComponent("Tornado", "Tornado", "t")
        gLogger.notice("Succesfully restart Tornado service")


@Script()
def main():
    Script.parseCommandLine(ignoreErrors=True)

    TornadoInstaller = TornadoComponentInstaller()
    gComponentInstaller.exitOnError = True

    setOverwrite = False
    setSpecialOption = False
    Script.registerSwitch(
        "w", "overwrite", "Overwrite the configuration in the global CS", setOverwrite
    )
    Script.registerSwitch(
        "p:", "parameter=", "Special component option ", setSpecialOption
    )

    # Registering arguments will automatically add their description to the help menu

    Script.registerArgument(
        (
            "System/Component: Full component name (ie: WorkloadManagement/Matcher)",
            "System:           Name of the DIRAC system (ie: WorkloadManagement)",
        )
    )
    Script.registerArgument(
        " HandlerPath:        HandlerPath (i.e DIRAC/.../TornadoHandler)",
        mandatory=True,
    )
    Script.registerArgument(
        " Component:        Name of the DIRAC service (ie: Matcher)", mandatory=False
    )

    Script.parseCommandLine()
    args = Script.getPositionalArgs()

    if len(args) == 2:
        args = args[0].split("/") + args[1]

    if len(args) != 3:
        Script.showHelp(exitCode=1)
    system = args[0]
    component = args[1]
    handlerPath = args[2]

    result = gComponentInstaller.getSoftwareComponents(extensionsByPriority())
    if not result["OK"]:
        gLogger.error(result["Message"])
        DIRACexit(1)
    availableComponents = result["Value"]

    for compType in availableComponents:
        if (
            system in availableComponents[compType]
            and component in availableComponents[compType][system]
        ):
            break
    else:
        gLogger.error(
            f"Component {system}/{component} is not available for installation"
        )
        DIRACexit(1)

    TornadoInstaller.installTornadoService(system, component, handlerPath)


if __name__ == "__main__":
    main()
