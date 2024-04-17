from typing import Any, Callable, Dict, List, Generator, NoReturn, TextIO, Union
from sys import stderr, stdout
from os import environ, path, scandir
from tarfile import TarInfo
from utils.basichtmlparser import BasicHtmlParser
from urllib.request import Request, urlopen


def _print(msg: str, fs: TextIO = stdout, end: str = '\n') -> None:
    """
    _print

    Prints a message.

    :msg: The message to be displayed.
    :fs: Uses stdout by default.
    :end: Last character to be append to the final of the message, defaults to '\n'.
    :return:
    """

    if not msg: return

    fs.write(msg + end)
    fs.flush()


def die(msg: str, exit_code: int = -1) -> NoReturn:
    """
    die

    Prints a message and exits.

    :msg: The message to be displayed.
    :exit_code: The exit code that should be used, defaults to -1 indicating an error.
    :return:
    """

    fs: TextIO = stdout if not exit_code else stderr

    _print(msg, fs) if msg else exit(exit_code)
    exit(exit_code)


def handleExceptionIfAny(message: str, fatal: bool, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    handleExceptionIfAny

    Calls the callable function and return its value if any handling any exception that may happen.

    :message: Message to be displayed in case of an exception is raised.
    :fatal: If it's True, the program will exit in case any exception is raised.
    :func: The callable function which may raise an exception.
    :args: Positional arguments to be passed to the callable function.
    :kwargs: Keyword arguments to be passed to the callable function.
    :return: If no exception is raised, the return value of the callable function is returned.
    """

    fatal_handler: Callable[[str], Union[NoReturn, None]] = die if fatal else _print

    try:
        return func(*args, **kwargs)
    except Exception as e:
        fatal_handler(f"{message}: {e}.")


def getValue(data: Any, key: Any) -> Any:
    """
    getValue

    Get the value from the container or raise an exception.

    :data: List, dictionary, etc.
    :key: Its index, hashkey, key, etc.
    :return: The value if no exception is raised.
    """

    try:
        return data[key]
    except Exception as e:
        raise e


def negate(value: int | bool) -> int:
    """
    negate

    Negastes a number or a boolean.
    If it's a non-zero number it becomes zero and vice-versa.

    :value: The number or boolean to be negated.
    :return: The negated value as an integer.
    """

    return int(not bool(value))


def negateBool(value: int | bool) -> bool:
    """
    negateBool

    Negastes a number or a boolean.
    If it's a non-zero number it becomes zero and vice-versa.

    :value: The number or boolean to be negated.
    :return: The negated value as a boolean.
    """

    return bool(negate(value))


def findFiles(path: str, patterns: List[str]) -> Generator[str, None, None]:
    """
    findFiles

    Look up under the directory specified by path and try to find files that matches those files in the patterns (no regex).

    :path: Path to be searched.
    :patterns: A list of file names that should be looked up.
    :return: The path of all files that was a match in the patterns as a generator.
    """

    try:
        for entry in scandir(path):
            if entry.is_dir(): yield from findFiles(entry.path, patterns)
            if entry.is_file() and entry.name in patterns: yield entry.path
    except PermissionError:
        _print(f"{findFiles.__name__}: Permission denied cannot access '{path}', ignoring.")


def removeExtentions(filename: str, n_times: int = 1) -> str:
    """
    removeExtentions

    Remove N extentions from the filename.
    Ex. example.tar.gz n_times=1 -> example.tar
    Ex. example.tar.gz n_times=2 -> example

    :filename: Filename.
    :n_times: Number of extentions that should be removed.
    :return: The new string with the extensions removed.
    """

    for _ in range(n_times):
        filename = path.splitext(filename)[0]

    return filename


def tarfileHasRootDirectory(members: List[TarInfo]) -> bool:
    """
    tarfileHasRootDirectory

    Tells where the names are within a common high-level directory.
    Paths must be in the order they appear.

    :names: List of TarInfo objects.
    :return: True if there's a single high-level directory for all other paths within the members.
    """

    return members[0].isdir() and path.commonpath([m.name for m in members]) == members[0].name if members else False


def getPackageUrl(url: str) -> str:
    """
    getPackageURL

    Gets the package of a Github project given it's provided.

    :url: Url of the github package that should be downloaded.
    :return:
    """

    expanded_assets_url: str = ""

    headers: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0"
    }

    request: Request = Request(url, headers=headers)

    try:
        with urlopen(request, timeout=30) as r:
            if r.getcode() != 200: die(f"Failed to fetch html document for url: {url}")

            html: str = r.read().decode("utf-8")
            parser: BasicHtmlParser = BasicHtmlParser("include-fragment", ("src", None), (None, lambda s: s.startswith("http")))
            parser.feed(html)
            expanded_assets_url = parser.get_attribute()
    except Exception as e:
        die(f"Failed to make a request to the url: {url}.\nError: {e}")

    if not expanded_assets_url != "": die("Failed to get expanded_assets_url.")

    request = Request(expanded_assets_url, headers=headers)

    with urlopen(request, timeout=30) as r:
        if r.getcode() != 200: die(f"Failed to fetch html document for url: {expanded_assets_url}")

        html: str = r.read().decode("utf-8")
        parser: BasicHtmlParser = BasicHtmlParser("a", ("href", None), (None, lambda s: s.endswith(".tar.gz")))
        parser.feed(html)
        relative_url: str = parser.get_attribute()

        return "https://github.com/" + relative_url if relative_url else relative_url


def restoreEnvar(name: str, value: str | None) -> None:
    """
    restoreEnvar

    Restore the value of the environment variable or pop it from the environ object.

    :name: Name of the environment variable.
    :value: Original value of the environment variable.
    :return:
    """

    if not value:
        environ.pop(name, None)

        return

    environ[name] = value

