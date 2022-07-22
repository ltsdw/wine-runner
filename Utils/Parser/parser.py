from os import path, mkdir, listdir
from json import load
from typing import List, Any, Dict
from Utils.Funcs import die
from Utils.App import App


class Parser:
    def __init__(self):
        """
        Parse the JSON files from the MyApps directory and create App objects from they.
        """


        self._my_apps_dir: str = path.abspath(path.join(path.dirname(__file__), "../../MyApps"))

        if not path.exists(self._my_apps_dir):
            mkdir(self._my_apps_dir)


    def createModels(self) -> List[App]:
        """
        run through MyApps directory and create Model class objects from the json files.

        :return: a list with models.
        """


        apps_list: List[App] = []

        for f in listdir(self._my_apps_dir):
            file_path: str = path.join(self._my_apps_dir, f)

            if path.isfile(file_path):
                with open(file_path, "r") as fp:
                    app_data: Any = load(fp)


                    _id: str 

                    try:
                        _id = (
                            app_data["id"]
                            if isinstance(app_data["id"], str) and app_data["id"]
                            else die("Couldn't parse application's id.")
                        )
                    except KeyError as e:
                        die(f"Couldn't parse application's id: {e}")


                    if _id == "example":
                        continue


                    wine_path: str 

                    try:
                        wine_path = (
                            path.expandvars(app_data["wine_path"])
                            if isinstance(app_data["wine_path"], str) and app_data["wine_path"]
                            else die("Couldn't parse wine_path.")
                        )
                    except KeyError as e:
                        die(f"Couldn't parse wine_path: {e}")


                    app_dir: str

                    try:
                        app_dir = (
                            path.expandvars(app_data["app_dir"])
                            if isinstance(app_data["app_dir"], str) and app_data["app_dir"]
                            else die("Couldn't parse app_dir.")
                        )
                    except KeyError as e:
                        die(f"Couldn't parser app_dir: {e}")


                    exe_dir: str | None

                    try:
                        exe_dir = (
                            path.expandvars(app_data["executable_dir"])
                            if isinstance(app_data["executable_dir"], str) and app_data["executable_dir"]
                            else None
                        )
                    except KeyError:
                        exe_dir = None


                    envars: Dict[str, str] | None

                    try:
                        envars = (
                            app_data["envars"]
                            if isinstance(app_data["envars"], dict) and app_data["envars"]
                            else None
                        )
                    except KeyError:
                        envars = None


                    cache_dir: str | None

                    try:
                        cache_dir = (
                            path.expandvars(app_data["cache_dir"])
                            if isinstance(app_data["cache_dir"], str) and app_data["cache_dir"]
                            else None
                        )
                    except KeyError:
                        cache_dir = None


                    dxvk_cache_dir: str | None

                    try:
                        dxvk_cache_dir = (
                            path.expandvars(app_data["dxvk_cache_dir"])
                            if isinstance(app_data["dxvk_cache_dir"], str) and app_data["dxvk_cache_dir"]
                            else None
                        )
                    except KeyError:
                        dxvk_cache_dir = None


                    executables: Dict[str, str] | None

                    try: 

                        executables = (
                            app_data["executables"]
                            if isinstance(app_data["executables"], dict) and app_data["executables"]
                            else None
                        )
                    except KeyError:
                        executables = None


                    show_logs: bool

                    try:
                        show_logs = (
                            app_data["debug"]
                            if isinstance(app_data["debug"], bool) and app_data["debug"]
                            else True
                        )
                    except KeyError:
                        show_logs = True


                    logs_filepath: str | None

                    try:
                        logs_filepath = (
                            path.expandvars(app_data["logs_filepath"])
                            if isinstance(app_data["logs_filepath"], str) and app_data["logs_filepath"]
                            else None
                        )
                    except KeyError:
                        logs_filepath = None


                    app: App = App(
                        _id             = _id,
                        wine_path       = wine_path,
                        app_dir         = app_dir,
                        exe_dir         = exe_dir,
                        envars          = envars,
                        cache_dir       = cache_dir,
                        dxvk_cache_dir  = dxvk_cache_dir,
                        executables     = executables,
                        show_logs       = show_logs,
                        logs_filepath   = logs_filepath
                    )

                    apps_list.append(app)

        return apps_list
