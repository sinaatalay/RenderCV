"""Check for CLI updates without blocking rendering."""

import json
import math
import os
import pathlib
import sys
import threading
import time
import urllib.request
from typing import TypedDict

import packaging.version
from rich import print

from rendercv import __version__

VERSION_CHECK_TTL_SECONDS = 86400


class VersionCache(TypedDict):
    last_check: float
    latest_version: str


def get_cache_dir() -> pathlib.Path:
    """Return the platform-appropriate cache directory for RenderCV."""
    if sys.platform == "win32":
        base = pathlib.Path(
            os.environ.get("LOCALAPPDATA", pathlib.Path.home() / "AppData" / "Local")
        )
    elif sys.platform == "darwin":
        base = pathlib.Path.home() / "Library" / "Caches"
    else:
        base = pathlib.Path(
            os.environ.get("XDG_CACHE_HOME", pathlib.Path.home() / ".cache")
        )
    return base / "rendercv"


def get_version_cache_file() -> pathlib.Path:
    """Return the path to the version check cache file."""
    return get_cache_dir() / "version_check.json"


def read_version_cache() -> VersionCache | None:
    """Read the cached version check data, or None if unavailable/corrupt."""
    try:
        data = json.loads(get_version_cache_file().read_text(encoding="utf-8"))
        if (
            isinstance(data, dict)
            and isinstance(data.get("last_check"), (int, float))
            and math.isfinite(data["last_check"])
            and isinstance(data.get("latest_version"), str)
        ):
            return data
    except (OSError, ValueError):
        pass
    return None


def write_version_cache(version_string: str) -> None:
    """Write the latest version string and current timestamp to the cache file."""
    cache_file = get_version_cache_file()
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(
            json.dumps({"last_check": time.time(), "latest_version": version_string}),
            encoding="utf-8",
        )
    except OSError:
        pass


def fetch_latest_version_from_pypi() -> str | None:
    """Fetch the latest RenderCV version string from PyPI, or None on failure."""
    url = "https://pypi.org/pypi/rendercv/json"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = response.read()
            encoding = response.info().get_content_charset("utf-8")
            json_data = json.loads(data.decode(encoding))
            return json_data["info"]["version"]
    except (OSError, json.JSONDecodeError, KeyError, ValueError):
        return None


def fetch_and_cache_latest_version() -> None:
    """Fetch the latest version from PyPI and write it to the cache file."""
    version_string = fetch_latest_version_from_pypi()
    if version_string:
        write_version_cache(version_string)


def warn_if_new_version_is_available() -> None:
    """Check for a newer RenderCV version using a stale-while-revalidate cache.

    Why:
        Uses a disk cache with background refresh so the CLI never blocks on
        network I/O. If the cache is stale or missing, a daemon thread refreshes
        it for the next invocation.
    """
    cache = read_version_cache()

    if not cache or (time.time() - cache["last_check"]) >= VERSION_CHECK_TTL_SECONDS:
        thread = threading.Thread(target=fetch_and_cache_latest_version, daemon=True)
        thread.start()

    if cache:
        try:
            latest = packaging.version.Version(cache["latest_version"])
            current = packaging.version.Version(__version__)
            if current < latest:
                print(
                    "\n[bold yellow]A new version of RenderCV is available!"
                    f" You are using v{__version__}, and the latest version"
                    f" is v{latest}.[/bold yellow]\n"
                )
        except packaging.version.InvalidVersion:
            pass
