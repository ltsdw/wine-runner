from typing import List
from Utils.Funcs import die
from Utils.Parser import Parser
from Utils.App import App


class AppsManager(Parser):
    def __init__(self, _argv: List[str]):
        """
        Parse the arguments.
        """


        super().__init__()


        try:
            self.id: str = _argv[1]
        except IndexError:
            die("You must specify the id of which application should be runned.")


        try:
            self.verb: str | None = _argv[2]
        except IndexError:
            self.verb = None


        try:
            self.args: List[str] | None = _argv[3:]
        except IndexError:
            self.args = None


        self.app: App = self._getApp()


        if self.verb == "--init" or self.verb == "init":
            self.app.initWinePrefix()
        elif (
            self.verb == "winecfg"
            or self.verb == "config"
            or self.verb == "cfg"
        ):
            self.app.winecfg()
        elif self.verb == "winetricks" or self.verb == "wt":
            self.app.winetricks(self.args)
        elif (
            self.verb == "dxvk"
            or self.verb == "install_dxvk"
            or self.verb == "installdxvk"
        ):
            self.app.installDXVK()
        elif (
            self.verb == "unidxvk"
            or self.verb == "uninstall_dxvk"
            or self.verb == "uninstalldxvk"
        ):
            self.app.uninstallDXVK()
        elif (
            self.verb == "nine"
            or self.verb == "installnine"
            or self.verb == "install_gallium_nine"
            or self.verb == "installgalliumnine"
        ):
            self.app.installGalliumNine()
        elif (
            self.verb == "ninecfg"
            or self.verb == "gallium_nine_config"
            or self.verb == "galliumnineconfig"
        ):
            self.app.galliumNineConfig()
        elif (
            self.verb == "uninine"
            or self.verb == "uninstall_gallium_nine"
            or self.verb == "uninstallgalliumnine"
        ):
            self.app.uninstallGalliumNine()
        elif (
            self.verb == "delete"
            or self.verb == "remove"
            or self.verb == "remove_prefix"
            or self.verb == "removeprefix"
            or self.verb == "uninstall"
        ):
            self.app.removePrefix()
        else:
            if self.verb:
                self.app.runExe(self.verb, self.args)
            else:
                self.app.runExe()


    def _getApp(self) -> App:
        """
        Searchs for the app.

        :return: Return the Application if found, or exit otherwise.
        """


        for _app in self.createModels():
            if _app.getId() == self.id:
                _app.createApp()

                return _app

        die(f"Application for id {self.id} not found.")

