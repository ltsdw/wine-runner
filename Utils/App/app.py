from os import path, chdir
from typing import Dict
from Utils.Funcs import die
from WineHelper import WineHelper


class App(WineHelper):
    """
    Every app must inherit from this class.

    :_id: application's id.
    :wine_path: path the wine's bin directory.
    :app_dir: path to where the prefix will be created.
    :exe_dir: path to the application's root directory.
    :envars: environment variables.
    :executables: dictionary of executables that can be executed.
    :show_logs: tell whether should display logs.
    :logs_filepath: if present logs will be saved to this file.
    """


    def __init__(
        self,
        _id: str, 
        wine_path: str,
        app_dir: str,
        exe_dir: str | None = None,
        envars: Dict[str, str] | None = None,
        executables: Dict[str, str] | None = None,
        show_logs: bool = False,
        logs_filepath: str | None = None
    ):

        self._id: str                           = _id
        self._wine_path: str                    = wine_path
        self._app_dir: str                      = app_dir
        self._exe_dir: str | None               = exe_dir
        self._envars: Dict[str, str] | None     = envars
        self._executables: Dict[str, str] | None= executables
        self._show_logs: bool                   = show_logs
        self._logs_filepath: str | None         = logs_filepath


    def runExe(self, exe: str | None = None) -> None:
        """
        Runs the app.

        :exe: the executable to be run, if not specified runs the first executable it finds.
        :return:
        """


        if self._executables:
            for k, v in self._executables.items():
                if not exe:
                    self.wine([v])

                    return

                if k == exe or v == exe:
                    if path.exists(v):
                        self.wine([v])

                        return

        die(f"Executable for {exe} not found at: {self._exe_dir}")


    def getId(self) -> str:
        """
        Gets the application id.

        :return: a string representing application's id.
        """


        return self._id


    def createApp(self) -> None:
        """
        Initiates the WineHelper object.
        This function must always be called after creating the App object.

        :return:
        """


        if self._exe_dir:
            if path.exists(self._exe_dir):
                chdir(self._exe_dir)
            else:
                self._exe_dir = path.join(self._app_dir, "pfx", self._exe_dir)

                if path.exists(self._exe_dir):
                    chdir(self._exe_dir)


        super().__init__(
            wine_path       = self._wine_path,
            app_dir         = self._app_dir,
            envars          = self._envars,
            show_logs       = self._show_logs,
            logs_filepath   = self._logs_filepath
        )

