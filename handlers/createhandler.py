from typing import Dict
from utils.funcs import die
from handlers import UMUHandler, WineHandler


def createHandler(
        default_runner: str,
        profile_id: str,
        application_directory: str,
        executables_aliases: Dict[str, str],
        wine_directory: str | None = None,
        umu_run_path: str | None = None,
        proton_directory: str | None = None,
        environment_variables: Dict[str, str] | None = None,
        debug: bool = False,
        debug_filepath: str | None = None,
        dxvk_directory: str | None = None,
        dxvk_nvapi_directory: str | None = None,
        winetricks_path: str | None = None,
        gallium_nine_directory: str | None = None
    ) -> UMUHandler | WineHandler:
    """
    createHandler

    :default_runner_arg: Default runner.
    :profile_id: Application's profile id.
    :application_directory: Path to the directory where the application's prefix will be created.
    :executables_aliases: Dictionary of format { "executable_aliase" : "/path/to/the/exectuable" }.
    :wine_directory: Path to the wine's bin directory.
    :umu_run_path: Path to umu directory.
    :proton_directory: Path to proton's directory which will be used by umu.
    :environment_variables: The environment variables to be used within wine's environment.
    :debug: Tell whether should display logs.
    :debug_filepath: Path to the file where logs should be saved if debug is set to true.
    :dxvk_directory: Path to DXVK.
    :dxvk_nvapi_directory: Path to DXVK NVAPI.
    :winetricks_path: Path to the winetricks script.
    :gallium_nine_directory: Path to GalliumNine directory.
    :return: A handler of type UMUHandler or WineHandler.
    """

    if default_runner == "umu" and umu_run_path and proton_directory:
        return UMUHandler(
            profile_id,
            umu_run_path,
            proton_directory,
            application_directory,
            executables_aliases,
            environment_variables,
            debug,
            debug_filepath
        )

    if default_runner == "wine" and wine_directory:
        return WineHandler(
            profile_id,
            wine_directory,
            application_directory,
            executables_aliases,
            environment_variables,
            debug,
            debug_filepath,
            dxvk_directory,
            dxvk_nvapi_directory,
            winetricks_path,
            gallium_nine_directory
        )

    die("No wine, umu or proton specified, exiting.")

