from os import chdir, path, mkdir, rename, remove
from typing import List, Dict
from utils.funcs import die, getPackageUrl, findFiles, _print
from utils.downloader import Downloader
from handlers import BaseHandler
from shutil import copy


class WineHandler(BaseHandler):
    """
    WineHelper

    :profile_id: Application's profile id.
    :wine_directory: Path to the wine's bin directory.
    :application_directory: Path to the directory where the application's prefix will be created.
    :executables_aliases: Dictionary of format { "executable_aliase" : "/path/to/the/exectuable" }.
    :environment_variables: The environment variables to be used within wine's environment.
    :debug: Tell whether should display logs.
    :debug_filepath: Path to the file where logs should be saved if debug is set to true.
    :dxvk_directory: Path to DXVK directory.
    :dxvk_nvapi_directory: Path to DXVK NVAPI.
    :winetricks_path: Path to winetricks.
    :gallium_nine_directory: Path to gallium nine directory.
    """

    def __init__(
        self,
        profile_id: str,
        wine_directory: str | None,
        application_directory: str,
        executables_aliases: Dict[str, str],
        environment_variables: Dict[str, str] | None = None,
        debug: bool = False,
        debug_filepath: str | None = None,
        dxvk_directory: str | None = None,
        dxvk_nvapi_directory: str | None = None,
        winetricks_path: str | None = None,
        gallium_nine_directory : str | None = None
    ):
        self._wine_directory: str | None        = wine_directory

        if not self._wine_directory:
            self._wine_directory = "/usr/bin"

        self._prefix: str                       = path.join(application_directory, "pfx")
        self._debug: bool                       = debug
        self._debug_filepath: str | None        = debug_filepath
        self._dxvk_directory: str | None        = dxvk_directory
        self._dxvk_nvapi_directory: str | None  = dxvk_nvapi_directory
        self._winetricks_path: str | None       = winetricks_path
        self._gallium_nine_directory: str | None= gallium_nine_directory
        self._system32_dir: str                 = path.join(self._prefix, "drive_c/windows/system32")
        self._syswow64_dir: str                 = path.join(self._prefix, "drive_c/windows/syswow64")

        super().__init__(
            profile_id,
            path.join(self._wine_directory, "wine"),
            path.join(self._wine_directory, "wine64"),
            application_directory,
            self.wine,
            executables_aliases,
            environment_variables,
            self._debug,
            self._debug_filepath
        )


    def wine(self, mode: str = "waitforexitandrun", args: List[str] | None = None) -> None:
        """
        Run the program with wine.

        :mode: The mode that should be used, defaults to waitforexitandrun (on wine does nothing).
        :args: A list with the program and its arguments.
        :return:
        """

        _args: List[str] = args if args else ["--help"]
        _: str = mode

        self.runCommand([self.getDefaultWinePath(), *_args], self._debug, self._debug_filepath)


    def wineboot(self, args: List[str] | None = None) -> None:
        """
        wineboot

        Runs wineboot

        :args: (Optional) List of arguments.
        :return:
        """

        _args: List[str] = args if args else ["--help"]

        self.runCommand([self.getDefaultWinePath(), "wineboot", *_args], True)


    def killAll(self) -> None:
        """
        killAll

        Calls wineboot with --kill flag.

        :return:
        """

        self.runCommand([self.getDefaultWinePath(), "wineboot", "--kill"], True)


    def initWinePrefix(self) -> None:
        """
        Setups a new prefix.

        :return:
        """

        _print("Initiating prefix.")

        if not path.exists(self._application_directory):
            mkdir(self._application_directory)

        self.wineboot(["--init"])

        _print("Prefix creted.")


    @staticmethod
    def _download(url: str, directory: str) -> str:
        """
        _download

        Downloads a packages from Github and extract them to the Wine Runner data directory.

        :url: Latest url release of the project.
        :directory: A relative directory to the Wine Runner data directory.
        :return: The path where the package was extracted to.
        """

        package_url: str = getPackageUrl(url)
        downloader: Downloader = Downloader(package_url, directory)
        downloader.download()

        return downloader.extract()


    def installDXVK(self) -> None:
        """
        Install DXVK.

        :return:
        """

        if not self._dxvk_directory or not path.exists(self._dxvk_directory):
            self._dxvk_directory = self._download("https://github.com/doitsujin/dxvk/releases/latest", "dxvk")

        if not self._dxvk_directory or not path.exists(self._dxvk_directory):
            die(f"DXVK directory not found at: {self._dxvk_directory}.")

        chdir(self._dxvk_directory)

        dxvk_dlls: List[str] = ["d3d10core.dll", "d3d11.dll", "d3d9.dll", "dxgi.dll"]
        x32_dir: str = path.join(self._dxvk_directory, "x32")
        x64_dir: str = path.join(self._dxvk_directory, "x64")

        if not path.exists(x32_dir) or not path.exists(x64_dir):
            die(f"DXVK x32 or x64 directory not found at: {self._dxvk_directory}.")

        dlls_x32: List[str] = [path.join(x32_dir, file) for file in dxvk_dlls]
        dlls_x64: List[str] = [path.join(x64_dir, file) for file in dxvk_dlls]

        if not all(path.exists(dll) for dll in dlls_x32) or not all(path.exists(dll) for dll in dlls_x64):
            die(f"Some or all DXVK dlls are missing: {self._dxvk_directory}.")

        if not path.exists(self._system32_dir) and not path.exists(self._syswow64_dir):
            die(f"The directories system32 and syswow64 were not found in prefix: {self._prefix}.")

        _print("Installing DXVK.")

        status_code: int = self.runCommandStatusChecked([self.getWine64Path(), "winepath"])

        if status_code != 0:
             for dll in dlls_x32:
                _print(f"{dll} -> {self._system32_dir}")
                copy(dll, self._system32_dir)
                self.reg(path.splitext(path.basename(dll))[0], "add", "native")
                _print("DXVK installed.")

                return

        for dll in dlls_x32:
            _print(f"{dll} -> {self._syswow64_dir}")
            copy(dll, self._syswow64_dir)
            self.reg(path.splitext(path.basename(dll))[0], "add", "native")

        for dll in dlls_x64:
            _print(f"{dll} -> {self._system32_dir}")
            copy(dll, self._system32_dir)
            self.reg(path.splitext(path.basename(dll))[0], "add", "native")

        _print("DXVK installed.")


    def uninstallDXVK(self) -> None:
        """
        Uninstall DXVK.

        :return:
        """

        dxvk_dlls: List[str] = ["d3d10core.dll", "d3d11.dll", "d3d9.dll", "dxgi.dll"]
        system32_dlls: List[str] = [path.join(self._system32_dir, file) for file in dxvk_dlls]
        syswow64_dlls: List[str] = [path.join(self._syswow64_dir, file) for file in dxvk_dlls]

        _print("Uninstalling DXVK.")

        for dll in dxvk_dlls:
            self.reg(path.splitext(dll)[0], "delete")

        for dll in system32_dlls:
            if not path.exists(dll): continue

            _print(f"Removed: {dll}")
            remove(dll)

        for dll in syswow64_dlls:
            if not path.exists(dll): continue

            _print(f"Removed: {dll}")
            remove(dll)

        self.wineboot(["-u"])
        _print("DXVK uninstalled.")


    def _installNVNGX(self) -> None:
        """
        _installNVNGX

        Try to find the NVNGX dlls of nvidia.

        :return:
        """

        lib_directory: str = "/usr/lib"
        nvngx_dlls: List[str] = [f for f in findFiles(lib_directory, ["_nvngx.dll", "nvngx.dll"])]

        if not nvngx_dlls: die(f"NVNGX dlls not found at: {nvngx_dlls}")

        if not path.exists(self._system32_dir): die(f"The directory system32 not found in prefix: {self._prefix}.")

        for dll in nvngx_dlls:
            copy(dll, self._system32_dir)
            _print(f"{dll} -> {self._system32_dir}")
            self.reg(path.splitext(path.basename(dll))[0], "add", "native")


    def _uninstallNVNGX(self) -> None:
        """
        _uninstallNVNGX

        Uninstall NVNGX from the prefix.

        :return:
        """

        nvngx_dlls: List[str] = [path.join(self._system32_dir, f) for f in ["_nvngx.dll", "nvngx.dll"]]

        _print("Uninstalling NVNGX.")

        for dll in nvngx_dlls:
            if not path.exists(dll): continue

            remove(dll)
            _print(f"Removed: {dll}")
            self.reg(path.splitext(path.basename(dll))[0], "delete")

        _print("NVNGX uninstalled.")


    def installDXVKNVAPI(self) -> None:
        """
        installDXVKNVAPI

        Install DXVK NVAPI.

        :return:
        """

        if not self._dxvk_nvapi_directory or not path.exists(self._dxvk_nvapi_directory):
            self._dxvk_nvapi_directory = self._download("https://github.com/jp7677/dxvk-nvapi/releases/latest", "dxvk-nvapi")

        if not self._dxvk_nvapi_directory or not path.exists(self._dxvk_nvapi_directory):
            die(f"DXVK directory not found at: {self._dxvk_nvapi_directory}.")

        status_code: int = self.runCommandStatusChecked([self.getWine64Path(), "winepath"])
        dxvk_dlls: List[str] = ["d3d10core.dll", "d3d11.dll", "d3d9.dll", "dxgi.dll"]

        if status_code != 0 and not all(path.exists(path.join(self._system32_dir, dll)) for dll in dxvk_dlls):
            _print("DXVK NVAPI needs DXVK to be installed first, installing DXVK.")
            self.installDXVK()
        elif status_code == 0 and not all(path.exists(path.join(self._syswow64_dir, dll)) for dll in dxvk_dlls) \
        or status_code == 0 and not all(path.exists(path.join(self._system32_dir, dll)) for dll in dxvk_dlls):
            _print("DXVK NVAPI needs DXVK to be installed first, installing DXVK.")
            self.installDXVK()

        chdir(self._dxvk_nvapi_directory)

        x32_dir: str = path.join(self._dxvk_nvapi_directory, "x32")
        x64_dir: str = path.join(self._dxvk_nvapi_directory, "x64")

        if not path.exists(x32_dir) or not path.exists(x64_dir):
            die(f"DXVK x32 or x64 directory not found at: {self._dxvk_nvapi_directory}.")

        dll_x32: str = path.join(x32_dir, "nvapi.dll")
        dll_x64: str = path.join(x64_dir, "nvapi64.dll")

        if not path.exists(dll_x32) or not path.exists(dll_x64):
            die(f"Some or all DXVK dlls are missing: {self._dxvk_nvapi_directory}.")

        if not path.exists(self._system32_dir) and not path.exists(self._syswow64_dir):
            die(f"The directories system32 and syswow64 were not found in prefix: {self._prefix}.")

        _print("Installing DXVK NVAPI.")

        self._installNVNGX()

        if status_code != 0:
            copy(dll_x32, self._system32_dir)
            _print(f"{dll_x32} -> {self._system32_dir}")
            self.reg(path.splitext(path.basename(dll_x32))[0], "add", "native")
            _print("DXVK NVAPI installed.")

            return

        copy(dll_x32, self._syswow64_dir)
        _print(f"{dll_x32} -> {self._syswow64_dir}")
        self.reg(path.splitext(path.basename(dll_x32))[0], "add", "native")

        copy(dll_x64, self._system32_dir)
        _print(f"{dll_x64} -> {self._system32_dir}")
        self.reg(path.splitext(path.basename(dll_x64))[0], "add", "native")

        _print("DXVK NVAPI installed.")


    def uninstallDXVKNVAPI(self) -> None:
        """
        uninstallDXVKNVAPI

        Uninstall DXVK NVAPI.

        :return:
        """

        status_code: int = self.runCommandStatusChecked([self.getWine64Path(), "winepath"])
        system32_dll: str = path.join(self._system32_dir, "nvapi64.dll" if status_code == 0 else "nvapi.dll")
        syswow64_dll: str = path.join(self._syswow64_dir, "nvapi.dll")

        _print("Uninstalling DXVK NVAPI.")

        if path.exists(system32_dll):
            _print(f"Removed: {system32_dll}")
            remove(system32_dll)

        if path.exists(syswow64_dll):
            _print(f"Removed: {syswow64_dll}")
            remove(syswow64_dll)

        self.reg("nvapi64", "delete")
        self.reg("nvapi", "delete")

        self._uninstallNVNGX()
        self.wineboot(["-u"])
        _print("DXVK NVAPI uninstalled.")


    def installGalliumNine(self) -> None:
        """
        installGalliumNine

        Install gallium nine.

        :return:
        """

        if not self._gallium_nine_directory or not path.exists(self._gallium_nine_directory):
            self._gallium_nine_directory = self._download("https://github.com/iXit/wine-nine-standalone/releases", "gallium-nine")

        if not self._gallium_nine_directory or not path.exists(self._gallium_nine_directory):
            die(f"Gallium Nine directory not found at: {self._gallium_nine_directory}.")

        ninewinecfg_32: str = path.join(self._gallium_nine_directory, "bin32/ninewinecfg.exe.so")
        d3d9_32: str = path.join(self._gallium_nine_directory, "lib32/d3d9-nine.dll.so")

        ninewinecfg_64: str = path.join(self._gallium_nine_directory, "bin64/ninewinecfg.exe.so")
        d3d9_64: str = path.join(self._gallium_nine_directory, "lib64/d3d9-nine.dll.so")

        if not path.exists(self._system32_dir) and not path.exists(self._syswow64_dir):
            die(f"The directories system32 and syswow64 were not found in prefix: {self._prefix}.")

        if not all(path.exists(file) for file in [ninewinecfg_32, ninewinecfg_64, d3d9_32, d3d9_64]):
            die(f"Some or all Gallium Nine dlls are missing: {self._gallium_nine_directory}.")

        status_code: int = self.runCommandStatusChecked([self.getWine64Path(), "winepath"])

        _print("Installing Gallium Nine.")

        if status_code != 0:
            _print(f"{ninewinecfg_32} -> {self._system32_dir}")
            copy(ninewinecfg_32, path.join(self._system32_dir, "ninewinecfg.exe"))
            _print(f"{d3d9_32} -> {self._system32_dir}")
            copy(d3d9_32, path.join(self._system32_dir, "d3d9-nine.dll"))
            self.runCommand([self.getWinePath(), "ninewinecfg.exe", "-e"])
            _print("Gallium Nine installed.")

            return

        _print(f"{ninewinecfg_32} -> {self._syswow64_dir}")
        copy(ninewinecfg_32, path.join(self._syswow64_dir, "ninewinecfg.exe"))
        _print(f"{d3d9_32} -> {self._syswow64_dir}")
        copy(d3d9_32, path.join(self._syswow64_dir, "d3d9-nine.dll"))

        _print(f"{ninewinecfg_64} -> {self._system32_dir}")
        copy(ninewinecfg_64, path.join(self._system32_dir, "ninewinecfg.exe"))
        _print(f"{d3d9_64} -> {self._system32_dir}")
        copy(d3d9_64, path.join(self._system32_dir, "d3d9-nine.dll"))
        self.runCommand([self.getWine64Path(), "ninewinecfg.exe", "-e"])

        _print("Gallium Nine installed.")


    def uninstallGalliumNine(self) -> None:
        """
        Uninstall gallium nine.

        :return:
        """

        self.runCommand([self.getDefaultWinePath(), "ninewinecfg.exe", "-d"])

        files_to_rename: List[str] = [
            path.join(self._system32_dir, "d3d9-nine.bak"),
            path.join(self._syswow64_dir, "d3d9-nine.bak")
        ]

        files_to_remove: List[str] = [
            path.join(self._system32_dir, "d3d9-nine.dll"),
            path.join(self._system32_dir, "ninewinecfg.exe"),
            path.join(self._syswow64_dir, "d3d9-nine.dll"),
            path.join(self._syswow64_dir, "ninewinecfg.exe"),
        ]

        _print("Uninstalling Gallium Nine.")

        for f in files_to_rename:
            if path.exists(f):
                new_name: str = path.join(path.dirname(f), "d3d9.dll")
                rename(f, new_name)
                _print(f"Renamed file: {f} -> {new_name}")

        for f in files_to_remove:
            if path.exists(f):
                remove(f)
                _print(f"Removed file: {f}")

        _print("Gallium Nine Uninstalled.")


    def winetricks(self, args: List[str] | None = None) -> None:
        """
        Install stuffs with winetricks.

        :args: list of things to install.
        :return:
        """

        if not self._winetricks_path or not path.exists(self._winetricks_path):
            die(f"Winetricks not found at: {self._winetricks_path}")

        if not args:
            self.runCommand([self._winetricks_path, "--help"], self._debug)

            return

        self.runCommand([self._winetricks_path, *args], self._debug, self._debug_filepath)


    def getWinePath(self) -> str:
        """
        getWinePath

        Gets the wine binary path.

        :return: The path to the wine binary or throw in case it's not provided.
        """

        if not self._wine_bin_path:
            raise TypeError(f"Wine binary path is empty.")

        return self._wine_bin_path


    def getWine64Path(self) -> str:
        """
        getWine64Path

        Gets the wine64 binary path.

        :return: The path to the wine64 binary or throw in case it's not provided.
        """

        if not self._wine64_bin_path:
            raise TypeError(f"Wine64 binary path is empty.")

        return self._wine64_bin_path


    def getDefaultWinePath(self) -> str:
        """
        getDefaultWinePath

        Gets the default default wine being used.

        :return: The path to the default wine or None in case umu is being used.
        """

        if not self._default_wine_path:
            raise TypeError(f"Wine binary path is empty.")

        return self._default_wine_path


    def winecfg(self) -> None:
        """
        winecfg

        Runs wine configuration.

        :return:
        """

        self.runCommand([self.getDefaultWinePath(), "winecfg"], self._debug, self._debug_filepath)
