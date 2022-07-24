from os import path, mkdir, environ
from json import dumps
from typing import Dict, Any, List
from Utils.Funcs import die


class Repair:
    def __init__(self):
        """
        Creates a MyApps directory and example json file if they don't exist.
        """


        example_json: Dict[str, Any] = {
                "id": "example",
                "wine_path": "path/to/wine/usr/bin",
                "app_dir": "path/to/app",
                "executable_dir": "path/to/app.exe",

                "envars": {
                    "WINEDEBUG": "-all",
                    "WINEFSYNC_FUTEX2": "0",
                    "WINEFSYNC": "0",
                    "WINEESYNC": "0",
                    "WINEFSYNC_SPINCOUNT": "100",
                    "WINE_DISABLE_WRITE_WATCH": "0",
                    "STAGING_SHARED_MEMORY": "0",
                    "STAGING_WRITECOPY": "0",
                    "MESA_SHADER_CACHE_DIR": "path/to/mesa/shader/cache",
                    "DXVK_STATE_CACHE_PATH": "path/to/dxvk/state/pipeline/cache",
                    "mesa_glthread": "false",
                    "DXVK_HUD": "0",
                },

                "executables": {
                    "exe_one": "exe_one.exe",
                    "exe_two": "exe_two.exe",
                    "exe_three": "exe_three.exe",
                    "config_exe": "exe_two_config.exe"
                },

                "debug": False,

                "logs_filepath": "path/to/where/savelogs.txt"

        }


        self._second_dir: str = path.join(path.dirname(__file__), "../../")
        snd_example_json_path: str


        if not path.exists(path.join(self._second_dir, "wine")):
            die(f"Not the root of wine-runner directory: {self._second_dir}")

        self._second_apps_dir: str = path.join(self._second_dir, "MyApps")

        snd_example_json_path = path.join(self._second_apps_dir, "example.json")

        if not path.exists(self._second_apps_dir):
            mkdir(self._second_apps_dir)

        if not path.exists(snd_example_json_path):
            with open(snd_example_json_path, "w") as fp:
                fp.write(dumps(example_json, indent=4))


        self._first_dir: str | None = None
        self._first_apps_dir: str | None = None


        try:
            self._first_dir = path.join(environ["XDG_CONFIG_HOME"], "wine-runner")

            if not path.exists(self._first_dir):
                mkdir(self._first_dir)

            self._first_apps_dir = path.join(self._first_dir, "MyApps")

            if not path.exists(self._first_apps_dir):
                mkdir(self._first_apps_dir)

            example_json_path: str = path.join(self._first_apps_dir, "example.json")

            if not path.exists(example_json_path):
                with open(example_json_path, "w") as fp:
                    fp.write(dumps(example_json, indent=4))
        except KeyError:
            pass


    def getAppsDirectories(self) -> List[Any]:
        """
        :return: the path the application's json configuration files.
        """


        return [self._first_apps_dir, self._second_apps_dir]

