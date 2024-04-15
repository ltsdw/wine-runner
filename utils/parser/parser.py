from os import path, listdir
from tomllib import load
from typing import Any, Dict, Generator, List, NoReturn
from utils.funcs import die, getValue, handleExceptionIfAny, _print
from utils.parser import Repair
from handlers import createHandler, UMUHandler, WineHandler


class Parser(Repair):
    """
    Parse the applications files configuration from the my-apps directory and create Handler objects.
    """

    def __init__(self):
        super().__init__()

        self._application_data: List[Dict[str, str]] = [
            app_data for app_data in self._generateApplicationData(self.getProfilesPath())
        ]


    @staticmethod
    def _generateApplicationData(profiles_path: str) -> Generator[Dict[str, str], None, None]:
        """
        _generateApplicationData

        Creates a list of dictionary like objects with the applications' configuration file.
        It ignores configuration files with id "configuration_example" and malformed toml files.

        :profiles_path: Path to search for the application's profile configuration file.
        :return: A generator of possible application's configuration files.
        """

        files: Generator[str, None, None] = (
            path.join(profiles_path, f)
            for f in listdir(profiles_path)
            if path.isfile(path.join(profiles_path, f))
        )

        for file_path in files:
            with open(file_path, "rb") as fp:
                app_data: Dict[str, Any] = {}

                app_data = handleExceptionIfAny(
                    f"Failed to parse the profile's configuration file: {file_path}.\n" \
                    "Probably there's something wrong with the this toml file.",
                    True,
                    load,
                    fp
                )

                app_data = handleExceptionIfAny(
                    message = f"Didn't found the [profile] field in the profile's configuration file: {file_path}.",
                    fatal = True,
                    func = getValue,
                    data = app_data,
                    key="profile"
                )

                if not app_data: continue

                yield app_data


    def createHandlers(self, profile_id_arg: str, default_runner_arg: str | None = None) -> UMUHandler | WineHandler | None:
        """
        Run through my-apps directory and creates a Handler class objects from the configuration files.

        :profile_id_arg: Application's profile id.
        :default_runner_arg: (Optional) Default runner, defaults to None.
        :return: The handler that matches the application's profile id of type UMUHandler or WineHandler.
        """

        for app_data in self._application_data:
            profile_id: str | None = self._parseValue(app_data, "profile_id", str, fatal = True, expand_envars = False)

            # Skips the example configuration file
            if profile_id == "example_configuration_file" or profile_id != profile_id_arg: continue

            wine_directory: str | None = self._parseValue(app_data, "wine_directory", str)
            umu_run_path: str | None = self._parseValue(app_data, "umu_run_path", str)
            proton_directory: str | None = self._parseValue(app_data, "proton_directory", str)

            default_runner_cfg: str | None = self._parseValue(app_data, "default_runner", str)
            default_runner: str = default_runner_arg if default_runner_arg \
                else "umu" if default_runner_cfg == "umu" else "wine"

            debug: bool | None = self._parseValue(app_data, "debug", bool, True)
            debug_filepath: str | None = self._parseValue(app_data, "debug_filepath", str)
            application_directory: str | None = self._parseValue(app_data, "application_directory", str, fatal = True)
            environment_variables: Dict[str, str] | None = self._parseValue(
                app_data,
                "environment_variables",
                dict
            )
            executables_aliases: Dict[str, str] | None = self._parseValue(app_data, "executables_aliases", dict, {})

            tools: Dict[str, str] | None = self._parseValue(app_data, "tools", dict)
            tools = self._sanitizePaths(tools) if tools else tools
            dxvk_directory: str | None = self._parseValue(tools, "dxvk_directory", str)
            dxvk_nvapi_directory: str | None = self._parseValue(tools, "dxvk_nvapi_directory", str)
            winetricks_path: str | None = self._parseValue(tools, "winetricks_path", str)
            gallium_nine_directory: str | None = self._parseValue(tools, "gallium_nine_directory", str)

            handler: UMUHandler | WineHandler = createHandler(
                default_runner,
                profile_id,             # pyright: ignore[reportArgumentType]
                application_directory,  # pyright: ignore[reportArgumentType]
                executables_aliases,    # pyright: ignore[reportArgumentType]
                wine_directory,
                umu_run_path,
                proton_directory,
                environment_variables,
                debug,                  # pyright: ignore[reportArgumentType]
                debug_filepath,
                dxvk_directory,
                dxvk_nvapi_directory,
                winetricks_path,
                gallium_nine_directory
            )

            return handler


    @staticmethod
    def _sanitizePaths(_dict: Dict[Any, Any]) -> Dict[str, str]:
        """
        _sanitizePaths

        Sanitazes the paths so they have the format "key_string" = "value_string".

        :_dict: The dictionary that should be sanitized.
        :return: The sanitized dictionary.
        """

        sanitized_dict: Dict[str, str] = {}

        for k, v in _dict.items():
            # The key value shouldn't be other thing than a string, but just to be safe.
            if not isinstance(k, str):
                _print("Invalid pathing {k} = {v}. Ignored.")

                continue

            if not isinstance(v, str): v = str(v)

            sanitized_dict[k] = v

        return sanitized_dict


    @staticmethod
    def _expandDictionaryEnvironmentVariables(_dict: Dict[Any, Any]) -> Dict[str, str]:
        """
        _expandDictionaryEnvironmentVariables

        Expands environment variables the value strings if there's any.

        :_dict: dictionary.
        :return: the dictionary with expanded environment variables.
        """

        new_dict: Dict[str, str] = {}

        for k, v in _dict.items():
            new_dict[k] = path.expandvars(str(v))

        return new_dict


    def _parseValue(
        self,
        data: Dict[Any, Any] | None,
        key: str,
        expected_type: type,
        default: Any = None,
        fatal: bool = False,
        expand_envars: bool = True
    ) -> Any | None | NoReturn:
        """
        _parseValue

        Parses the dictionary data accordingly to the expected type,
        exiting the program if fatal is set to true and wrong type than the expected is feed.

        :data: Dictionary containing the data.
        :key: The key that should be looked up.
        :expected_type: The type this function is expecting to parse.
        :default: (Optional) Default value to be returned in case fatal is false.
        :fatal: (Optional) Tells if the program should quit in case of error, defaults to false.
        :expand_envars: (Optional) If string should expand envars, defaults to true.
        """

        value: Any | None = data.get(key) if data else None
        is_instance_type: bool = isinstance(value, expected_type)

        if isinstance(value, str) and expand_envars:
            value = path.expandvars(value)
        elif isinstance(value, dict) and expand_envars:
            value = self._sanitizePaths(value)
            value = self._expandDictionaryEnvironmentVariables(value)

        if value != None and is_instance_type:
            return value

        if value != None and not is_instance_type:
            die(f"Exepected a {expected_type} value for key \"{key}\" but \"{value}\" - \"{type(value)}\" was given.")

        if fatal:
            die(f"Tried parsing for key {key}: {key} not found!")

        return default


    def getAllIDs(self) -> Generator[str, None, None]:
        """
        getAllIDs

        Parse through all application's configuration files and get its ids.

        :return:
        """

        files: Generator[str, None, None] = (
            path.join(d, f) for d in self.getProfilesPath()
            for f in listdir(d)
            if path.isfile(path.join(d, f))
        )

        for file_path in files:
            with open(file_path, "rb") as fp:
                app_data: Dict[str, Any] = {}

                app_data = handleExceptionIfAny(
                    f"Failed to parse the profile's configuration file: {file_path}.\n" \
                    "Probably there's something wrong with the this toml file.",
                    False,
                    load,
                    fp
                )

                app_data = handleExceptionIfAny(
                    message = f"Didn't found the [profile] field in the profile's configuration file: {file_path}.",
                    fatal = False,
                    func = getValue,
                    data = app_data,
                    key = "profile"
                )

                if not app_data: continue

                profile_id: str | None = self._parseValue(app_data, "profile_id", str, fatal = False, expand_envars = False)

                # Skips the example configuration file
                if not profile_id or profile_id == "example_configuration_file": continue

                yield profile_id


    def listAliases(self, profile_id: str) -> str:
        """
        listAliases

        Lists all the aliases in the application's profile configuration file.

        :profile_id_arg: Application's profile id.
        :return: A string with all available executables aliases for the given profile id.
        """

        executables_aliases: Dict[str, str] | None = None

        for app_data in self._application_data:
            _profile_id: str | None = self._parseValue(app_data, "profile_id", str, fatal = False, expand_envars = False)

            # Skips the example configuration file
            if not _profile_id or _profile_id == "example_configuration_file": continue

            if _profile_id == profile_id:
                executables_aliases = self._parseValue(app_data, "executables_aliases", dict, {})

                break

        if not executables_aliases: return ""

        final_text: str = ""

        for k, v in executables_aliases.items():
            if not path.exists(v):
                continue

            final_text += f"{k}: {v}\n"

        return final_text[:-1]

