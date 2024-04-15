from os import environ, makedirs, chdir, path
from urllib.request import Request, urlopen
from http.client import HTTPResponse
from typing import Any, Dict, List
from email.message import Message
from tarfile import open as topen
from tarfile import TarInfo
from utils.funcs import die, _print, removeExtentions


class Downloader:
    """
    Downloader

    Simple class that downloads a file to a path.

    :url: Url of the file to be downloaded.
    :directory: Relative path to where the file should be saved.
    """

    def __init__(self, url: str, directory: str):
        self._url: str = url
        self._download_directory: str
        _data_directory: str | None = environ.get("WRUNNER_DATA_DIR")

        try:
            _data_directory = _data_directory if _data_directory \
            else path.join(environ["XDG_DATA_HOME"], "wine-runner/downloads")
        except KeyError:
            _data_directory = path.join(environ["HOME"], ".local/share/wine-runner/downloads")

        self._download_directory = path.join(_data_directory, directory)

        if not path.exists(self._download_directory):
            makedirs(self._download_directory)

        chdir(self._download_directory)

        headers: Dict[str, str] = {
            "User-Agent": "Mozilla/5.0"
        }

        self._request: Request = Request(self._url, headers=headers)

        try:
            self._response: HTTPResponse = urlopen(self._request, timeout=30)
        except Exception as e:
            die(f"Failed to make a request to the url: {url}.\nError: {e}")

        if self._response.getcode() != 200: die("Failed to fetch download information.")

        content_dispositon: str | None = self._response.headers["Content-Disposition"]
        content_dispositon = content_dispositon if content_dispositon else 'Content-Disposition: attachment; filename=unknown.tar.gz'
        msg: Message = Message()
        msg.add_header("Content-Disposition", content_dispositon)
        _filename: str | None = msg.get_filename()
        self._filename: str = _filename if _filename else die("Couldn't retrieve filename!")
        self._filepath: str = path.join(self._download_directory, self._filename)


    def getFileSize(self) -> int | None:
        """
        getFileSize

        Checks the size of the file.

        :return:
        """

        content_length: str | None = self._response.headers["Content-Length"]

        return int(content_length) if content_length else None


    def download(self) -> None:
        """
        download

        Downloads the file.

        :return:
        """

        if path.exists(self._filepath) and path.getsize(self._filepath) == self.getFileSize(): return

        _print(f"Downloading {self._filename}")

        with open(self._filepath, "wb") as f:
            f.write(self._response.read())

        _print(f"Download complete.")


    @staticmethod
    def _tarfileHasRootDirectory(members: List[TarInfo]) -> bool:
        """
        _tarfileHasRootDirectory

        Tells where the names are within a common high-level directory.
        Paths must be in the order they appear.

        :names: List of TarInfo objects.
        :return: True if there's a single high-level directory for all other paths within the members.
        """

        return members[0].isdir() and path.commonpath([m.name for m in members]) == members[0].name if members else False


    def extract(self) -> str:
        """
        extract

        Extracts the downloaded file.

        :return: The path where the package was extracted to.
        """

        with topen(self._filepath, "r:gz") as f:
            dirname: str = removeExtentions(self._filename, 2)
            members: List[TarInfo] = f.getmembers()

            _print(f"Extracting {self._filename} to {self._download_directory}")
            if not self._tarfileHasRootDirectory(f.getmembers()):
                makedirs(dirname, exist_ok = True)
                f.extractall(dirname)
                _print(f"File extraction completed.")

                return path.join(self._download_directory, dirname)

            dirname = members[0].name if members else ""

            f.extractall(self._download_directory)
            _print(f"File extraction completed.")

            return path.join(self._download_directory, dirname) if dirname else self._download_directory

