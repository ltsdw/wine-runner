from typing import Any, Callable, Dict, List, NoReturn
from utils.funcs import die
from utils.parser import Parser
from utils.parser import ArgumentTypeError, Namespace, WRArgumentParser, RawTextHelpFormatter
from handlers import UMUHandler, WineHandler


class ProfilesManager(Parser):
    """
    Manages the profiles of the applications creating the appropriate handler.

    :_argv: List of arguments.
    """

    def __init__(self):
        super().__init__()

        self._namespace: Namespace
        self._remainder: List[str]

        # Configure the arguments parser.
        self._wr_arg_parser: WRArgumentParser = WRArgumentParser(add_help=False)

        self._wr_arg_parser.compilePreArgumentsParser()

        self._namespace, self._remainder = self._wr_arg_parser.parse_known_args()

        # Check if any pre argument was provided
        self._preArgumentParse()

        # If not, parse the rest of the arguments
        self._wr_arg_parser = WRArgumentParser(formatter_class = RawTextHelpFormatter)

        self._wr_arg_parser.compilePosArgumentsParser()

        self._namespace = self._wr_arg_parser.parse_args(self._remainder)

        # Check if at least one optional was provied.
        try:
            self._wr_arg_parser.positionalArgumentsCheck(self._namespace)
        except ArgumentTypeError as e:
            self._wr_arg_parser.print_help()
            die(f"Error: {e}")

        # Only at this stage that the profile id is available
        self._profileIdFunctions()

        handler: UMUHandler | WineHandler = self._getHandler()

        self._mapped_functions: Dict[str, Callable[..., Any]] = self._createMappedFunctions(handler, self._namespace)

        try:
            # Call the mapped function if any argument provided is currently mapped
            self._callMappedFunction()
        except NotImplementedError as e:
            die(f"Function not implemented for this kind of handler, nothing done.\n{e}")


    @staticmethod
    def _createMappedFunctions(
        handler: UMUHandler | WineHandler,
        namespace: Namespace
    ) -> Dict[str, Callable[..., Any]]:
        """
        _createMappedFunctions

        :handler: UMUHandler or WineHandler.
        :namespace: Simple object for storing arguments
        :return: A dictionary of mapped functions
        """

        mapped_functions: Dict[str, Callable[..., Any]] = {
            "init": handler.initWinePrefix,
            "kill-all": handler.killAll,
            "init": handler.initWinePrefix,
            "winecfg": handler.winecfg,
            "config": handler.winecfg,
            "cfg": handler.winecfg,
            "delete": handler.destroyPrefix,
            "destroy-prefix": handler.destroyPrefix,
            "--winetricks": lambda args: handler.winetricks(args),
            "install-dxvk": handler.installDXVK,
            "uninstall-dxvk": handler.uninstallDXVK,
            "install-dxvk-nvapi": handler.installDXVKNVAPI,
            "uninstall-dxvk-nvapi": handler.uninstallDXVKNVAPI,
            "install-gallium-nine": handler.installGalliumNine,
            "uninstall-gallium-nine": handler.uninstallGalliumNine,
            "--run": lambda args = None: \
                handler.runExe("run", args) \
                if namespace.run else handler.runExe(mode="run"),

            "--runinprefix": lambda args = None: \
                handler.runExe("runinprefix", args) \
                if namespace.runinprefix else handler.runExe(mode="runinprefix"),

            "--waitforexitandrun": lambda args = None: \
                handler.runExe("waitforexitandrun", args) \
                if namespace.waitforexitandrun else handler.runExe(mode="waitforexitandrun"),
        }

        return mapped_functions


    def _profileIdFunctions(self) -> None | NoReturn:
        """
        _profileIdFunctions

        Call functions that need the application's profile id to work.

        :return:
        """

        profile_id: str = self._namespace.profile_id[0]

        if self._namespace.list_aliases: die(self.listAliases(profile_id), 0)


    def _preArgumentParse(self) -> None | NoReturn:
        """
        _checkArgumentParse

        Do arguments checking and parse it.

        :return:
        """

        if self._namespace.show_ids: die(f"{' '.join(self.getAllIDs())}", 0)
        if self._namespace.show_verbs: die(f"{self._wr_arg_parser.getVerbHelp()}", 0)
        if self._namespace.show_optional_args: die(f"{self._wr_arg_parser.getOptionalArgumentHelp()}", 0)


    def _callMappedFunction(self) -> None:
        """
        Calls the function mapped to the verb.

        :return:
        """

        verb: str | None = self._namespace.verb
        run: List[str] | None = self._namespace.run
        runinprefix: List[str] | None = self._namespace.runinprefix
        waitforexitandrun: List[str] | None = self._namespace.waitforexitandrun
        winetricks: List[str] | None = self._namespace.winetricks

        if verb != None:
            self._mapped_functions[verb]()

            return

        if run != None:
            self._mapped_functions["--run"](run)

            return

        if runinprefix != None:
            self._mapped_functions["--runinprefix"](runinprefix)

            return

        if self._namespace.waitforexitandrun != None:
            self._mapped_functions["--waitforexitandrun"](waitforexitandrun)

            return

        if winetricks != None:
            self._mapped_functions["--winetricks"](winetricks)

            return


    def _getHandler(self) -> UMUHandler | WineHandler:
        """
        Look up for the id of the application and its respective handler.

        :return: Return the Application if found, or exit otherwise.
        """

        profile_id: str = self._namespace.profile_id[0]

        if self._namespace.use_wine and self._namespace.use_umu:
            die("Two override runner were specified, choose only one.")

        default_runner: str | None = None if not self._namespace.use_wine and not self._namespace.use_umu \
            else "wine" if self._namespace.use_wine else "umu"

        handler: UMUHandler | WineHandler | None = self.createHandlers(profile_id, default_runner)

        return handler if handler else die(f"Application with profile id \"{profile_id}\" not found.")

