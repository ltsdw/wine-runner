from os import environ, path, mkdir
from typing import List, Dict
from utils.funcs import die, _print
from handlers import BaseHandler


class UMUHandler(BaseHandler):
    """
    UMUHelper

    :profile_id: Application's profile id.
    :umu_run_path: Path to umu directory.
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
        umu_run_path: str,
        proton_directory: str,
        application_directory: str,
        executables_aliases: Dict[str, str],
        environment_variables: Dict[str, str] | None = None,
        debug: bool = False,
        debug_filepath: str | None = None
    ):

        self._profile_id: str           = profile_id
        self._umu_run_path: str         = umu_run_path
        self._proton_directory: str     = proton_directory
        self._wine32_bin_path: str        = path.join(self._proton_directory, "files/bin/wine")
        self._wine64_bin_path: str        = path.join(self._proton_directory, "files/bin/wine64")
        self._wine_lib_dir: str         = path.join(self._proton_directory, "files/lib")
        self._wine_lib64_dir: str       = path.join(self._proton_directory, "files/lib64")
        self._wineboot_bin_path: str    = path.join(self._wine_lib64_dir, "wine/x86_64-windows/wineboot.exe")
        self._winecfg_bin_path: str     = path.join(self._wine_lib64_dir, "wine/x86_64-windows/winecfg.exe")
        self._application_directory: str= application_directory
        self._debug: bool               = debug
        self._debug_filepath: str | None= debug_filepath

        exit_code: int = self.runCommandStatusChecked([self._umu_run_path, "--help"])

        if exit_code != 0:
            self._umu_run_path = "/usr/bin/umu-run"

        if exit_code != 0 and self.runCommandStatusChecked([self._umu_run_path, "--help"]) != 0:
            die(f"umu-run not found at: {self._umu_run_path}")

        if not path.isfile(self._umu_run_path):
            die(f"umu-run path isn't a file: {self._umu_run_path}")

        if not path.exists(self._proton_directory):
            die(f"Proton directory does not exist at: {self._proton_directory}")

        environ["PATH"] += ":" + path.dirname(self._umu_run_path)
        environ["PATH"] += ":" + self._proton_directory

        super().__init__(
            self._profile_id,
            self._wine32_bin_path,
            self._wine64_bin_path,
            self._wineboot_bin_path,
            self._winecfg_bin_path,
            self._application_directory,
            self.umuRun,
            executables_aliases,
            environment_variables,
            self._debug,
            self._debug_filepath
        )


    def umuRun(self, mode: str = "waitforexitandrun", args: List[str] | None = None) -> None:
        """
        umuRun

        Run the program with UMU.

        :mode: The mode that should be used, defaults to waitforexitandrun.
        :args: A list with the program and its arguments.
        :return:
        """

        _args: List[str] = args if args else ["--help"]

        self.runCommand([self._umu_run_path, mode, *_args], self._debug, self._debug_filepath)


    def wineboot(self, args: List[str] | None = None) -> None:
        """
        wineboot

        Runs wineboot

        :args: (Optional) List of arguments.
        :return:
        """

        _args: List[str] = args if args else ["--help"]

        self.runCommand([self._umu_run_path, "runinprefix", "wineboot", *_args], True)


    def initWinePrefix(self) -> None:
        """
        Setups a new prefix.

        :return:
        """

        _print("Initiating prefix.")

        if not path.exists(self._application_directory):
            mkdir(self._application_directory)

        self.wineboot(["--init"])

        _print("Prefix creted.")


    def winecfg(self) -> None:
        """
        Runs wine configuration.

        :return:
        """

        self.runCommand([self._umu_run_path, "runinprefix", "winecfg"], self._debug, self._debug_filepath)


    def killAll(self) -> None:
        """
        killAll

        Calls wineboot with --kill flag.

        :return:
        """

        self.runCommand([self._umu_run_path, "wineboot", "--kill"], True)

