from subprocess import Popen, PIPE, DEVNULL, STDOUT
from shutil import rmtree
from os import environ, path, mkdir
from typing import List, Dict, IO
from Utils.Funcs import die


class WineHelper:
    def __init__(
        self,
        wine_path: str,
        app_dir: str,
        envars: Dict[str, str] | None = None,
        cache_dir: str | None = None,
        dxvk_cache_dir: str | None = None,
        show_logs: bool = False,
        logs_filepath: str | None = None
    ):
        """
        WineHelper

        :wine_path: path to wine's bin directory.
        :app_dir: path to where the application's prefix will be created.
        :envars: the environment variables to be used within wine's context.
        :cache_dir: path to cache mesa shader.
        :dxvk_cache_dir: path to cache dxvk pipeline state.
        :show_logs: tell whether should display logs.
        :logs_filepath: if present logs will be saved to this file.
        :return:
        """


        self._wine_path: str            = wine_path
        self._wine_bin: str             = path.join(self._wine_path, "wine")
        self._app_dir: str              = app_dir
        self._prefix: str               = path.join(app_dir, "pfx")
        self._show_logs: bool           = show_logs
        self._logs_filepath: str | None = logs_filepath

        if cache_dir:
            environ["MESA_SHADER_CACHE_DIR"] = cache_dir

        if dxvk_cache_dir:
            environ["DXVK_STATE_CACHE_PATH"] = dxvk_cache_dir

        if path.exists(self._wine_bin):
            environ["PATH"] += ":" + self._wine_path
            environ["WINE"] = self._wine_bin
        else:
            die(f"Wine not found at: {self._wine_bin}")

        environ["WINEPREFIX"] = self._prefix

        if envars:
            self._setEnvars(envars)


    @staticmethod
    def _setEnvars(envars: Dict[str, str]) -> None:
        """
        Sets the environment variables.

        :envars: environemnt variables.
        :return:
        """

        for k, v in envars.items():
            environ[k] = v


    @staticmethod
    def _runCommand(
        cmd: List[str],
        show_logs: bool = False,
        logs_filepath: str | None = None
    ) -> None:
        """
        Spawns a new process.

        :cmd: a list with a command as first element and its arguments.
        :show_logs: tell whether it should log to the command line.
        :log_path: a path to log file.
        :return:
        """


        if logs_filepath:
            with open(logs_filepath, 'w') as f:
                with Popen(cmd, stdout=f, stderr=STDOUT, bufsize=0, universal_newlines=True) as _:
                    pass
        else:

            stream: int = PIPE if show_logs else DEVNULL

            with Popen(cmd, stdout=stream, stderr=STDOUT, universal_newlines=True) as p:
                _stdout: IO[str] | None = p.stdout
                    
                if _stdout:
                    for l in _stdout:
                        print(l, end="")


    def _winePathCommand(self, cmd: str) -> str:
        """
        Returns the absolute path to the command.

        :cmd: command to be appended to the wine directory path.
        :return: the absolute path with the appended command.
        """
        

        return path.join(self._wine_path, cmd)

        
    def wine(
        self, args: List[str] | None = None
    ) -> None:
        """
        Run the program with wine.

        :args: A list with the program and its arguments.
        :return:
        """

        cmd: str = self._winePathCommand("wine")

        if not path.exists(cmd):
            die(f"Wine not found at: {cmd}")

        if args:
            self._runCommand([cmd] + args, self._show_logs, self._logs_filepath)
        else:
            self._runCommand([cmd, "--version"], self._show_logs, self._logs_filepath)


    def initWinePrefix(self) -> None:
        """
        Setups a new prefix.

        :return:
        """


        print("Initiating prefix.")

        cmd: str = self._winePathCommand("wineboot")

        if not path.exists(cmd):
            die(f"Wineboot not found at: {cmd}")

        if not path.exists(self._app_dir):
            mkdir(self._app_dir)

        self._runCommand([cmd, "--init"], self._show_logs, self._logs_filepath)

        print("Prefix initiated")


    def winecfg(self) -> None:
        """
        Runs wine configuration.

        :return:
        """


        cmd: str = self._winePathCommand("winecfg")

        if not path.exists(cmd):
            die(f"Winecfg not found at: {cmd}")

        self._runCommand([cmd], self._show_logs, self._logs_filepath)


    def installDXVK(self) -> None:
        """
        Install DXVK.

        :return:
        """


        cmd: str = self._winePathCommand("setup_dxvk.sh")

        if not path.exists(cmd):
            die(f"Setup_dxvk not found at: {cmd}")

        self._runCommand([cmd, "install"], self._show_logs, self._logs_filepath)


    def uninstallDXVK(self) -> None:
        """
        Uninstall DXVK.

        :return:
        """


        cmd: str = self._winePathCommand("setup_dxvk.sh")

        if not path.exists(cmd):
            die(f"Setup_dxvk.sh not found at: {cmd}")

        self._runCommand([cmd, "uninstall"], self._show_logs, self._logs_filepath)


    def installGalliumNine(self) -> None:
        """
        Install gallium nine.

        :return:
        """


        cmd: str = self._winePathCommand("nine-install.sh")

        if not path.exists(cmd):
            die(f"Nine-install.sh not found at: {cmd}")

        self._runCommand([cmd], self._show_logs, self._logs_filepath)


    def galliumNineConfig(self) -> None:
        """
        Gallium Nine's configuration tool.

        :return:
        """


        self.wine(["ninewinecfg"])


    def uninstallGalliumNine(self) -> None:
        """
        Uninstall gallium nine.

        :return:
        """


        try:
            from os import remove


            win_path: str = path.join(self._prefix, "dosdevices/c:/windows/system32")
            win64_path: str = path.join(self._prefix, "dosdevices/c:/windows/syswow64")

            remove(path.join(win64_path, "d3d9.dll"))
            remove(path.join(win64_path, "d3d9-nine.dll"))
            remove(path.join(win64_path, "ninewinecfg.exe"))
            remove(path.join(win_path, "d3d9-nine.dll"))
            remove(path.join(win_path, "ninewinecfg.exe"))

        except FileNotFoundError:
            pass

        
        self.wine(
            [
                "reg",
                "delete",
                "\'HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides\'",
                "/v",
                "d3d9",
                "/f"
            ]
        )


    def winetricks(self, args: List[str] | None = None) -> None:
        """
        Install stuffs with winetricks.

        :args: list of things to install.
        :return:
        """


        cmd: str = self._winePathCommand("winetricks")

        if not path.exists(cmd):
            die(f"Winetricks not found at: {cmd}")

        if args:
            self._runCommand([cmd] + args, self._show_logs, self._logs_filepath)
        else:
            self._runCommand([cmd, "--version"], self._show_logs, self._logs_filepath)

    
    def removePrefix(self) -> None:
        """
        Removes the prefix.

        :return:
        """


        if path.exists(self._app_dir):
           rmtree(self._app_dir, ignore_errors=True)

