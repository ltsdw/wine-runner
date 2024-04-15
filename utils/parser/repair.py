from os import path, mkdir, makedirs, environ


class Repair:
    """
    Sets up the configuration directory and files.
    """

    def __init__(self):
        config_example_filename: str = "example_profile_config"
        minimal_example_filename: str = "minimal_example_profile_config"
        self._config_dir: str | None = environ.get("WRUNNER_CONFIG_DIR")

        try:
            self._config_dir = self._config_dir if self._config_dir else path.join(environ["XDG_CONFIG_HOME"], "wine-runner")
        except KeyError:
            self._config_dir = path.join(environ["HOME"], ".config/wine-runner")

        if not path.exists(self._config_dir):
            makedirs(self._config_dir)

        self._config_profiles_dir: str = path.join(self._config_dir, "profiles")

        if not path.exists(self._config_profiles_dir):
            mkdir(self._config_profiles_dir)

        examples_path: str = path.dirname(path.abspath(__file__))

        config_example_filepath = path.join(self._config_profiles_dir, config_example_filename)
        minimal_example_filepath = path.join(self._config_profiles_dir, minimal_example_filename)

        if not path.exists(config_example_filepath):
            with open(path.join(examples_path, "examples/example_profile_config"), "r") as fp:
                content: str = fp.read()

            with open(config_example_filepath, "w") as fp:
                fp.write(content)

        if not path.exists(minimal_example_filepath):
            with open(path.join(examples_path, "examples/minimal_example_profile_config"), "r") as fp:
                content = fp.read()

            with open(minimal_example_filepath, "w") as fp:
                fp.write(content)

        environ["WRUNNER_CONFIG_DIR"] = self._config_dir
        environ["WRUNNER_PROFILES_DIR"] = self._config_profiles_dir


    def getProfilesPath(self) -> str:
        """
        getProfilesPath

        :return: the path the application's json configuration files.
        """

        return self._config_profiles_dir

