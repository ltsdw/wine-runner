from os import environ, path, mkdir
from sys import stderr
from typing import List, Dict
from utils.funcs import die, _print
from handlers import BaseHandler


class UMUHandler(BaseHandler):
    """
    UMUHelper

    :profile_id: Application's profile id.
    :umu_directory: Path to umu directory.
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
        umu_directory: str | None,
        proton_directory: str | None,
        application_directory: str,
        executables_aliases: Dict[str, str],
        environment_variables: Dict[str, str] | None = None,
        debug: bool = False,
        debug_filepath: str | None = None
    ):
        self._umu_directory: str

        if not umu_directory or (umu_directory and not path.exists(umu_directory)):
            self._umu_directory = "/usr/bin"

            _print(f"umu-run not found at: {umu_directory}\n"
                   f"Defaulting to system's umu-run directory at: {self._umu_directory}", stderr)
        else:
            self._umu_directory = umu_directory

        self._profile_id: str               = profile_id
        self._umu_run_path: str             = path.join(self._umu_directory, "umu-run")
        self._proton_directory: str | None  = proton_directory

        self._application_directory: str    = application_directory
        self._debug: bool                   = debug
        self._debug_filepath: str | None    = debug_filepath

        exit_code: int = self.runCommandStatusChecked([self._umu_run_path, "--help"])

        if exit_code != 0 and self.runCommandStatusChecked([self._umu_run_path, "--help"]) != 0:
            die(f"umu-run not found at: {self._umu_run_path}")

        if not path.isfile(self._umu_run_path):
            die(f"umu-run path isn't a file: {self._umu_run_path}")

        if self._proton_directory and path.exists(self._proton_directory):
            proton_path: str = path.join(self._proton_directory, "proton")

            if path.exists(proton_path):
                environ["PROTONPATH"] = self._proton_directory
            else:
                _print(
                    f"Proton wasn't found at the directory: {self._proton_directory}\n"
                    f"Defaulting to UMU's proton path.", stderr
                )

        environ["PATH"] += ":" + path.dirname(self._umu_run_path)

        super().__init__(
            self._profile_id,
            None, # No need to specify wine path
            None, # No need for specify wine64 path
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

        self.runCommand([self._umu_run_path, "run", "wineboot", *_args], True)


    def winecfg(self) -> None:
        """
        Runs wine configuration.

        :return:
        """

        self.runCommand([self._umu_run_path, "run", "winecfg"], self._debug, self._debug_filepath)


    def killAll(self) -> None:
        """
        killAll

        Calls wineboot with --kill flag.

        :return:
        """

        self.runCommand([self._umu_run_path, "wineboot", "--kill"], True)

