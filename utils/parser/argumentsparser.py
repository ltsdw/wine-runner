from argparse import ArgumentParser, ArgumentTypeError, ArgumentDefaultsHelpFormatter, Namespace
from typing import Any, Dict, Generator, List, Tuple


class WRArgumentParser(ArgumentParser):
    """
    A class that leverages from ArgumentParser while building a list of accepted arguments and flags
    and checking if the arguments are provided correctly.

    :formatter_class: Help message formatter which adds formatting to the help message,
                      defaults to ArgumentDefaultsHelpFormatter.
    :add_help: Tells where to enable/disable the help message.
    """

    def __init__(
        self,
        formatter_class: Any = ArgumentDefaultsHelpFormatter,
        add_help: bool = True
    ) -> None:
        super().__init__(
            prog = "wrunner",
            description = "Runs an application using UMU or Wine.",
            formatter_class = formatter_class,
            add_help = add_help
        )

        # ANY changes to these variables must be reflected also on utils/appsmanager/appsmanager.py
        # otherwise they won't have any effect.

        # Format is [ (nargs, name_of_the_arg, help) ]
        self._positional_args: List[Tuple[str | int, str, str]] = [
            (1, "profile_id", "Application's profile id.")
        ]

        _choices: Dict[str, str] = {
            "init": "Creates a WINE prefix if it doesn't exists or update an existent one.",
            "kill-all": "Kills wineserver.",
            "winecfg": "Calls winecfg.",
            "config": "Calls winecfg.",
            "cfg": "Calls winecfg.",
            "destroy-prefix": "Removes the WINE prefix and all its applications installed under the prefix.",
            "install-dxvk": "Installs DXVK.",
            "uninstall-dxvk": "Uninstall DXVK.",
            "install-dxvk-nvapi": "Installs DXVK NVAPI.",
            "uninstall-dxvk-nvapi": "Uninstall DXVK NVAPI.",
            "install-gallium-nine": "Installs Gallium Nine.",
            "uninstall-gallium-nine": "Uninstall Gallium Nine."
        }

        self._verb_help: str = "\n".join([f"{k}: {v}" for k, v in _choices.items()])

        # Format is { name_of_the_arg: (nargs, [choices], help) }
        self._optional_positional_args: Dict[str, Tuple[str | int, List[str], str]] = {
            "verb": # arg
            (
                "?", # nargs
                [key for key in _choices], # choices
                self._verb_help
            )
        }

        # Format is [ (nargs, [args_names], help, metaver) ]
        self._optional_args: List[Tuple[str | int, List[str], str, str | None]] = [
            ("*", ["--run"],                "Run the application.", "EXE_NAME ARGS"),
            ("*", ["--runinprefix"],        "Similar to --run, but run the application inside prefix." \
                                            "(While using WINE is the same as --run.)", "EXE_NAME ARGS"),
            ("*", ["--waitforexitandrun"],  "Similar to --run, but waits for wineserver shutdown." \
                                            "(While using WINE is the same as --run.)", "EXE_NAME ARGS"),
            ("*", ["-w", "--winetricks"],   "Installs dlls/apps inside the prefix.", "ARGS"),
            (0, ["--use-wine"],             "Overrides the default runners and runs the application using Wine.", None),
            (0, ["--use-umu"],              "Overrides the default runners and runs the application using UMU.", None),
            (0, ["--list-aliases"],         "Lists all executable aliases in the application's configuration file.", None)
        ]

        # Format is [ (nargs, [args_names], help, metaver) ]
        self._pre_optional_args: List[Tuple[str | int, List[str], str, str | None]] = [
            (0, ["--show-ids"],             "Displays all application's profile ids.", None),
            (0, ["--show-verbs"],           "Displays all verbs and its description.", None),
            (0, ["--show-optional-args"],   "Displays all verbs and its description.", None),
        ]


    def compilePreArgumentsParser(self) -> None:
        """
        compilePreArgumentsParser

        These are pre compiled and should take precedence when using with parse_known_args,
        if they aren't provided then compilePosArgumentsParser takes precedence,
        this should be used before compilePosArgumentsParser and used in conjunction with
        parse_known_args.

        :return:
        """

        for arg in self._pre_optional_args:
            if arg[0] == 0:
                self.add_argument(*arg[1], action = "store_true", help = arg[2])

                continue

            self.add_argument(*arg[1], nargs = arg[0], help = arg[2], metavar = arg[3])


    def compilePosArgumentsParser(self) -> None:
        """
        compilePosArgumentsParser

        Configures the ArgumentParser object, defining its input format and behavior and return it to the caller.

        :return:
        """

        for arg in self._positional_args:
            self.add_argument(arg[1], nargs = arg[0], help = arg[2])

        for arg_name, arg in self._optional_positional_args.items():
            self.add_argument(arg_name, nargs = arg[0], choices = arg[1], help = arg[2])

        for arg in self._optional_args:
            if arg[0] == 0:
                self.add_argument(*arg[1], action = "store_true", help = arg[2])

                continue

            self.add_argument(*arg[1], nargs = arg[0], help=arg[2], metavar = arg[3])


    def positionalArgumentsCheck(self, namespace: Namespace) -> None:
        """
        positionalArgumentsCheck

        Checks if any of the optional was provided arguments.
        Will raise an ArgumentTypeError exception if no positional was provided.

        :namespace: Simple object that stores ArgumentParser attributes.
        :return:
        """

        if not any(vars(namespace)[key] != None for key in vars(namespace)):
            raise ArgumentTypeError("At least one positional argument must be provided.")


    def getNextOptArg(self, namespace: Namespace) -> Any | None:
        """
        getNextOptArg

        Gets the next optional argument that isn't None.

        :namepsace: Simple object that stores ArgumentParser attributes.
        :return: The parameter of the non-None argument.
        """

        generator: Generator[str, None, None] = (arg[1] for arg in self._positional_args)
        for key, value in vars(namespace).items():
            if value != None and key not in generator and value not in generator:
                return value


    def getVerbHelp(self) -> str:
        """
        getVerbHelp

        :return: The help message for the verb positional argument.
        """

        return self._verb_help


    def getOptionalArgumentHelp(self) -> str:
        """
        getOptionalArgumentHelp

        :return: The help messages for all optional arguments.
        """

        final_text: str = ""

        for arg in self._optional_args:
            for _arg in arg[1]:
                final_text += f"{_arg}: {arg[2]}\n"

        return final_text[:-1]

