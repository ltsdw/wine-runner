from abc import ABC
from subprocess import Popen, PIPE, DEVNULL, STDOUT, run
from shutil import rmtree
from os import environ, path, chdir, mkdir
from typing import List, Dict, IO, Callable, Optional, NoReturn
from utils.funcs import die, negate, _print, restoreEnvar


class BaseHandler(ABC):
    """
    BaseHelper

    Abstract handler class.

    :profile_id: Application's profile id.
    :wine32_bin_path: Path to wine 32 bits binary.
    :wine64_bin_path: Path to wine 64 bits binary.
    :wineboot_bin_path: Path to wineboot.
    :winecfg_bin_path: Path to winecfg.
    :proton_directory: Path to proton's directory which will be used by umu.
    :application_directory: Path to the directory where the application's prefix will be created.
    :executables_aliases: Dictionary of format { "executable_aliase" : "/path/to/the/exectuable" }.
    :environment_variables: The environment variables to be used within wine's environment.
    :debug: Tell whether should display logs.
    :debug_filepath: Path to the file where logs should be saved if debug is set to true.
    """

    def __init__(
        self,
        profile_id: str,
        wine32_bin_path: str,
        wine64_bin_path: str,
        wineboot_bin_path: str,
        winecfg_bin_path: str,
        application_directory: str,
        runner: Callable[[str, Optional[List[str]]], None],
        executables_aliases: Dict[str, str],
        environment_variables: Dict[str, str] | None = None,
        debug: bool = False,
        debug_filepath: str | None = None
    ):
        self._profile_id: str                                   = profile_id
        self._wine32_bin_path: str                              = wine32_bin_path
        self._wine64_bin_path: str                              = wine64_bin_path
        self._wineboot_bin_path: str                            = wineboot_bin_path
        self._winecfg_bin_path: str                             = winecfg_bin_path
        self._application_directory: str                        = application_directory
        self._runner: Callable[[str, Optional[List[str]]], None]= runner
        self._executables_aliases: Dict[str, str]               = executables_aliases
        self._prefix: str                                       = path.join(application_directory, "pfx")
        self._debug: bool                                       = debug
        self._debug_filepath: str | None                        = debug_filepath

        if self.runCommandStatusChecked([self._wine32_bin_path, "--version"]) != 0:
            self._wine32_bin_path = "/usr/bin/wine"
            self._wine64_bin_path = "/usr/bin/wine64"
            self._wineboot_bin_path = "/usr/bin/wineboot"
            self._winecfg_bin_path = "/usr/bin/winecfg"

        if self.runCommandStatusChecked([self._wine32_bin_path, "--version"]) != 0:
            die(f"Wine not found at: {self._wine32_bin_path}.")

        if not path.exists(self._wineboot_bin_path):
            die(f"wineboot not found at: {self._wineboot_bin_path}")

        if not path.exists(self._winecfg_bin_path):
            die(f"winecfg not found at: {self._winecfg_bin_path}")

        environ["WINEPREFIX"] = self._prefix

        environ["PATH"] += ":" + path.dirname(self._wine64_bin_path)

        if environment_variables: self._setEnvironmentVariables(environment_variables)

        self._keepConsistentSyncMethod()

        if path.exists(self._prefix):
            if self.runCommandStatusChecked([self._wine64_bin_path, "winepath"]) == 0:
                environ["WINE"] = self._wine64_bin_path
            elif self.runCommandStatusChecked([self._wine32_bin_path, "winepath"]) == 0:
                environ["WINE"] = self._wine32_bin_path
            else:
                die(f"Failed to check if the prefix {self._prefix} is 32 or 64 bits.")

        _wine: str | None = environ.get("WINE")
        self._default_wine_path: str = _wine if _wine else self._wine64_bin_path


    @staticmethod
    def _keepConsistentSyncMethod() -> None:
        """
        _keepConsistentSyncMethod

        Keeps consistent method of synchronization chosen.

        :return:
        """

        sync_methods: List[str] = ["WINEESYNC", "PROTON_NO_ESYNC", "WINEFSYNC", "PROTON_NO_FSYNC"]
        sync_methods_specified: Dict[str, str] = {}

        for k, v in environ.items():
            if k in sync_methods:
                sync_methods_specified[k] = v

        if not sync_methods_specified:
            environ["WINEFSYNC"] = "1"
            environ["PROTON_NO_FSYNC"] = "0"
            environ["WINEESYNC"] = "0"
            environ["PROTON_NO_ESYNC"] = "1"

            return

        for key, str_value in sync_methods_specified.items():
            value: int = int(str_value) if str_value.isdigit() else 0 if key != "PROTON_NO_FSYNC" and key != "PROTON_NO_ESYNC" else 1

            if key == "WINEESYNC":
                environ["WINEESYNC"]        = str(value)
                environ["PROTON_NO_ESYNC"]  = str(negate(value))

                wine_fsync: str | None      = environ.get("WINEFSYNC") if environ["WINEESYNC"] == "0" else "0"
                environ["WINEFSYNC"]        = wine_fsync if wine_fsync else "0"
                environ["PROTON_NO_FSYNC"]  = str(negate(int(environ["WINEFSYNC"])))

                continue

            if key == "PROTON_NO_ESYNC":
                environ["WINEESYNC"]        = str(negate(value))
                environ["PROTON_NO_ESYNC"]  = str(value)

                wine_fsync: str | None      = environ.get("WINEFSYNC") if environ["WINEESYNC"] == "0" else "0"
                environ["WINEFSYNC"]        = wine_fsync if wine_fsync else "0"
                environ["PROTON_NO_FSYNC"]  = str(negate(int(environ["WINEFSYNC"])))

                continue

            if key == "WINEFSYNC":
                environ["WINEFSYNC"]        = str(value)
                environ["PROTON_NO_FSYNC"]  = str(negate(value))

                wine_esync: str | None      = environ.get("WINEESYNC") if environ["WINEFSYNC"] == "0" else "0"
                environ["WINEESYNC"]        = wine_esync if wine_esync else "0"
                environ["PROTON_NO_ESYNC"]  = str(negate(int(environ["WINEESYNC"])))

                continue

            if key == "PROTON_NO_FSYNC":
                environ["WINEFSYNC"] = str(negate(value))
                environ["PROTON_NO_FSYNC"] = str(value)

                wine_esync: str | None      = environ.get("WINEESYNC") if environ["WINEFSYNC"] == "0" else "0"
                environ["WINEESYNC"]        = wine_esync if wine_esync else "0"
                environ["PROTON_NO_ESYNC"]  = str(negate(int(environ["WINEESYNC"])))

                continue


    @staticmethod
    def _setEnvironmentVariables(environment_variables: Dict[str, str]) -> None:
        """
        _setEnvironmentVariables

        Sets the environment variables.

        :environment_variables: environemnt variables.
        :return:
        """

        for k, v in environment_variables.items():
            environ[k] = v


    @staticmethod
    def runCommandStatusChecked(cmd: List[str]) -> int:
        """
        runCommandStatusChecked

        Run a command without producing any logging and return the command exit code.

        :cmd: A list with a command as first element and its arguments.
        :return: Return code of the command.
        """

        return run(cmd, stdout = DEVNULL, stderr = DEVNULL).returncode


    @staticmethod
    def runCommand(
        cmd: List[str],
        debug: bool = False,
        debug_filepath: str | None = None
    ) -> None:
        """
        runCommand

        Spawns a new process.

        :cmd: A list with a command as first element and its arguments.
        :debug: Tell whether it should log to the command line.
        :debug_filepath: The path to  the file to write logs in.
        :return:
        """

        fd: int = PIPE if debug else DEVNULL
        lc_all: str | None = environ.get("LC_ALL")
        environ["LC_ALL"] = "C"

        if not debug:
            Popen(cmd, stdout = fd, stderr = STDOUT)

            restoreEnvar("LC_ALL", lc_all)

            return

        if debug and debug_filepath:
            with open(debug_filepath, 'w') as f:
                with Popen(
                    cmd,
                    stdout = f,
                    stderr = STDOUT,
                    text = True,
                    encoding="utf-8"
                ) as p: pass

            restoreEnvar("LC_ALL", lc_all)

            return

        with Popen(
            cmd,
            stdout = fd,
            stderr = STDOUT,
            text = True,
            encoding="utf-8"
        ) as p:
            _stdout: IO[str] | None = p.stdout

            if not _stdout:
                restoreEnvar("LC_ALL", lc_all)

                return

            for l in _stdout: _print(l, end = "")

            restoreEnvar("LC_ALL", lc_all)


    def runExe(
        self,
        mode: str = "waitforexitandrun",
        args: List[str] = []
    ) -> None:
        """
        Runs the app.

        :mode: The mode that should be used, defaults to --waitforexitandrun.
        :args: list of arguments.
        :return:
        """

        exe: str | None = args[0] if  args else None

        for k, v in self._executables_aliases.items():
            if not exe:
                if not path.exists(v):
                    _print(f"Path: {v} does not exist.")

                    continue

                chdir(path.dirname(v))
                self._runner(mode, [v, *args])

                return

            if k == exe or v == exe:
                if not path.exists(v):
                    _print(f"Path: {v} does not exist.")

                    continue

                chdir(path.dirname(v))
                self._runner(mode, [v, *args[1:]])

                return


    def wineboot(self, args: List[str] | None = None) -> None:
        """
        wineboot

        Runs wineboot

        :args: (Optional) List of arguments.
        :return:
        """

        raise NotImplementedError(f"Method {self.wineboot.__name__} not implemented.")


    def killAll(self) -> None:
        """
        killAll

        Calls wineboot with --kill flag.

        :return:
        """

        raise NotImplementedError(f"Method {self.killAll.__name__} not implemented.")


    def initWinePrefix(self) -> None:
        """
        initWinePrefix

        Setups a new prefix.

        :return:
        """

        _print("Initiating prefix.")

        if not path.exists(self._application_directory):
            mkdir(self._application_directory)

        self.wineboot(["--init"])

        _print("Prefix creted.")


    def reg(self, dll_name: str, action: str, data: str | None = None) -> None | NoReturn:
        """
        reg

        Uses Wine's reg command to override DLLs values or remove them.

        :dll_name: Name of the DLL.
        :action: Action that can be either add or delete.
        :data: The value that a DLL should have when added.
        """

        args: List[str] = \
        [
            "reg",
            action,
            r"HKEY_CURRENT_USER\Software\Wine\DllOverrides",
            "/v",
            dll_name,
            "/t",
            "REG_SZ",
            "/d",
            data,
            "/f"
        ] if action == "add" and data \
        else \
        [
            "reg",
            action,
            r"HKEY_CURRENT_USER\Software\Wine\DllOverrides",
            "/v",
            dll_name,
            "/f"
        ] if action == "delete" \
        else die("Malformed wine reg command.")

        self._runner("run", args)


    def installDXVK(self) -> None:
        """
        installDXVK

        Install DXVK.

        :return:
        """

        raise NotImplementedError(f"Method {self.installDXVK.__name__} not implemented.")


    def uninstallDXVK(self) -> None:
        """
        uninstallDXVK

        Uninstall DXVK.

        :return:
        """

        raise NotImplementedError(f"Method {self.uninstallDXVK.__name__} not implemented.")


    def installDXVKNVAPI(self) -> None:
        """
        installDXVKNVAPI

        Install DXVK NVAPI.

        :return:
        """

        raise NotImplementedError(f"Method {self.installDXVKNVAPI.__name__} not implemented.")


    def uninstallDXVKNVAPI(self) -> None:
        """
        uninstallDXVKNVAPI

        Uninstall DXVK NVAPI.

        :return:
        """

        raise NotImplementedError(f"Method {self.uninstallDXVKNVAPI.__name__} not implemented.")


    def installGalliumNine(self) -> None:
        """
        installGalliumNine

        Install gallium nine.

        :return:
        """

        raise NotImplementedError(f"Method {self.installGalliumNine.__name__} not implemented.")


    def uninstallGalliumNine(self) -> None:
        """
        uninstallGalliumNine

        Uninstall gallium nine.

        :return:
        """

        raise NotImplementedError(f"Method {self.uninstallGalliumNine.__name__} not implemented.")


    def winetricks(self, args: List[str] | None = None) -> None:
        """
        winetricks

        Install stuffs with winetricks.

        :args: list of things to install.
        :return:
        """

        raise NotImplementedError(f"Method {self.winetricks.__name__} not implemented.")


    def winecfg(self) -> None:
        """
        winecfg

        Runs wine configuration.

        :return:
        """

        self.runCommand([self._winecfg_bin_path], self._debug, self._debug_filepath)


    def getProfileId(self) -> str:
        """
        getProfileId

        Gets the application's profile id.

        :return: The pplication's profile id as a string.
        """

        return self._profile_id


    def destroyPrefix(self) -> None:
        """
        destroyPrefix

        Removes the prefix.

        :return:
        """

        _print(f"Removing prefix: {self._prefix}.")

        if path.exists(self._application_directory):
           rmtree(self._application_directory, ignore_errors=True)

        _print(f"Removed prefix: {self._prefix}.")


    def getDefaultWinePath(self) -> str:
        """
        getDefaultWinePath

        Gets the default default wine being used.

        :return: The path to the default wine.
        """

        return self._default_wine_path

