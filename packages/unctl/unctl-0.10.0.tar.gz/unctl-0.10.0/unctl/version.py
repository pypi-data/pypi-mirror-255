import toml
from importlib.metadata import version

try:
    from packaging.version import parse
except ImportError:
    from pip._vendor.packaging.version import parse

from colorama import Fore, Style


def current():
    try:
        return toml.load("pyproject.toml")["tool"]["poetry"]["version"]
    except Exception:
        return version(__package__)


def check():
    if last() > parse(current()):
        print(
            f"{Fore.YELLOW}A new release of unctl is available: "
            f"{Fore.RED + Style.BRIGHT}{current()}{Style.RESET_ALL} -> "
            f"{Fore.GREEN + Style.BRIGHT}{last()}{Style.RESET_ALL}"
        )
        print(
            f"{Fore.YELLOW}To update, run: "
            f"{Fore.GREEN + Style.BRIGHT}pip install --upgrade unctl{Style.RESET_ALL}"
        )


def last():
    """Return version of the last available package."""
    # TODO: currently ignoring this check as we will have private distribution
    version = parse("0")
    return version
