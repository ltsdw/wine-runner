from os import path, mkdir
from json import dumps
from typing import Dict, Any


class Repair:
    def __init__(self):
        """
        Creates a MyApps directory and example json file if they don't exist.
        """


        root_dir: str = path.join(path.dirname(__file__), "../../")
        my_apps_dir: str = path.join(root_dir, "MyApps") 
        example_json_path: str = path.join(my_apps_dir, "example.json")


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


        if path.exists(path.join(root_dir, "wine")):
            if not path.exists(my_apps_dir):
                mkdir(my_apps_dir)

            if not path.exists(example_json_path):
                with open(example_json_path, "w") as fp:
                    fp.write(dumps(example_json, indent=4))

