#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NASA NEX-GDDP-CMIP6 Downloader - GUI Edition (Version 1.1)

A desktop application for bulk downloading high-resolution climate projection
data from NASA's NEX-GDDP-CMIP6 dataset. Designed for climate researchers,
hydrologists and environmental scientists who need efficient access to climate
model outputs for analysis and research.

WHAT'S NEW IN VERSION 1.1 
- New wizard step "Area" (between Variables and Options). Download the whole
  globe exactly as before, or only a rectangular study area given by four
  numbers: north, south, west and east.
- Study-area downloads use the THREDDS NetcdfSubset (NCSS) web service: the NASA
  server cuts the data first and sends a small NetCDF file that covers only your
  area (for the full year of every file), so downloads are much smaller and faster.
- Longitudes may be typed as -180..360 (negative values are converted to the
  dataset's 0..360 convention). Persian / Arabic digits are accepted in the
  coordinate fields. The window shows how many grid cells the box covers.
- Study-area files are saved under <output>/subset_<box>/<model>/<scenario>/
  <ensemble>/<variable>/ and keep their original file names, so different areas
  can never be mixed up.
- NCSS files are built on the fly by the server and cannot be resumed part-way:
  each file uses one connection and is simply downloaded again after an error.
  Partial files are always removed (the files are small).
- The command line gets a --bbox NORTH SOUTH WEST EAST option.
- The file progress bar stops animating when a download ends; --self-test now
  also checks the study-area logic and runs the subset downloader against a
  small local test server (no internet needed).
- Smarter lists: scenarios, ensembles and variables now show everything that at least one
  selected model has, with a counter such as [24 of 35 models]. Every model downloads only
  the variables / ensembles it really has (a model that lacks tasmin is skipped for tasmin
  only). The tick box "Only show ... shared by every model" brings back the old behaviour.
- New tick box "All ensembles of every model" (Ensembles step): each model downloads all the
  ensembles it has. The list can still be used to pick ensembles by hand.
- New workflow switch (bottom of the sidebar, with a short explanation of each choice):
  "Variables first" changes the order to Variables -> Scenario -> Models -> Ensembles ->
  Area -> Options -> Download. After you pick the variables and the scenario, every model
  that has them is found and selected for you (untick any you do not want).
- Faster catalog reading: catalogs are now requested in parallel (8 at a time) and are kept
  on disk for 7 days (folder ~/.nex_gddp_cmip6_downloader.cache; File > Clear catalog cache,
  or the Refresh list buttons, fetch them again). "Find files" and the model scan of
  "Variables first" are several times faster, and almost instant on repeated use.
- Correct speed / time-left display in study-area mode: the time left is based on the real
  time every file took (the server prepares each file before sending it), the speed is
  measured over a sliding window, and two new values (Files/min, Time/file) are shown. The
  current file shows "waiting for the server" or "receiving". An impossible time left is
  never shown any more.
- The command line accepts --ensembles all.
- Nothing changes for whole-globe downloads (segmented download, resume, ...).
- Crash diagnostics: a crash log (~/.nex_gddp_cmip6_downloader.crash.log) now
  records hard crashes (faulthandler) and every uncaught exception, so a
  "sudden close" always leaves a traceback behind.
- The UI refresh loop can no longer die silently: it is rescheduled even when
  an event handler fails, and Tk callback errors are logged instead of lost.
- The free-disk-space check no longer freezes the window (it used to run a
  network request on the UI thread, so Windows could show "Not responding").
- Clean shutdown: Tk objects are released on the main thread and leftover
  background threads can no longer crash the interpreter while it exits
  (typical "Tcl_AsyncDelete" / fatal-error exit).
- Version string, user agent and documentation updated.
- One shared HTTP session (no session leak); in-memory catalog cache.
- New default file filter "Latest version of each file".
- Disk-full stops the queue cleanly; free-space check before downloading.
- Existing files shown as Skipped up front; ETA counts only remaining files.
- Size check of existing files, quick NetCDF signature check, rotating log file.
- Optional headless mode: --cli (see --help); --self-test runs offline tests.
- Progress bar, retry-wait and other fixes.
- Completely redesigned, wizard-style interface: a step sidebar, one clear
  task per page, Back / Next navigation and automatic loading of every list
  (no more "Load ..." buttons).
- Multi-model downloads: select one, several or all climate models in the
  first step. The later steps (scenario, ensembles, variables) then show only
  the options that are common to every selected model, and the chosen
  scenario / ensembles / variables are downloaded for all selected models.
- Changing an earlier choice now automatically resets the later steps, so a
  download queue can never be built from stale or mismatched selections.
- Friendly descriptions for scenarios and climate variables.
- Smoother progress display (the UI is no longer flooded by per-chunk events)
  and a more accurate speed / ETA estimate.
- Downloads are verified (size checks on every segment and on the merged file),
  partial files are kept by default so downloads can be resumed, and permanent
  errors (404, disk full, ...) no longer cause minutes of pointless retries.
- Catalog operations can be cancelled; settings are remembered between runs.

KEY FUNCTIONALITIES
1. Models       - browse the climate models (ACCESS-CM2, BCC-CSM2-MR, ...) and
                  select one, several or all of them
2. Scenario     - choose a historical run or an SSP emission pathway
3. Ensembles    - select model realizations (rXiXpXfX patterns)
4. Variables    - pick climate variables (tasmax, tasmin, pr, ...)
5. Area         - whole globe, or a study area (north / south / west / east)
6. Options      - output folder, year range, file version, connections
7. Download     - review the file list, then download with pause / resume / stop

DATASET INFORMATION
- Source: NASA NEX-GDDP-CMIP6 THREDDS Catalog
- Resolution: 0.25 degree (~25 km) daily data
- Coverage: Global (60S to 90N, 0 to 360E)
- Time range: Historical (1950-2014) and Future (2015-2100) projections
- Format: NetCDF4 with CF-compliant metadata

TECHNICAL SPECIFICATIONS
- Whole files: HTTP/HTTPS with range request support (HTTPServer service)
- Study areas: THREDDS NetcdfSubset (NCSS) grid service, netcdf4-classic output
- Parallel connections: configurable (1-16), segmented download of large files
- Error handling: automatic retry with exponential backoff
- Resume: interrupted whole-file downloads continue from the partial data on disk

SYSTEM REQUIREMENTS
- Operating system: Windows 10+, macOS 10.14+, or Linux
- Python 3.7 or higher
- Dependencies: requests, tkinter (included with most Python installers;
  not needed for --cli and --self-test)

COMMAND LINE (no GUI)
  python nex_gddp_cmip6_downloader.py --cli --models ACCESS-CM2 --scenario ssp245 \
      --variables pr tasmax --years 2015 2030 --out D:/cmip6 \
      --bbox 38.5 36.5 44 46.5
  (--bbox NORTH SOUTH WEST EAST is optional; without it whole files are downloaded.)

DEVELOPMENT
- Author: Hadi Asghari
- Contact: hadi.asghari@outlook.com
- GitHub: https://github.com/haadiasghari
- LinkedIn: www.linkedin.com/in/haadi-asghari
- Repository: https://github.com/haadiasghari/NEX-GDDP-CMIP6-Downloader

LICENSE & ATTRIBUTION
- Software: MIT License (see LICENSE file)
- Data: NASA NEX-GDDP-CMIP6 dataset - proper attribution required
- Citation: users must cite NASA data sources in publications

More information about the dataset:
https://www.nccs.nasa.gov/services/data-collections/land-based-products/nex-gddp-cmip6
"""

from __future__ import annotations

import argparse
import errno
import faulthandler
import gc
import hashlib
import json
import logging
import math
import os
import queue
import random
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import types
import webbrowser
import xml.etree.ElementTree as ET
import zlib
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from logging.handlers import RotatingFileHandler
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple, Union
from urllib.parse import urlencode, urljoin

import requests
from requests.adapters import HTTPAdapter

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter import font as tkfont
    HAVE_TK = True
except Exception:  # headless environment: --cli and --self-test still work
    HAVE_TK = False

    class _TkStub:
        """Placeholder base class used only when tkinter is unavailable."""

    tk = types.SimpleNamespace(Tk=_TkStub, Toplevel=_TkStub, Frame=_TkStub,
                               Widget=_TkStub, StringVar=_TkStub, BooleanVar=_TkStub,
                               TclError=Exception)
    ttk = types.SimpleNamespace(Frame=_TkStub)
    filedialog = messagebox = tkfont = None


# ============================================================
# CONFIG
# ============================================================

APP_NAME = "NEX-GDDP-CMIP6 Downloader"
APP_VERSION = "1.1"
AUTHOR_NAME = "Hadi Asghari"
AUTHOR_EMAIL = "hadi.asghari@outlook.com"
GITHUB_URL = "https://github.com/haadiasghari"
REPO_URL = "https://github.com/haadiasghari/NEX-GDDP-CMIP6-Downloader"
DATASET_URL = ("https://www.nccs.nasa.gov/services/data-collections/"
               "land-based-products/nex-gddp-cmip6")

BASE_CATALOG = "https://ds.nccs.nasa.gov/thredds/catalog/AMES/NEX/GDDP-CMIP6"
BASE_CATALOG_XML = BASE_CATALOG + "/catalog.xml"
FILES_BASE = "https://ds.nccs.nasa.gov/thredds/fileServer/"

# THREDDS NetcdfSubset (NCSS) grid service, used for study-area downloads.
# NCSS_QUERY_EXTRA is appended to every request. "temporal=all" asks for every
# time step of the file (without it NCSS returns a single time step).
NCSS_BASE = "https://ds.nccs.nasa.gov/thredds/ncss/grid/"
NCSS_QUERY_EXTRA = (("horizStride", "1"), ("temporal", "all"),
                    ("accept", "netcdf4-classic"))
NCSS_READ_TIMEOUT = 180        # the server builds the file on the fly: be patient
MAX_RETRIES_PER_SUBSET_FILE = 6

# Dataset grid limits used to validate a study area.
LAT_MIN = -60.0
LAT_MAX = 90.0
GRID_STEP = 0.25
AREA_GLOBE = "globe"
AREA_SUBSET = "subset"

# Wizard pages (ids) and the two workflows (the order in which the pages are shown).
P_MODELS, P_SCENARIO, P_ENSEMBLES, P_VARIABLES, P_AREA, P_OPTIONS, P_DOWNLOAD = range(7)
PAGE_NAMES = {P_MODELS: "Models", P_SCENARIO: "Scenario", P_ENSEMBLES: "Ensembles",
              P_VARIABLES: "Variables", P_AREA: "Area", P_OPTIONS: "Options",
              P_DOWNLOAD: "Download"}
FLOW_MODEL = "model"         # models first (the order of earlier versions)
FLOW_VARIABLE = "variable"   # variables and scenario first; models are found automatically
FLOW_ORDERS = {
    FLOW_MODEL: [P_MODELS, P_SCENARIO, P_ENSEMBLES, P_VARIABLES, P_AREA, P_OPTIONS, P_DOWNLOAD],
    FLOW_VARIABLE: [P_VARIABLES, P_SCENARIO, P_MODELS, P_ENSEMBLES, P_AREA, P_OPTIONS, P_DOWNLOAD],
}

# "identity" avoids transparent compression, which would corrupt range requests.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (NEX-GDDP-CMIP6-downloader GUI v1.1)",
    "Accept-Encoding": "identity",
}

REQUEST_TIMEOUT = 30
CATALOG_REQUEST_DELAY = 0.05
CATALOG_WORKERS = 8            # catalog requests made in parallel

DEFAULT_WORKERS = 4
DEFAULT_SEGMENTS = 8

MAX_RETRIES_PER_CATALOG = 5
MAX_RETRIES_PER_FILE = 10
MAX_RETRIES_PER_PART = 6

RETRY_BACKOFF_BASE = 1.6
RETRY_BACKOFF_MAX = 60.0

TRANSIENT_STATUS = {429, 500, 502, 503, 504}
PERMANENT_STATUS = {400, 401, 403, 404, 410}

LATEST_VERSION_LABEL = "Latest version of each file"
ALL_VERSIONS_LABEL = "All versions"
DEFAULT_VERSION_FILTER = LATEST_VERSION_LABEL
CHUNK_SIZE = 1024 * 64

DISK_FULL_DETAIL = "Disk full"
LONG_PAUSE_SECONDS = 30.0      # a pause longer than this may drop the connection
MAX_FREE_RETRIES = 3           # retries not counted after a long pause

CATALOG_CACHE_MAX = 2000
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".nex_gddp_cmip6_downloader.cache")
CACHE_TTL_SECONDS = 7 * 24 * 3600    # catalogs kept on disk for a week
SUBSET_SPEED_WINDOW = 30.0           # seconds: window of the speed shown for study areas

MIN_YEAR = 1950
MAX_YEAR = 2100

# UI
MAX_LOG_LINES = 5000
TRIM_LOG_TO_LINES = 4500
QUEUE_CONFIRM_THRESHOLD = 1000
QUEUE_TABLE_SHOW_LIMIT = 5000
UI_TICK_MS = 150

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".nex_gddp_cmip6_downloader.json")
LOG_PATH = os.path.join(os.path.expanduser("~"), ".nex_gddp_cmip6_downloader.log")
CRASH_LOG_PATH = os.path.join(os.path.expanduser("~"), ".nex_gddp_cmip6_downloader.crash.log")
LOG_MAX_BYTES = 1024 * 1024
LOG_BACKUP_COUNT = 3

# Colours
BG = "#ffffff"
SIDEBAR_BG = "#f1f5f9"
ACTIVE_BG = "#dbeafe"
HEADER_BG = "#0f2a4a"
ACCENT = "#2563eb"
TEXT = "#0f172a"
MUTED = "#64748b"
BORDER = "#cbd5e1"
GREEN = "#16a34a"
RED = "#b91c1c"

FONT_FAMILY = "TkDefaultFont"  # replaced at start-up by the best available font

SCENARIO_HINTS = {
    "historical": "Historical simulation (1950-2014).",
    "ssp126": "SSP1-2.6: sustainability pathway, low emissions.",
    "ssp245": "SSP2-4.5: 'middle of the road', intermediate emissions.",
    "ssp370": "SSP3-7.0: regional rivalry, high emissions.",
    "ssp585": "SSP5-8.5: fossil-fuelled development, very high emissions.",
}

VARIABLE_HINTS = {
    "hurs": "Near-surface relative humidity (%)",
    "huss": "Near-surface specific humidity",
    "pr": "Precipitation",
    "rlds": "Surface downwelling longwave radiation",
    "rsds": "Surface downwelling shortwave radiation",
    "sfcWind": "Near-surface wind speed",
    "tas": "Daily mean near-surface air temperature",
    "tasmax": "Daily maximum near-surface air temperature",
    "tasmin": "Daily minimum near-surface air temperature",
}

# The nine variables of NEX-GDDP-CMIP6 (the 'Variables first' workflow lists them
# before any model has been read).
KNOWN_VARIABLES = tuple(VARIABLE_HINTS)

QUICK_GUIDE = (
    "Follow the steps in the left sidebar:\n\n"
    "1. Models - pick one, several or all climate models. Lists load automatically.\n"
    "2. Scenario - pick 'historical' or one SSP emission pathway.\n"
    "3. Ensembles - pick one or more realizations (most users need r1i1p1f1), or tick "
    "'All ensembles of every model'.\n"
    "4. Variables - pick the climate variables you need (e.g. tasmax, pr).\n"
    "5. Area - download the whole globe, or only a study area: type the north, "
    "south, west and east limits in degrees.\n"
    "6. Options - choose the output folder, years and file version, then press "
    "'Find files'.\n"
    "7. Download - review the list and press 'Start download'.\n\n"
    "Tips:\n"
    "- Lists show everything that at least one selected model has, with a counter "
    "such as [24 of 35 models]. Every model downloads only the variables and "
    "ensembles it really has, so a model without tasmin is simply skipped for tasmin.\n"
    "- Workflow switch (bottom of the sidebar): 'Variables first' lets you pick the "
    "variables and then the scenario; every model that has them is found and selected "
    "for you. Choosing it clears your current selections.\n"
    "- Catalog information is kept on disk for 7 days, so repeating a search is fast "
    "(File > Clear catalog cache forgets it).\n"
    "- A study area is cut on the NASA server, so the files are much smaller and "
    "faster to download. Give a box a little larger than your basin: the server "
    "returns whole 0.25-degree grid cells.\n"
    "- Longitudes: the dataset uses 0 to 360 degrees east. Negative values "
    "(for example -10) are converted automatically.\n"
    "- Double-click a scenario to continue to the next step.\n"
    "- Use the search box to filter long lists; your selection is kept.\n"
    "- Pause, Resume and Stop are available during a download. Whole-file "
    "downloads keep partial files, so you can start again later and the download "
    "continues. Study-area files are small and are simply downloaded again.\n"
    "- Files that already exist in the output folder are skipped.\n"
    "- Changing a choice in an earlier step resets the later steps."
)

SHORTCUTS = (
    "F1\t\tQuick guide\n"
    "F5\t\tRefresh the list on the current step\n"
    "Alt+Right\tNext step\n"
    "Alt+Left\t\tPrevious step\n"
    "Ctrl+L\t\tShow / hide the activity log\n"
    "Ctrl+Q\t\tQuit\n"
    "Double-click\tOn a scenario: continue to the next step"
)


# ============================================================
# GLOBAL EVENTS / SESSION / CACHE / FILE LOG
# ============================================================

resume_event = threading.Event()   # set = running, cleared = paused
stop_event = threading.Event()     # set = stop downloads as soon as possible

_session_lock = threading.Lock()
_shared_session: Optional[requests.Session] = None


def get_session() -> requests.Session:
    """Return the single shared Session (created on first use, and again after
    close_all_sessions()). Only get/head are used, which is safe across threads."""
    global _shared_session
    with _session_lock:
        if _shared_session is None:
            s = requests.Session()
            s.headers.update(HEADERS)
            adapter = HTTPAdapter(pool_connections=4, pool_maxsize=32)
            s.mount("http://", adapter)
            s.mount("https://", adapter)
            _shared_session = s
        return _shared_session


def close_all_sessions():
    global _shared_session
    with _session_lock:
        s = _shared_session
        _shared_session = None
    if s is not None:
        try:
            s.close()
        except Exception:
            pass


# --- catalog cache (in memory and on disk, url -> raw XML bytes) ---
_catalog_cache: Dict[str, bytes] = {}
_catalog_cache_lock = threading.Lock()


def _cache_file(url: str) -> str:
    return os.path.join(CACHE_DIR, hashlib.sha1(url.encode("utf-8")).hexdigest() + ".z")


def cache_get(url: str) -> Optional[bytes]:
    with _catalog_cache_lock:
        data = _catalog_cache.get(url)
    if data is not None:
        return data
    # not in memory: try the disk copy (valid for CACHE_TTL_SECONDS)
    path = _cache_file(url)
    try:
        if time.time() - os.path.getmtime(path) > CACHE_TTL_SECONDS:
            return None
        with open(path, "rb") as fh:
            data = zlib.decompress(fh.read())
    except Exception:
        return None
    if not data:
        return None
    _memory_cache_put(url, data)
    return data


def _memory_cache_put(url: str, data: bytes):
    with _catalog_cache_lock:
        if url not in _catalog_cache and len(_catalog_cache) >= CATALOG_CACHE_MAX:
            try:
                _catalog_cache.pop(next(iter(_catalog_cache)))
            except Exception:
                _catalog_cache.clear()
        _catalog_cache[url] = data


def cache_put(url: str, data: bytes):
    if not data:
        return
    _memory_cache_put(url, data)
    path = _cache_file(url)
    tmp = f"{path}.{threading.get_ident()}.tmp"
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(tmp, "wb") as fh:
            fh.write(zlib.compress(data, 6))
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass


def cache_clear(urls: Optional[Iterable[str]] = None):
    """Forget cached catalogs (memory and disk): the given URLs, or everything."""
    with _catalog_cache_lock:
        if urls is None:
            _catalog_cache.clear()
        else:
            urls = list(urls)
            for u in urls:
                _catalog_cache.pop(u, None)
    if urls is None:
        try:
            for f in os.listdir(CACHE_DIR):
                if f.endswith(".z") or f.endswith(".tmp"):
                    try:
                        os.remove(os.path.join(CACHE_DIR, f))
                    except OSError:
                        pass
        except OSError:
            pass
    else:
        for u in urls:
            try:
                os.remove(_cache_file(u))
            except OSError:
                pass


# --- rotating log file (thread-safe: logging handlers are locked) ---
_file_logger: Optional[logging.Logger] = None
_file_logger_lock = threading.Lock()


def setup_file_logging():
    global _file_logger
    with _file_logger_lock:
        if _file_logger is not None:
            return
        try:
            lg = logging.getLogger("nex_gddp_cmip6_downloader")
            lg.setLevel(logging.INFO)
            lg.propagate = False
            handler = RotatingFileHandler(LOG_PATH, maxBytes=LOG_MAX_BYTES,
                                          backupCount=LOG_BACKUP_COUNT, encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
            lg.addHandler(handler)
            _file_logger = lg
        except Exception:
            _file_logger = None


def file_log(msg: str):
    lg = _file_logger
    if lg is None:
        return
    try:
        lg.info(msg)
    except Exception:
        pass


# --- crash diagnostics (new in 1.1) ---
_crash_fh = None


def install_crash_handlers():
    """Make 'sudden closes' diagnosable.

    * faulthandler writes a Python traceback of every thread to the crash log
      when the process dies from a fatal error (segfault, Tcl/Tk abort, ...).
    * Uncaught exceptions in the main thread and in worker threads are written
      to the normal log file. Nothing here can raise."""
    global _crash_fh
    try:
        _crash_fh = open(CRASH_LOG_PATH, "a", encoding="utf-8", buffering=1)
        _crash_fh.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')}  {APP_NAME} "
                        f"v{APP_VERSION}  Python {sys.version.split()[0]} ===\n")
        faulthandler.enable(file=_crash_fh, all_threads=True)
    except Exception:
        _crash_fh = None

    def _fmt(exc_type, exc, tb) -> str:
        try:
            return "".join(traceback.format_exception(exc_type, exc, tb))
        except Exception:
            return f"{exc_type}: {exc}"

    def _main_hook(exc_type, exc, tb):
        file_log("[FATAL] Uncaught exception:\n" + _fmt(exc_type, exc, tb))
        try:
            sys.__excepthook__(exc_type, exc, tb)
        except Exception:
            pass

    def _thread_hook(args):
        if args.exc_type is SystemExit:
            return
        name = args.thread.name if args.thread is not None else "?"
        file_log(f"[FATAL] Uncaught exception in thread {name}:\n"
                 + _fmt(args.exc_type, args.exc_value, args.exc_traceback))

    try:
        sys.excepthook = _main_hook
        if hasattr(threading, "excepthook"):
            threading.excepthook = _thread_hook
    except Exception:
        pass


def exit_if_threads_alive(code: int = 0):
    """Leftover background threads (network reads, thread-pool workers) must
    not be left running while the interpreter finalizes: a thread that is the
    last owner of a Tk object makes Tcl abort the whole process. If any are
    still alive, flush the logs and leave immediately."""
    try:
        alive = [t for t in threading.enumerate()
                 if t is not threading.main_thread() and t.is_alive()]
    except Exception:
        alive = []
    if not alive:
        return
    file_log(f"[INFO] Exiting with {len(alive)} background thread(s) still running.")
    try:
        logging.shutdown()
    except Exception:
        pass
    for stream in (sys.stdout, sys.stderr, _crash_fh):
        try:
            if stream is not None:
                stream.flush()
        except Exception:
            pass
    os._exit(code)


# --- long-pause tracking (see B7) ---
_pause_lock = threading.Lock()
_long_pause_gen = 0


def _pause_generation() -> int:
    with _pause_lock:
        return _long_pause_gen


def _note_long_pause():
    global _long_pause_gen
    with _pause_lock:
        _long_pause_gen += 1


class PermanentError(Exception):
    """An error that will not go away by retrying (HTTP 404, disk full, ...)."""


class DiskFullError(PermanentError):
    """The output drive has no free space left."""


class RangeIgnored(Exception):
    """The server answered a range request with a full response."""


class TransientHTTPError(RuntimeError):
    """A retryable HTTP status; carries the server's Retry-After hint."""

    def __init__(self, code: int, retry_after: Optional[float] = None):
        super().__init__(f"HTTP {code}")
        self.retry_after = retry_after


# ============================================================
# SMALL HELPERS
# ============================================================

def sleep_backoff(attempt: int, event: threading.Event,
                  base: float = RETRY_BACKOFF_BASE, cap: float = RETRY_BACKOFF_MAX,
                  min_wait: float = 0.0):
    """Interruptible exponential backoff (returns early if `event` is set).
    `min_wait` (e.g. Retry-After) raises the wait, so only one wait happens."""
    backoff = min(cap, base ** attempt)
    if min_wait > backoff:
        backoff = min(min_wait, RETRY_BACKOFF_MAX)
    jitter = random.uniform(0.0, backoff * 0.15)
    event.wait(backoff + jitter)


def retry_after_seconds(resp: requests.Response) -> Optional[float]:
    ra = resp.headers.get("Retry-After")
    if not ra:
        return None
    try:
        return float(ra)
    except Exception:
        return None


def _retry_wait_hint(e: Exception) -> float:
    ra = getattr(e, "retry_after", None)
    if isinstance(ra, (int, float)) and ra > 0:
        return float(ra)
    return 0.0


def format_bytes(n: float) -> str:
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} TB"


def format_speed(bps: float) -> str:
    return format_bytes(bps) + "/s"


def format_duration(seconds: Optional[float]) -> str:
    if seconds is None or seconds < 0 or math.isinf(seconds) or math.isnan(seconds):
        return "-"
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    if seconds < 86400:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
    return f"{seconds // 86400}d {(seconds % 86400) // 3600}h"


def shorten(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: max(1, limit - 1)] + "\u2026"


def open_folder(path: str):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        if messagebox is not None:
            messagebox.showerror("Open folder", f"Could not open the folder:\n{e}")


def parallel_map(func: Callable, items: list, cancel: threading.Event,
                 workers: int = CATALOG_WORKERS,
                 on_done: Optional[Callable[[int, int], None]] = None) -> Optional[list]:
    """Run func(item) for every item in a small thread pool. The results keep the
    order of `items`; an item whose call raised gets None. `on_done(done, total)` is
    called (from the calling thread) as results arrive. Returns None when `cancel`
    was set. Used for the catalog requests, which are small and slow because of
    their latency, so doing several at once makes a big difference."""
    total = len(items)
    results: list = [None] * total
    if total == 0:
        return results

    def run(i: int, item):
        if cancel.is_set():
            return i, None
        try:
            return i, func(item)
        except Exception:
            file_log("[ERR] parallel_map task failed:\n" + traceback.format_exc())
            return i, None

    done = 0
    with ThreadPoolExecutor(max_workers=max(1, min(workers, total))) as pool:
        futures = [pool.submit(run, i, it) for i, it in enumerate(items)]
        for fut in as_completed(futures):
            i, res = fut.result()
            results[i] = res
            done += 1
            if on_done is not None:
                try:
                    on_done(done, total)
                except Exception:
                    pass
    return None if cancel.is_set() else results


# ============================================================
# XML / THREDDS HELPERS
# ============================================================

def parse_xml(data: Union[str, bytes]) -> Optional[ET.Element]:
    try:
        if isinstance(data, str):
            data = data.encode("utf-8")
        return ET.fromstring(data)
    except Exception:
        return None


def local_tag(elem: ET.Element) -> str:
    if "}" in elem.tag:
        return elem.tag.split("}", 1)[1]
    return elem.tag


def parse_catalog_refs(xml_data: Union[str, bytes]) -> List[Dict[str, Optional[str]]]:
    root = parse_xml(xml_data)
    if root is None:
        return []
    refs: List[Dict[str, Optional[str]]] = []
    for el in root.iter():
        if local_tag(el).lower() == "catalogref":
            title = None
            href = None
            for k, v in el.attrib.items():
                lk = k.lower()
                if lk.endswith("title"):
                    title = v
                elif lk.endswith("href"):
                    href = v
            for ch in el:
                if local_tag(ch).lower() == "title" and ch.text:
                    title = ch.text.strip()
            refs.append({"title": title, "href": href})

    seen = set()
    out: List[Dict[str, Optional[str]]] = []
    for r in refs:
        key = (r.get("title"), r.get("href"))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def parse_urlpaths(xml_data: Union[str, bytes]) -> List[str]:
    root = parse_xml(xml_data)
    if root is None:
        return []
    paths: List[str] = []
    for el in root.iter():
        tag = local_tag(el).lower()
        if tag == "urlpath" and el.text:
            paths.append(el.text.strip())
        elif tag == "dataset" and "urlPath" in el.attrib:
            paths.append(el.attrib["urlPath"].strip())
    seen = set()
    out: List[str] = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def href_to_catalog_xml(parent_catalog: str, href: Optional[str],
                        name_guess: Optional[str]) -> Optional[str]:
    if href:
        base = parent_catalog.rsplit("/", 1)[0] + "/"
        url = urljoin(base, href)
        if url.endswith(".html"):
            return url[: -len(".html")] + ".xml"
        if url.endswith(".xml"):
            return url
        if url.endswith("/"):
            return url + "catalog.xml"
        return url + "/catalog.xml"
    if name_guess:
        return f"{BASE_CATALOG}/{name_guess}/catalog.xml"
    return None


# ============================================================
# CATALOG CLIENT (runs in background threads, cancellable)
# ============================================================

class CatalogClient:
    """Fetches THREDDS catalogs. Every list_* method returns None on network
    failure and a (possibly empty) list on success. With refresh=True the
    cached copy of every fetched URL is dropped first."""

    def __init__(self, post_ui: Callable[[dict], None], cancel: threading.Event, gen: int,
                 refresh: bool = False):
        self._post_ui = post_ui
        self.cancel = cancel
        self.gen = gen
        self.refresh = refresh

    # --- messaging ---
    def log(self, msg: str):
        self._post_ui({"type": "log", "msg": msg})

    def status(self, msg: str):
        self._post_ui({"type": "status", "gen": self.gen, "msg": msg})

    # --- HTTP ---
    def fetch_text(self, url: str) -> Optional[bytes]:
        """Return the raw (bytes) XML of a catalog, or None on failure."""
        if self.refresh:
            cache_clear([url])
        else:
            cached = cache_get(url)
            if cached is not None:
                return cached

        session = get_session()
        for attempt in range(1, MAX_RETRIES_PER_CATALOG + 1):
            if self.cancel.is_set():
                return None
            try:
                r = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)

                if r.status_code in TRANSIENT_STATUS:
                    ra = retry_after_seconds(r)
                    self.log(f"[WARN] HTTP {r.status_code}: {url} "
                             f"(attempt {attempt}/{MAX_RETRIES_PER_CATALOG})")
                    if attempt < MAX_RETRIES_PER_CATALOG:
                        sleep_backoff(attempt, self.cancel, min_wait=ra or 0.0)
                    continue

                if 400 <= r.status_code < 500:
                    self.log(f"[WARN] HTTP {r.status_code}: {url}")
                    return None

                r.raise_for_status()
                data = r.content
                if parse_xml(data) is None:
                    raise ValueError("the server did not return a valid catalog")
                cache_put(url, data)
                self.cancel.wait(CATALOG_REQUEST_DELAY)
                return data

            except Exception as e:
                if attempt == MAX_RETRIES_PER_CATALOG:
                    self.log(f"[WARN] Could not fetch {url}: {e}")
                    return None
                self.log(f"[WARN] Fetch error: {url} -> {e} "
                         f"(attempt {attempt}/{MAX_RETRIES_PER_CATALOG})")
                sleep_backoff(attempt, self.cancel)
        return None

    # --- traversal ---
    def _children(self, cat_url: str, what: str) -> Optional[List[Dict[str, Optional[str]]]]:
        self.log(f"[INFO] Fetching {what} catalog: {cat_url}")
        txt = self.fetch_text(cat_url)
        if txt is None:
            return None
        out: List[Dict[str, Optional[str]]] = []
        for r in parse_catalog_refs(txt):
            title = r.get("title")
            href = r.get("href")
            if not title:
                continue
            out.append({
                "title": title.rstrip("/"),
                "href": href,
                "catalog_xml": href_to_catalog_xml(cat_url, href, title),
            })
        return out

    def scan_models(self):
        top = self._children(BASE_CATALOG_XML, "top-level")
        if top is None:
            return None
        if len(top) == 1 and top[0].get("catalog_xml"):
            self.log(f"[INFO] Descending into container: {top[0]['title']}")
            return self._children(top[0]["catalog_xml"], "container")  # type: ignore[arg-type]
        return top

    def list_scenarios(self, model: Dict[str, Optional[str]]):
        cat = model.get("catalog_xml")
        return self._children(cat, "model") if cat else []

    def list_ensembles(self, scenario: Dict[str, Optional[str]]):
        cat = scenario.get("catalog_xml")
        if not cat:
            return []
        ensembles = self._children(cat, "scenario")
        if ensembles is None:
            return None
        regex = re.compile(r"^r\d+i\d+p\d+f\d+$", re.IGNORECASE)
        filtered = [e for e in ensembles if regex.match(e.get("title") or "")]
        return filtered if filtered else ensembles

    def list_parameters(self, ensemble: Dict[str, Optional[str]]):
        cat = ensemble.get("catalog_xml")
        return self._children(cat, "ensemble") if cat else []

    def list_urlpaths(self, parameter: Dict[str, Optional[str]]) -> Optional[List[str]]:
        cat = parameter.get("catalog_xml")
        if not cat:
            return []
        self.log(f"[INFO] Fetching variable catalog: {cat}")
        txt = self.fetch_text(cat)
        if txt is None:
            return None
        return parse_urlpaths(txt)


# ============================================================
# NAME / YEAR / PATH HELPERS
# ============================================================

def build_fileserver_url(urlpath: str) -> str:
    if urlpath.startswith("/"):
        urlpath = urlpath[1:]
    return urljoin(FILES_BASE, urlpath)


def sanitize_folder_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[\\/:\*\?\"<>\|]", "_", name)
    name = name.replace(" ", "_")
    return name


_VER = r"(?:_v\d+(?:\.\d+)*)?"


def file_years_from_filename(fname: str) -> Tuple[Optional[int], Optional[int]]:
    m = re.search(r"_(\d{8})-(\d{8})" + _VER + r"\.nc$", fname, re.IGNORECASE)
    if m:
        return int(m.group(1)[:4]), int(m.group(2)[:4])
    m = re.search(r"_(\d{4})-(\d{4})" + _VER + r"\.nc$", fname, re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"_(\d{4})" + _VER + r"\.nc$", fname, re.IGNORECASE)
    if m:
        y = int(m.group(1))
        if 1800 <= y <= 2300:
            return y, y
    for g in reversed(re.findall(r"(?<!\d)(\d{4})(?!\d)", fname)):
        y = int(g)
        if 1800 <= y <= 2300:
            return y, y
    return None, None


def years_overlap(file_y0: Optional[int], file_y1: Optional[int],
                  req_y0: int, req_y1: int) -> bool:
    if file_y0 is None and file_y1 is None:
        return False
    y0 = file_y0 if file_y0 is not None else file_y1
    y1 = file_y1 if file_y1 is not None else file_y0
    if y0 is None or y1 is None:
        return False
    return not (y1 < req_y0 or y0 > req_y1)


def version_key(fname: str) -> Tuple[int, ...]:
    """Version of a file as a tuple of ints ('..._v2.0.nc' -> (2, 0)).
    A file without a version suffix is the lowest version, (0,)."""
    m = re.search(r"_v(\d+(?:\.\d+)*)\.nc$", fname, re.IGNORECASE)
    if not m:
        return (0,)
    return tuple(int(x) for x in m.group(1).split("."))


# ============================================================
# STUDY AREA (SUBSET) HELPERS  (new in 1.1)
# ============================================================

# Persian / Arabic-Indic digits and separators are converted to plain ASCII so
# that coordinates can be typed with any keyboard layout.
_DIGIT_MAP: Dict[int, str] = {}
for _i, _c in enumerate("\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9"):
    _DIGIT_MAP[ord(_c)] = str(_i)
for _i, _c in enumerate("\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669"):
    _DIGIT_MAP[ord(_c)] = str(_i)
_DIGIT_MAP[0x066B] = "."    # Arabic decimal separator
_DIGIT_MAP[0x066C] = ""     # Arabic thousands separator
_DIGIT_MAP[ord(",")] = "."  # decimal comma
_DIGIT_MAP[0x2212] = "-"    # unicode minus
_DIGIT_MAP[0x2013] = "-"    # en dash


def parse_coord(text, label: str) -> float:
    """Convert one typed coordinate to a float, or raise ValueError with a
    message that is suitable for showing to the user."""
    s = str(text if text is not None else "").strip().translate(_DIGIT_MAP)
    s = s.replace(" ", "")
    if not s:
        raise ValueError(f"Enter a value for {label}.")
    try:
        v = float(s)
    except ValueError:
        raise ValueError(f"{label} must be a number (for example 37.5).")
    if not math.isfinite(v):
        raise ValueError(f"{label} must be a finite number.")
    return v


def parse_bbox(north, south, west, east) -> Dict[str, float]:
    """Validate a study area and return {'north', 'south', 'west', 'east'} as
    floats, with longitudes converted to the dataset's 0..360 convention.
    Raises ValueError (user-friendly message) for anything unusable."""
    n = parse_coord(north, "North")
    s = parse_coord(south, "South")
    w = parse_coord(west, "West")
    e = parse_coord(east, "East")

    for name, v in (("North", n), ("South", s)):
        if not (LAT_MIN <= v <= LAT_MAX):
            raise ValueError(f"{name} must be between {LAT_MIN:g} and {LAT_MAX:g} degrees "
                             f"(the dataset covers 60\u00b0S to 90\u00b0N).")
    if n <= s:
        raise ValueError("North must be greater than South.")

    for name, v in (("West", w), ("East", e)):
        if not (-180.0 <= v <= 360.0):
            raise ValueError(f"{name} must be between -180 and 360 degrees.")
    if w < 0:
        w += 360.0
    if e < 0:
        e += 360.0
    if w >= e:
        raise ValueError("West must be less than East (longitudes are converted to 0-360). "
                         "An area that crosses the 0\u00b0 meridian cannot be requested in one "
                         "box: download it as two boxes.")
    return {"north": n, "south": s, "west": w, "east": e}


def _fmt_coord(v: float) -> str:
    """Compact decimal text of a coordinate: 43.0 -> '43', 44.5 -> '44.5'."""
    t = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if t in ("", "-0") else t


def format_bbox(b: Dict[str, float]) -> str:
    return (f"N{_fmt_coord(b['north'])} S{_fmt_coord(b['south'])} "
            f"W{_fmt_coord(b['west'])} E{_fmt_coord(b['east'])}")


def subset_tag(b: Dict[str, float]) -> str:
    """Folder-safe tag of a study area, e.g. 'N38p5_S36p5_W44_E46p5'."""
    def f(v: float) -> str:
        return _fmt_coord(v).replace("-", "m").replace(".", "p")
    return f"N{f(b['north'])}_S{f(b['south'])}_W{f(b['west'])}_E{f(b['east'])}"


def build_ncss_url(urlpath: str, var: str, bbox: Dict[str, float]) -> str:
    """NetcdfSubset request for one file and one variable inside a bounding box."""
    query = [("var", var),
             ("north", _fmt_coord(bbox["north"])),
             ("west", _fmt_coord(bbox["west"])),
             ("east", _fmt_coord(bbox["east"])),
             ("south", _fmt_coord(bbox["south"]))]
    query.extend(NCSS_QUERY_EXTRA)
    return NCSS_BASE + urlpath.lstrip("/") + "?" + urlencode(query)


def bbox_cells(b: Dict[str, float]) -> Tuple[int, int]:
    """Approximate (columns, rows) of grid cells covered by the box."""
    cols = max(1, int(math.ceil((b["east"] - b["west"]) / GRID_STEP)))
    rows = max(1, int(math.ceil((b["north"] - b["south"]) / GRID_STEP)))
    return cols, rows


# ============================================================
# SELECTION HELPERS  (new in 1.1)
# ============================================================

def union_counts(per_model: Dict[str, Iterable[str]]) -> Tuple[Dict[str, int], int]:
    """For {model: items} return ({item: number of models that have it}, number of models)."""
    counts: Dict[str, int] = {}
    for items in per_model.values():
        for it in set(items):
            counts[it] = counts.get(it, 0) + 1
    return counts, len(per_model)


def count_label(n: int, total: int) -> str:
    """'[24 of 35 models]' (nothing when there is only one model to compare)."""
    return f"[{n} of {total} models]" if total > 1 else ""


def model_variables(per_ens: Dict[str, Dict[str, object]]) -> Set[str]:
    """Variables a model has in any of its loaded ensembles."""
    out: Set[str] = set()
    for variables in per_ens.values():
        out.update(variables.keys())
    return out


def models_with_variables(params_by_model: Dict[str, Dict[str, Dict[str, object]]],
                          variables: List[str]) -> List[Tuple[str, List[str], List[str]]]:
    """[(model, have, missing)] for every model that has at least one of the
    variables, sorted by model name. Used by the 'Variables first' workflow."""
    out: List[Tuple[str, List[str], List[str]]] = []
    for model in sorted(params_by_model, key=str.lower):
        has = model_variables(params_by_model[model])
        have = [v for v in variables if v in has]
        if have:
            out.append((model, have, [v for v in variables if v not in has]))
    return out


def select_download_params(params_by_model: Dict[str, Dict[str, Dict[str, object]]],
                           models: List[str], ensembles: List[str],
                           all_ensembles: bool) -> Dict[str, Dict[str, Dict[str, object]]]:
    """Keep only the chosen models and ensembles. With all_ensembles every
    ensemble a model has is kept (each model uses its own ensembles)."""
    out: Dict[str, Dict[str, Dict[str, object]]] = {}
    for model in models:
        per = params_by_model.get(model) or {}
        for ens_name, variables in per.items():
            if all_ensembles or ens_name in ensembles:
                out.setdefault(model, {})[ens_name] = dict(variables)
    return out


# ============================================================
# QUEUE BUILDING (background)
# ============================================================

def collect_download_items(client: CatalogClient, spec: dict) -> dict:
    """Scan the catalogs of the chosen variables and return the matching files.
    spec['params_by_model'] holds, for every model, the ensembles to use and the
    variables each ensemble has; a model simply contributes the chosen variables
    it has. With spec['subset'] (a bounding box from parse_bbox) every item is a
    NetcdfSubset request instead of a whole-file download."""
    items: List[Dict] = []
    seen_urls: Set[str] = set()
    failures = 0
    latest_only = bool(spec.get("latest_only"))
    subset = spec.get("subset")
    root_dir = spec["out_dir"]
    if subset:
        root_dir = os.path.join(root_dir, "subset_" + subset_tag(subset))

    jobs: List[Tuple[str, str, str, Dict[str, Optional[str]]]] = []
    missing: Dict[str, List[str]] = {}
    for model in spec["models"]:
        per_ens_all = spec["params_by_model"].get(model)
        if not per_ens_all:
            client.log(f"[WARN] None of the selected ensembles is available for model "
                       f"'{model}'; skipped.")
            continue
        for ens_name, per_params in per_ens_all.items():
            for p_name in spec["params"]:
                entry = per_params.get(p_name)
                if not entry:
                    missing.setdefault(p_name, []).append(f"{model}/{ens_name}")
                    continue
                jobs.append((model, ens_name, p_name, entry))
    for p_name, where in missing.items():
        shown = ", ".join(where[:8]) + (" \u2026" if len(where) > 8 else "")
        client.log(f"[INFO] Variable '{p_name}' is not available in {len(where)} "
                   f"model/ensemble combination(s), skipped there: {shown}")

    def progress(done: int, total: int):
        client.status(f"Finding files\u2026 reading catalogs ({done}/{total})")

    fetched = parallel_map(lambda job: client.list_urlpaths(job[3]), jobs, client.cancel,
                           on_done=progress)
    if fetched is None:                  # cancelled
        return {"items": [], "failures": failures}
    for (model, ens_name, p_name, entry), urlpaths in zip(jobs, fetched):
        if urlpaths is None:
            failures += 1
            continue
        for up in urlpaths:
            if not up.lower().endswith(".nc"):
                continue
            if spec["version_filter"] and spec["version_filter"] not in up:
                continue
            fname = os.path.basename(up)
            fy0, fy1 = file_years_from_filename(fname)
            if not years_overlap(fy0, fy1, spec["y0"], spec["y1"]):
                continue
            fs_url = build_fileserver_url(up)
            if fs_url in seen_urls:
                continue
            seen_urls.add(fs_url)
            req_url = build_ncss_url(up, p_name, subset) if subset else fs_url
            out_folder = os.path.join(
                root_dir,
                sanitize_folder_name(model),
                sanitize_folder_name(spec["scenario"]),
                sanitize_folder_name(ens_name),
                sanitize_folder_name(p_name),
            )
            sort_year = fy0 if fy0 is not None else (fy1 if fy1 is not None else 0)
            yr_text = f"{fy0}" if fy0 == fy1 else f"{fy0}-{fy1}"
            items.append({
                "url": req_url,
                "out_dir": out_folder,
                "filename": fname,
                "model": model,
                "year_sort": sort_year,
                "year_text": yr_text,
                "vkey": version_key(fname),
                "group": (model, ens_name, p_name, fy0, fy1),
                "variable": p_name,
                "ensemble": ens_name,
                "subset": bool(subset),
            })

    if latest_only:
        best: Dict[tuple, Dict] = {}
        for it in items:
            cur = best.get(it["group"])
            if cur is None or it["vkey"] > cur["vkey"]:
                best[it["group"]] = it
        items = [it for it in items if best[it["group"]] is it]

    items.sort(key=lambda x: (x["model"].lower(), x["year_sort"], x["filename"]))

    if subset and items:
        client.log(f"[INFO] Study area {format_bbox(subset)}. Example request: {items[0]['url']}")

    # Light, network-free check for files that are already on disk.
    for it in items:
        try:
            it["exists"] = os.path.exists(os.path.join(it["out_dir"], it["filename"]))
        except Exception:
            it["exists"] = False
    return {"items": items, "failures": failures}


# ============================================================
# DOWNLOAD ENGINE
# ============================================================

class ProgressTracker:
    """Thread-safe progress counters. Worker threads write, the UI reads."""

    def __init__(self):
        self._lock = threading.Lock()
        self._reset_unlocked()

    def _reset_unlocked(self):
        self.start_ts: Optional[float] = None
        self.pause_ts: Optional[float] = None
        self.paused = False
        self.paused_total = 0.0
        self.session_bytes = 0
        self.file_total: Optional[int] = None
        self.file_done = 0
        self.completed_sizes: List[int] = []
        self.completed_durations: List[float] = []   # seconds each finished file took
        self.files_total = 0
        self.files_done = 0
        self.skip_pending = 0        # files that were on disk at start, not processed yet
        self.cur_flagged = False     # current file is one of those
        self.file_start_ts: Optional[float] = None
        self.file_paused_base = 0.0
        self.phase = ""              # e.g. "waiting for the server" (study-area downloads)

    def start(self, files_total: int, preexisting: int = 0):
        with self._lock:
            self._reset_unlocked()
            self.start_ts = time.monotonic()
            self.files_total = files_total
            self.skip_pending = max(0, min(int(preexisting), files_total))

    def _paused_so_far(self, now: float) -> float:
        """Total time spent paused up to `now` (including a pause in progress)."""
        extra = (now - self.pause_ts) if (self.paused and self.pause_ts) else 0.0
        return self.paused_total + extra

    def pause(self):
        with self._lock:
            if self.start_ts is not None and not self.paused:
                self.paused = True
                self.pause_ts = time.monotonic()

    def resume(self):
        with self._lock:
            if self.paused and self.pause_ts is not None:
                self.paused_total += time.monotonic() - self.pause_ts
            self.paused = False
            self.pause_ts = None

    def begin_file(self, flagged: bool = False):
        with self._lock:
            now = time.monotonic()
            self.file_total = None
            self.file_done = 0
            self.cur_flagged = bool(flagged)
            self.file_start_ts = now
            self.file_paused_base = self._paused_so_far(now)
            self.phase = ""

    def set_phase(self, text: str):
        with self._lock:
            self.phase = text

    def set_file_total(self, total: Optional[int]):
        with self._lock:
            self.file_total = total

    def set_file_abs(self, value: int):
        with self._lock:
            self.file_done = max(0, int(value))

    def add_bytes(self, n: int):
        with self._lock:
            self.file_done += n
            self.session_bytes += n

    def end_file(self, status: str, flagged: bool = False):
        with self._lock:
            now = time.monotonic()
            if status in ("ok", "skipped", "failed"):
                self.files_done += 1
                if flagged and self.skip_pending > 0:
                    self.skip_pending -= 1
            if status == "ok":
                size = self.file_total or self.file_done
                if size:
                    self.completed_sizes.append(int(size))
                if self.file_start_ts is not None:
                    dur = now - self.file_start_ts - (self._paused_so_far(now) - self.file_paused_base)
                    self.completed_durations.append(max(0.0, dur))
            self.cur_flagged = False
            self.file_start_ts = None
            self.phase = ""

    def snapshot(self) -> dict:
        with self._lock:
            now = time.monotonic()
            if self.start_ts is None:
                active = 0.0
            else:
                active = max(0.0, now - self.start_ts - self._paused_so_far(now))
            if self.file_start_ts is None:
                cur_elapsed = 0.0
            else:
                cur_elapsed = max(0.0, now - self.file_start_ts
                                  - (self._paused_so_far(now) - self.file_paused_base))
            return {
                "active_seconds": active,
                "paused": self.paused,
                "session_bytes": self.session_bytes,
                "file_total": self.file_total,
                "file_done": self.file_done,
                "completed_sizes": list(self.completed_sizes),
                "completed_durations": list(self.completed_durations),
                "cur_elapsed": cur_elapsed,
                "phase": self.phase,
                "files_total": self.files_total,
                "files_done": self.files_done,
                "skip_pending": self.skip_pending,
                "cur_flagged": self.cur_flagged,
            }


def estimate_eta(snap: dict, speed: float) -> Optional[float]:
    """Remaining bytes / speed, assuming the remaining files are about as large
    as the files seen so far (NEX-GDDP files are very uniform in size). Files
    that were already on disk at the start are not counted. Good for whole-file
    downloads, where the time is spent transferring bytes."""
    if speed <= 0:
        return None
    known = list(snap["completed_sizes"])
    cur_total = snap["file_total"]
    if cur_total:
        known.append(cur_total)
    if not known:
        return None
    avg = sum(known) / len(known)
    flagged = snap.get("cur_flagged", False)
    real_left = snap["files_total"] - snap["files_done"] - snap.get("skip_pending", 0)
    after_current = max(0, real_left - (0 if flagged else 1))
    if cur_total:
        cur_remaining = max(0, cur_total - snap["file_done"])
    elif flagged:
        cur_remaining = 0
    else:
        cur_remaining = avg
    return (cur_remaining + avg * after_current) / speed


def estimate_eta_files(snap: dict) -> Optional[float]:
    """Remaining files x the time the last finished files really took. Used for
    study-area downloads: the server prepares every file before it sends it, so the
    time per file is not related to the number of bytes (a bytes-per-second estimate
    would be wildly wrong). Needs at least one finished file."""
    durations = snap.get("completed_durations") or []
    if not durations:
        return None
    recent = durations[-10:]
    avg = sum(recent) / len(recent)
    flagged = snap.get("cur_flagged", False)
    real_left = snap["files_total"] - snap["files_done"] - snap.get("skip_pending", 0)
    after_current = max(0, real_left - (0 if flagged else 1))
    if flagged:
        cur_remaining = 0.0
    else:
        cur_remaining = max(0.0, avg - snap.get("cur_elapsed", 0.0))
    return cur_remaining + avg * after_current


def compute_eta(snap: dict, speed: float, subset: bool) -> Optional[float]:
    """Time left in seconds, or None when it cannot be estimated yet."""
    if subset:
        return estimate_eta_files(snap)
    eta = estimate_eta(snap, speed)
    return eta if eta is not None else estimate_eta_files(snap)


def format_eta(eta: Optional[float]) -> str:
    """Text for the 'Time left' field. Absurd values (a stalled connection) are
    shown as '> 30 days' instead of a huge number."""
    if eta is None or math.isnan(eta) or eta < 0:
        return "Calculating\u2026"
    if math.isinf(eta) or eta > 30 * 86400:
        return "> 30 days"
    return format_duration(eta)


def raise_for_bad_status(r: requests.Response):
    code = r.status_code
    if code in PERMANENT_STATUS:
        raise PermanentError(f"HTTP {code} for {r.url}")
    if code in TRANSIENT_STATUS:
        # The caller's retry loop waits max(backoff, Retry-After) exactly once.
        raise TransientHTTPError(code, retry_after_seconds(r))
    if code >= 400:
        raise RuntimeError(f"HTTP {code}")


def head_info(url: str) -> Tuple[Optional[int], bool]:
    """Return (total_size, supports_range). Raises PermanentError on 404 etc."""
    session = get_session()
    try:
        headers = dict(HEADERS)
        headers["Range"] = "bytes=0-0"
        with session.get(url, headers=headers, timeout=REQUEST_TIMEOUT,
                         stream=True, allow_redirects=True) as r:
            if r.status_code in PERMANENT_STATUS:
                raise PermanentError(f"HTTP {r.status_code} for {url}")
            if r.status_code == 206:
                m = re.match(r"bytes\s+\d+-\d+/(\d+|\*)",
                             r.headers.get("Content-Range", ""), re.IGNORECASE)
                if m and m.group(1).isdigit():
                    return int(m.group(1)), True
                return None, True
            if r.status_code == 200:
                cl = r.headers.get("Content-Length")
                if cl and cl.isdigit():
                    return int(cl), False
    except PermanentError:
        raise
    except Exception:
        pass

    try:
        r = session.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if r.status_code == 200:
            cl = r.headers.get("Content-Length")
            if cl and cl.isdigit():
                return int(cl), False
    except Exception:
        pass
    return None, False


def cleanup_partials(dest_dir: str, fname: str):
    try:
        for f in os.listdir(dest_dir):
            if (f == fname + ".part"
                    or f.startswith("." + fname + ".part")
                    or f == fname + ".partmerge"):
                try:
                    os.remove(os.path.join(dest_dir, f))
                except Exception:
                    pass
    except Exception:
        pass


def segment_part_paths(dest_dir: str, fname: str, count: int) -> List[str]:
    # The part count is part of the name, so parts made with a different
    # segment setting can never be mixed up with the current ones.
    return [os.path.join(dest_dir, f".{fname}.part{i}of{count}") for i in range(count)]


def purge_foreign_parts(dest_dir: str, fname: str, keep: List[str]):
    """Remove segment parts of this file that are not in `keep`."""
    keep_set = {os.path.basename(p) for p in keep}
    try:
        for f in os.listdir(dest_dir):
            if f.startswith("." + fname + ".part") and f not in keep_set:
                try:
                    os.remove(os.path.join(dest_dir, f))
                except Exception:
                    pass
    except Exception:
        pass


def purge_single_part(final_path: str):
    """Remove the old single-connection partial file of this file."""
    try:
        p = final_path + ".part"
        if os.path.exists(p):
            os.remove(p)
    except Exception:
        pass


def sum_sizes(paths: List[str]) -> int:
    total = 0
    for p in paths:
        try:
            total += os.path.getsize(p)
        except OSError:
            pass
    return total


def merge_parts(part_paths: List[str], final_path: str, expected_total: int):
    tmp = final_path + ".partmerge"
    with open(tmp, "wb") as fw:
        for p in part_paths:
            with open(p, "rb") as fr:
                while True:
                    buf = fr.read(CHUNK_SIZE * 16)
                    if not buf:
                        break
                    fw.write(buf)
    size = os.path.getsize(tmp)
    if size != expected_total:
        try:
            os.remove(tmp)
        except OSError:
            pass
        for p in part_paths:
            try:
                os.remove(p)
            except OSError:
                pass
        raise IOError(f"Merged file size mismatch ({size} != {expected_total}); parts discarded")
    os.replace(tmp, final_path)
    for p in part_paths:
        try:
            os.remove(p)
        except OSError:
            pass


def verify_netcdf(path: str) -> Optional[str]:
    """Quick signature check of a finished .nc file. Returns None when the file
    looks fine (or is not a .nc file); otherwise renames it to .bad and returns
    an error message. Never raises."""
    try:
        if not path.lower().endswith(".nc"):
            return None
        with open(path, "rb") as fh:
            head = fh.read(4)
        if head.startswith(b"\x89HDF") or head[:3] == b"CDF":
            return None
        try:
            os.replace(path, path + ".bad")
        except OSError:
            pass
        return "Downloaded file is not valid NetCDF/HDF5 (renamed to .bad); it will be downloaded again next time"
    except Exception:
        return None


def stream_to_file(resp: requests.Response, fp, tracker: ProgressTracker) -> int:
    wrote = 0
    for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
        paused_since: Optional[float] = None
        while not resume_event.wait(0.5):      # paused
            if paused_since is None:
                paused_since = time.monotonic()
            if stop_event.is_set():
                break
        if paused_since is not None and time.monotonic() - paused_since > LONG_PAUSE_SECONDS:
            _note_long_pause()                 # the server may have closed the connection
        if stop_event.is_set():
            break
        if chunk:
            fp.write(chunk)
            wrote += len(chunk)
            tracker.add_bytes(len(chunk))
    return wrote


def _raise_if_disk_full(e: Exception):
    if isinstance(e, OSError) and getattr(e, "errno", None) == errno.ENOSPC:
        raise DiskFullError(DISK_FULL_DETAIL)


def download_part(url: str, start: int, end: int, part_path: str,
                  tracker: ProgressTracker, post_log,
                  max_retries: int = MAX_RETRIES_PER_PART) -> bool:
    session = get_session()
    expected = end - start + 1
    name = os.path.basename(part_path)
    attempt = 0
    free_retries = 0

    while attempt < max_retries:
        attempt += 1
        if stop_event.is_set():
            return False
        gen0 = _pause_generation()
        try:
            existing = os.path.getsize(part_path) if os.path.exists(part_path) else 0
            if existing > expected:
                # download_file_robust normally removes such parts up front.
                os.remove(part_path)
                existing = 0
            if existing == expected:
                return True

            real_start = start + existing
            headers = dict(HEADERS)
            headers["Range"] = f"bytes={real_start}-{end}"

            with session.get(url, headers=headers, stream=True,
                             timeout=REQUEST_TIMEOUT, allow_redirects=True) as r:
                if r.status_code == 200:
                    raise RangeIgnored("Server ignored the Range header")
                if r.status_code != 206:
                    raise_for_bad_status(r)
                    raise RuntimeError(f"Unexpected HTTP {r.status_code}")

                m = re.match(r"bytes\s+(\d+)-(\d+)/(\d+|\*)",
                             r.headers.get("Content-Range", ""), re.IGNORECASE)
                if m and int(m.group(1)) != real_start:
                    raise RuntimeError(
                        f"Content-Range mismatch: got {m.group(1)}, expected {real_start}")

                with open(part_path, "ab" if existing > 0 else "wb") as f:
                    stream_to_file(r, f, tracker)

            if stop_event.is_set():
                return False
            size = os.path.getsize(part_path)
            if size != expected:
                raise IOError(f"Incomplete segment ({size}/{expected} bytes)")
            return True

        except (PermanentError, RangeIgnored):
            raise
        except Exception as e:
            _raise_if_disk_full(e)
            if free_retries < MAX_FREE_RETRIES and _pause_generation() != gen0:
                # The connection most likely died during a long pause: reconnect
                # without spending one of the retry attempts.
                free_retries += 1
                attempt -= 1
                post_log(f"[INFO] Connection lost after a long pause ({name}); reconnecting.")
                stop_event.wait(1.0)
                continue
            if attempt == max_retries:
                post_log(f"[WARN] Segment failed ({name}): {e}")
                return False
            post_log(f"[WARN] Segment error ({name}): {e} (retry {attempt}/{max_retries})")
            sleep_backoff(attempt, stop_event, min_wait=_retry_wait_hint(e))

    return False


def download_single_stream(url: str, out_path: str, total: Optional[int],
                           tracker: ProgressTracker, post_log,
                           max_retries: int = MAX_RETRIES_PER_PART) -> bool:
    session = get_session()
    tmp = out_path + ".part"
    name = os.path.basename(out_path)
    attempt = 0
    free_retries = 0

    while attempt < max_retries:
        attempt += 1
        if stop_event.is_set():
            return False
        gen0 = _pause_generation()
        try:
            existing = os.path.getsize(tmp) if os.path.exists(tmp) else 0
            if total:
                if existing > total:
                    os.remove(tmp)
                    existing = 0
                elif existing == total:
                    tracker.set_file_abs(total)
                    os.replace(tmp, out_path)
                    return True
            tracker.set_file_abs(existing)

            headers = dict(HEADERS)
            if existing > 0:
                headers["Range"] = f"bytes={existing}-"

            with session.get(url, headers=headers, stream=True,
                             timeout=REQUEST_TIMEOUT, allow_redirects=True) as r:
                if existing > 0:
                    start_ok = False
                    if r.status_code == 206:
                        m = re.match(r"bytes\s+(\d+)-", r.headers.get("Content-Range", ""),
                                     re.IGNORECASE)
                        start_ok = (m is None) or int(m.group(1)) == existing
                    if not start_ok:
                        if r.status_code in PERMANENT_STATUS or r.status_code in TRANSIENT_STATUS:
                            raise_for_bad_status(r)
                        post_log(f"[WARN] Server cannot resume; restarting {name}")
                        try:
                            os.remove(tmp)
                        except OSError:
                            pass
                        tracker.set_file_abs(0)
                        continue
                else:
                    if r.status_code not in (200, 206):
                        raise_for_bad_status(r)
                        raise RuntimeError(f"Unexpected HTTP {r.status_code}")

                cl = r.headers.get("Content-Length")
                expected_len = int(cl) if (cl and cl.isdigit()) else None

                with open(tmp, "ab" if existing > 0 else "wb") as f:
                    wrote = stream_to_file(r, f, tracker)

                if (not stop_event.is_set() and expected_len is not None
                        and wrote != expected_len):
                    raise IOError(f"Incomplete response ({wrote}/{expected_len} bytes)")

            if stop_event.is_set():
                return False

            size = os.path.getsize(tmp)
            if total and size != total:
                raise IOError(f"Incomplete download ({size}/{total} bytes)")
            os.replace(tmp, out_path)
            return True

        except PermanentError:
            raise
        except Exception as e:
            _raise_if_disk_full(e)
            if free_retries < MAX_FREE_RETRIES and _pause_generation() != gen0:
                free_retries += 1
                attempt -= 1
                post_log(f"[INFO] Connection lost after a long pause ({name}); reconnecting.")
                stop_event.wait(1.0)
                continue
            if attempt == max_retries:
                post_log(f"[WARN] Download failed ({name}): {e}")
                return False
            post_log(f"[WARN] Download error ({name}): {e} (retry {attempt}/{max_retries})")
            sleep_backoff(attempt, stop_event, min_wait=_retry_wait_hint(e))

    return False


def _existing_file_ok(url: str, final_path: str, post_log) -> bool:
    """Compare an existing file with the size the server reports. Returns False
    only when the sizes are known and differ (the file is then moved to .bad so
    it gets downloaded again). Any doubt keeps the old 'skip' behaviour."""
    if stop_event.is_set():
        return True
    try:
        expected, _ = head_info(url)
    except Exception:
        return True
    try:
        if expected and expected > 0:
            local = os.path.getsize(final_path)
            if local != expected:
                post_log(f"[WARN] Existing file has wrong size ({local} != {expected}); "
                         f"renamed to .bad and downloading again: {os.path.basename(final_path)}")
                os.replace(final_path, final_path + ".bad")
                return False
    except OSError:
        return True
    return True


def download_file_robust(url: str, dest_dir: str, segments: int, workers: int,
                         max_retries: int, tracker: ProgressTracker, post_log,
                         cleanup_on_stop: bool = False) -> Tuple[str, str]:
    """Download one file. Returns (status, detail); status is one of
    'ok', 'skipped', 'failed', 'stopped'."""
    os.makedirs(dest_dir, exist_ok=True)
    fname = os.path.basename(url)
    final_path = os.path.join(dest_dir, fname)

    if os.path.exists(final_path):
        if _existing_file_ok(url, final_path, post_log):
            return "skipped", final_path

    def stopped() -> Tuple[str, str]:
        if cleanup_on_stop:
            cleanup_partials(dest_dir, fname)
            post_log(f"[INFO] Removed partial files for {fname}")
        return "stopped", "Stopped by user"

    def finish_ok() -> Tuple[str, str]:
        bad = verify_netcdf(final_path)
        if bad:
            return "failed", bad
        return "ok", final_path

    try:
        total, supports_range = head_info(url)
    except PermanentError as e:
        return "failed", str(e)
    if stop_event.is_set():
        return stopped()

    total_known = bool(total and total > 0)
    tracker.set_file_total(total if total_known else None)

    for attempt in range(1, max_retries + 1):
        if stop_event.is_set():
            return stopped()

        try:
            if not total_known:
                t2, sr2 = head_info(url)
                if t2:
                    total, supports_range, total_known = t2, sr2, True
                    tracker.set_file_total(total)

            segmented = bool(supports_range and total_known and segments > 1 and total)

            if segmented:
                assert total is not None
                part_size = math.ceil(total / segments)
                ranges: List[Tuple[int, int]] = []
                for i in range(segments):
                    s = i * part_size
                    e = min(total - 1, (i + 1) * part_size - 1)
                    if s <= e:
                        ranges.append((s, e))

                part_paths = segment_part_paths(dest_dir, fname, len(ranges))
                purge_foreign_parts(dest_dir, fname, part_paths)
                purge_single_part(final_path)       # old single-connection leftovers
                for pth, (s, e) in zip(part_paths, ranges):
                    try:
                        if os.path.exists(pth) and os.path.getsize(pth) > e - s + 1:
                            os.remove(pth)          # oversize part: start it again
                    except OSError:
                        pass
                tracker.set_file_abs(sum_sizes(part_paths))

                fatal: Optional[Exception] = None
                range_ignored = False
                results: List[bool] = []
                max_workers = max(1, min(workers, len(ranges)))
                with ThreadPoolExecutor(max_workers=max_workers) as pool:
                    futs = []
                    for idx, (s, e) in enumerate(ranges):
                        if stop_event.is_set():
                            break
                        futs.append(pool.submit(download_part, url, s, e,
                                                part_paths[idx], tracker, post_log))
                    for f in futs:
                        try:
                            results.append(f.result())
                        except PermanentError as ex:
                            fatal = ex
                            results.append(False)
                        except RangeIgnored:
                            range_ignored = True
                            results.append(False)
                        except Exception:
                            results.append(False)

                if fatal is not None:
                    return "failed", str(fatal)
                if stop_event.is_set():
                    return stopped()
                if range_ignored:
                    post_log(f"[WARN] Server ignored range requests; "
                             f"using a single connection for {fname}")
                    supports_range = False
                    cleanup_partials(dest_dir, fname)
                    tracker.set_file_abs(0)
                    continue
                if len(results) == len(ranges) and all(results):
                    merge_parts(part_paths, final_path, total)
                    return finish_ok()

                tracker.set_file_abs(sum_sizes(part_paths))
                post_log(f"[WARN] Incomplete segmented download for {fname}, "
                         f"retrying (attempt {attempt}/{max_retries})")
                sleep_backoff(attempt, stop_event)
                continue

            # --- single connection ---
            purge_foreign_parts(dest_dir, fname, [])    # old segment parts of this file
            ok = download_single_stream(url, final_path, total if total_known else None,
                                        tracker, post_log)
            if ok:
                return finish_ok()
            if stop_event.is_set():
                return stopped()

            tmp = final_path + ".part"
            tracker.set_file_abs(os.path.getsize(tmp) if os.path.exists(tmp) else 0)
            post_log(f"[WARN] Download failed for {fname}, "
                     f"retrying (attempt {attempt}/{max_retries})")
            sleep_backoff(attempt, stop_event)

        except PermanentError as e:
            return "failed", str(e)
        except Exception as e:
            if isinstance(e, OSError) and getattr(e, "errno", None) == errno.ENOSPC:
                return "failed", DISK_FULL_DETAIL
            post_log(f"[WARN] File-level error for {fname}: {e} "
                     f"(attempt {attempt}/{max_retries})")
            sleep_backoff(attempt, stop_event)

    return "failed", f"Failed after {max_retries} attempts"


# --- study-area (NetcdfSubset) downloads, new in 1.1 ---

def _netcdf_signature_ok(path: str) -> bool:
    """True when the file starts like a NetCDF3 ('CDF') or NetCDF4/HDF5 file."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(4)
    except OSError:
        return False
    return head.startswith(b"\x89HDF") or head[:3] == b"CDF"


def _remove_quiet(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def _body_snippet(resp: requests.Response, limit: int = 300) -> str:
    """Short plain-text excerpt of an (error) response body, never raises."""
    try:
        chunk = next(resp.iter_content(chunk_size=limit * 4), b"")
        text = chunk.decode("utf-8", "replace")
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return shorten(text, limit)
    except Exception:
        return ""


def download_subset_file(url: str, dest_dir: str, fname: str,
                         tracker: ProgressTracker, post_log,
                         max_retries: int = MAX_RETRIES_PER_SUBSET_FILE) -> Tuple[str, str]:
    """Download one NetcdfSubset (NCSS) result. Returns (status, detail) like
    download_file_robust.

    The server builds the answer on the fly, so there is no Range support and
    often no Content-Length: one connection, written to '<name>.part' and
    renamed when complete and valid. A failed or stopped attempt leaves nothing
    behind and the file is simply requested again."""
    os.makedirs(dest_dir, exist_ok=True)
    final_path = os.path.join(dest_dir, fname)
    tmp = final_path + ".part"

    if os.path.exists(final_path):
        if _netcdf_signature_ok(final_path):
            return "skipped", final_path
        post_log(f"[WARN] Existing file is not valid NetCDF; renamed to .bad and "
                 f"downloading again: {fname}")
        try:
            os.replace(final_path, final_path + ".bad")
        except OSError:
            pass

    session = get_session()
    attempt = 0
    free_retries = 0

    while attempt < max_retries:
        attempt += 1
        if stop_event.is_set():
            _remove_quiet(tmp)
            return "stopped", "Stopped by user"
        gen0 = _pause_generation()
        try:
            tracker.set_file_total(None)
            tracker.set_file_abs(0)
            tracker.set_phase("waiting for the server")

            with session.get(url, headers=HEADERS, stream=True,
                             timeout=(REQUEST_TIMEOUT, NCSS_READ_TIMEOUT),
                             allow_redirects=True) as r:
                code = r.status_code
                if code in PERMANENT_STATUS:
                    detail = _body_snippet(r) or "request rejected by the server"
                    raise PermanentError(f"HTTP {code}: {detail}")
                if code in TRANSIENT_STATUS:
                    raise TransientHTTPError(code, retry_after_seconds(r))
                if code != 200:
                    raise RuntimeError(f"Unexpected HTTP {code}")

                ctype = (r.headers.get("Content-Type") or "").lower()
                if ctype.startswith("text/") or "html" in ctype:
                    detail = _body_snippet(r) or ctype
                    raise PermanentError(f"The server sent text instead of NetCDF: {detail}")

                cl = r.headers.get("Content-Length")
                enc = (r.headers.get("Content-Encoding") or "").lower()
                expected = int(cl) if (cl and cl.isdigit() and enc in ("", "identity")) else None
                tracker.set_file_total(expected)
                tracker.set_phase("receiving")

                with open(tmp, "wb") as f:
                    wrote = stream_to_file(r, f, tracker)

            if stop_event.is_set():
                _remove_quiet(tmp)
                return "stopped", "Stopped by user"
            if wrote == 0:
                raise IOError("Empty response")
            if expected is not None and wrote != expected:
                raise IOError(f"Incomplete response ({wrote}/{expected} bytes)")
            if not _netcdf_signature_ok(tmp):
                raise IOError("Response is not a valid NetCDF/HDF5 file")
            os.replace(tmp, final_path)
            return "ok", final_path

        except PermanentError as e:
            _remove_quiet(tmp)
            return "failed", str(e)
        except Exception as e:
            _remove_quiet(tmp)
            if isinstance(e, OSError) and getattr(e, "errno", None) == errno.ENOSPC:
                return "failed", DISK_FULL_DETAIL
            if free_retries < MAX_FREE_RETRIES and _pause_generation() != gen0:
                # The connection most likely died during a long pause: ask again
                # without spending one of the retry attempts.
                free_retries += 1
                attempt -= 1
                post_log(f"[INFO] Connection lost after a long pause ({fname}); reconnecting.")
                stop_event.wait(1.0)
                continue
            if attempt >= max_retries:
                post_log(f"[WARN] Download failed ({fname}): {e}")
                return "failed", f"Failed after {max_retries} attempts: {e}"
            post_log(f"[WARN] Download error ({fname}): {e} (retry {attempt}/{max_retries})")
            sleep_backoff(attempt, stop_event, min_wait=_retry_wait_hint(e))

    return "failed", f"Failed after {max_retries} attempts"


def run_download_queue(items: List[Dict], workers: int, segments: int, delete_partial: bool,
                       tracker: ProgressTracker, post_ui: Callable[[dict], None],
                       post_log: Callable[[str], None]) -> dict:
    """Download every item in order. Shared by the GUI and the CLI. A 'Disk full'
    failure ends the whole queue instead of failing every remaining file.
    Items with it['subset'] set are NetcdfSubset requests (one connection each);
    all other items are whole-file downloads."""
    ok = skipped = failed = 0
    stopped = False
    disk_full = False
    attempted = 0
    for idx, it in enumerate(items, 1):
        if stop_event.is_set():
            stopped = True
            post_log("[INFO] Stop requested. Ending downloads.")
            break

        attempted = idx
        flagged = bool(it.get("exists"))
        tracker.begin_file(flagged)
        post_ui({"type": "dl_file_start", "index": idx, "filename": it["filename"],
                 "total": len(items)})
        try:
            if it.get("subset"):
                status, detail = download_subset_file(
                    it["url"], it["out_dir"], it["filename"], tracker, post_log)
            else:
                status, detail = download_file_robust(
                    it["url"], it["out_dir"], segments=segments, workers=workers,
                    max_retries=MAX_RETRIES_PER_FILE, tracker=tracker,
                    post_log=post_log, cleanup_on_stop=delete_partial)
        except Exception as e:
            status, detail = "failed", f"Unexpected error: {e}"
            file_log("[ERR] Unexpected error while downloading "
                     f"{it['filename']}:\n{traceback.format_exc()}")

        if status == "ok":
            ok += 1
            post_log(f"[OK] {detail}")
        elif status == "skipped":
            skipped += 1
            post_log(f"[SKIP] Already exists: {detail}")
        elif status == "stopped":
            stopped = True
        else:
            failed += 1
            post_log(f"[ERR] {it['filename']}: {detail}")
            if detail == DISK_FULL_DETAIL:
                disk_full = True
                post_log("[ERR] Disk full: the output drive has no free space. The queue "
                         "was stopped; free some space and start again to continue.")

        tracker.end_file(status, flagged)
        post_ui({"type": "dl_file_done", "index": idx, "status": status})
        if stopped or disk_full:
            break

    return {"ok": ok, "skipped": skipped, "failed": failed,
            "stopped": stopped or stop_event.is_set(), "disk_full": disk_full,
            "not_attempted": max(0, len(items) - attempted)}


# ============================================================
# UI WIDGETS
# ============================================================

class SelectList(ttk.Frame):
    """Searchable list for single or multiple selection.

    Items are (key, label) pairs. The selection is stored by key, so it is kept
    while the list is filtered with the search box."""

    def __init__(self, parent, multi: bool = False,
                 on_change: Optional[Callable[[], None]] = None,
                 on_activate: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.multi = multi
        self.on_change = on_change
        self.on_activate = on_activate
        self._items: List[Tuple[str, str]] = []
        self._visible: List[str] = []
        self._selected: Set[str] = set()

        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 6))
        ttk.Label(top, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(top, text="Clear", width=7,
                   command=lambda: self.search_var.set("")).pack(side="left")

        self.msg_var = tk.StringVar()
        self.msg_label = ttk.Label(self, textvariable=self.msg_var, style="Hint.TLabel",
                                   wraplength=760, justify="left")

        self._mid = ttk.Frame(self)
        self._mid.pack(fill="both", expand=True)
        self.lb = tk.Listbox(
            self._mid, selectmode="multiple" if multi else "browse",
            exportselection=False, activestyle="none", borderwidth=1, relief="solid",
            highlightthickness=0, selectbackground="#bfdbfe", selectforeground=TEXT,
            background="white")
        sb = ttk.Scrollbar(self._mid, orient="vertical", command=self.lb.yview)
        self.lb.configure(yscrollcommand=sb.set)
        self.lb.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        self._mid.rowconfigure(0, weight=1)
        self._mid.columnconfigure(0, weight=1)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", pady=(6, 0))
        self.info_var = tk.StringVar(value="")
        ttk.Label(bottom, textvariable=self.info_var, style="Hint.TLabel").pack(side="left")
        self._btns: List[ttk.Button] = []
        if multi:
            b_clear = ttk.Button(bottom, text="Clear selection", command=self.clear_selection)
            b_clear.pack(side="right")
            b_all = ttk.Button(bottom, text="Select all shown", command=self.select_all_visible)
            b_all.pack(side="right", padx=(0, 6))
            self._btns = [b_clear, b_all]

        self.search_var.trace_add("write", lambda *_: self._apply_filter())
        self.lb.bind("<<ListboxSelect>>", self._on_listbox_select)
        if on_activate:
            self.lb.bind("<Double-Button-1>", self._on_double)
            self.lb.bind("<Return>", self._on_double)

    # --- public API ---
    def set_items(self, items: List[Tuple[str, str]]):
        self._items = sorted(items, key=lambda kv: kv[0].lower())
        keys = {k for k, _ in self._items}
        self._selected &= keys
        self._apply_filter()

    def count(self) -> int:
        return len(self._items)

    def set_message(self, text: str, error: bool = False):
        self.msg_var.set(text)
        if text:
            self.msg_label.configure(foreground=RED if error else MUTED)
            if not self.msg_label.winfo_manager():
                self.msg_label.pack(fill="x", pady=(0, 6), before=self._mid)
        else:
            self.msg_label.pack_forget()

    def get_selected(self) -> List[str]:
        return [k for k, _ in self._items if k in self._selected]

    def select_keys(self, keys: List[str]):
        all_keys = {k for k, _ in self._items}
        self._selected = set(keys) & all_keys
        self._refresh()

    def select_all_visible(self):
        self._selected.update(self._visible)
        self._refresh()
        self._notify()

    def clear_selection(self):
        self._selected.clear()
        self._refresh()
        self._notify()

    def set_enabled(self, enabled: bool):
        """Enable / disable user interaction (the items can still be replaced)."""
        self.lb.configure(state="normal" if enabled else "disabled")
        for b in self._btns:
            b.configure(state="normal" if enabled else "disabled")

    # --- internals ---
    def _apply_filter(self):
        text = self.search_var.get().strip().lower()
        self._visible = [k for k, label in self._items if not text or text in label.lower()]
        self._refresh()

    def _refresh(self):
        labels = dict(self._items)
        state = str(self.lb.cget("state"))
        self.lb.configure(state="normal")       # a disabled Listbox ignores changes
        self.lb.delete(0, "end")
        first_selected = None
        for i, key in enumerate(self._visible):
            self.lb.insert("end", labels.get(key, key))
            if key in self._selected:
                self.lb.selection_set(i)
                if first_selected is None:
                    first_selected = i
        if first_selected is not None:
            self.lb.see(first_selected)
        self.lb.configure(state=state)
        self._update_info()

    def _update_info(self):
        total = len(self._items)
        shown = len(self._visible)
        txt = f"{shown} shown of {total}" if shown != total else f"{total} item(s)"
        if self.multi:
            txt += f"   \u2022   {len(self._selected)} selected"
        self.info_var.set(txt)

    def _on_listbox_select(self, _e=None):
        idx = set(self.lb.curselection())
        if self.multi:
            for i, key in enumerate(self._visible):
                if i in idx:
                    self._selected.add(key)
                else:
                    self._selected.discard(key)
        elif idx:
            self._selected = {self._visible[min(idx)]}
        self._update_info()
        self._notify()

    def _on_double(self, _e=None):
        self._on_listbox_select()
        if self.on_activate and self._selected:
            self.on_activate()

    def _notify(self):
        if self.on_change:
            self.on_change()


class StepSidebar(tk.Frame):
    """Clickable list of wizard steps with a one-line summary under each, and
    (optionally) the workflow switch at the bottom."""

    def __init__(self, parent, steps: List[str], on_click: Callable[[int], None],
                 flow_var=None, on_flow: Optional[Callable[[], None]] = None):
        super().__init__(parent, bg=SIDEBAR_BG, width=250)
        self.pack_propagate(False)
        self.flow_buttons: List[tk.Radiobutton] = []
        if flow_var is not None:
            box = tk.Frame(self, bg=SIDEBAR_BG)
            box.pack(side="bottom", fill="x", padx=14, pady=(0, 10))
            tk.Frame(box, bg=BORDER, height=1).pack(fill="x", pady=(0, 8))
            tk.Label(box, text="WORKFLOW", bg=SIDEBAR_BG, fg=MUTED,
                     font=(FONT_FAMILY, 9, "bold")).pack(anchor="w", pady=(0, 2))
            for value, text, desc in (
                    (FLOW_MODEL, "Models first",
                     "Pick the models, then the scenario, ensembles and variables. Best "
                     "when you know which models you want."),
                    (FLOW_VARIABLE, "Variables first",
                     "Pick the variables and the scenario; every model that has them is "
                     "found and selected for you. Best for 'tasmax from all models'.")):
                rb = tk.Radiobutton(box, text=text, value=value, variable=flow_var,
                                    command=on_flow, bg=SIDEBAR_BG,
                                    activebackground=SIDEBAR_BG, selectcolor="white",
                                    anchor="w", highlightthickness=0, bd=0,
                                    font=(FONT_FAMILY, 10, "bold"))
                rb.pack(fill="x", anchor="w", pady=(4, 0))
                self.flow_buttons.append(rb)
                tk.Label(box, text=desc, wraplength=212, justify="left", bg=SIDEBAR_BG,
                         fg=MUTED, font=(FONT_FAMILY, 9)).pack(anchor="w", padx=(22, 0))
        tk.Label(self, text="STEPS", bg=SIDEBAR_BG, fg=MUTED,
                 font=(FONT_FAMILY, 9, "bold")).pack(anchor="w", padx=20, pady=(18, 8))
        self.items: List[dict] = []
        for i, name in enumerate(steps):
            row = tk.Frame(self, bg=SIDEBAR_BG)
            row.pack(fill="x", padx=8, pady=2)
            badge = tk.Label(row, text=str(i + 1), width=3, bg=SIDEBAR_BG, fg=MUTED,
                             font=(FONT_FAMILY, 11, "bold"))
            badge.pack(side="left", padx=(8, 4), pady=6)
            text_box = tk.Frame(row, bg=SIDEBAR_BG)
            text_box.pack(side="left", fill="x", expand=True)
            title = tk.Label(text_box, text=name, anchor="w", bg=SIDEBAR_BG, fg=TEXT,
                             font=(FONT_FAMILY, 11, "bold"))
            title.pack(fill="x")
            sub = tk.Label(text_box, text="", anchor="w", bg=SIDEBAR_BG, fg=MUTED,
                           font=(FONT_FAMILY, 9))
            sub.pack(fill="x")
            widgets = [row, badge, text_box, title, sub]
            for w in widgets:
                w.bind("<Button-1>", lambda _e, idx=i: on_click(idx))
            self.items.append({"row": row, "badge": badge, "box": text_box,
                               "title": title, "sub": sub, "widgets": widgets})

    def set_names(self, names: List[str]):
        for it, name in zip(self.items, names):
            it["title"].configure(text=name)

    def update_state(self, current: int, max_step: int, summaries: List[str], enabled: bool):
        for rb in self.flow_buttons:
            rb.configure(state="normal" if enabled else "disabled")
        for i, it in enumerate(self.items):
            is_cur = (i == current)
            reachable = enabled and i <= max_step
            done = i < max_step
            bg = ACTIVE_BG if is_cur else SIDEBAR_BG
            for w in it["widgets"]:
                w.configure(bg=bg, cursor="hand2" if (reachable and not is_cur) else "arrow")
            it["badge"].configure(
                text="\u2713" if done else str(i + 1),
                fg=ACCENT if is_cur else (GREEN if done else MUTED))
            it["title"].configure(fg=TEXT if (reachable or is_cur) else MUTED)
            it["sub"].configure(text=shorten(summaries[i], 30) if summaries[i] else "")


class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f"About {APP_NAME}")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(parent)

        frame = ttk.Frame(self, padding=24)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="NASA NEX-GDDP-CMIP6 Downloader", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text=f"Version {APP_VERSION}", style="Sub.TLabel").pack(anchor="w", pady=(0, 12))
        ttk.Label(
            frame, wraplength=440, justify="left",
            text=("Download high-resolution (0.25\u00b0) daily climate projections from the "
                  "NASA NEX-GDDP-CMIP6 dataset in a few simple steps, as complete global "
                  "files or for a study area only, with pause / resume and automatic "
                  "retries.")
        ).pack(anchor="w", pady=(0, 14))

        info = ttk.LabelFrame(frame, text="Author", padding=12)
        info.pack(fill="x", pady=(0, 12))
        for r, (k, v) in enumerate((("Name", AUTHOR_NAME), ("Email", AUTHOR_EMAIL),
                                    ("GitHub", GITHUB_URL), ("License", "MIT"))):
            ttk.Label(info, text=k + ":", font=(FONT_FAMILY, 10, "bold"), width=9).grid(
                row=r, column=0, sticky="w", pady=2)
            ttk.Label(info, text=v).grid(row=r, column=1, sticky="w", pady=2)

        ttk.Label(
            frame, wraplength=440, justify="left", style="Hint.TLabel",
            text=("Data attribution: this tool downloads data from NASA's NEX-GDDP-CMIP6 "
                  "dataset. Please follow NASA's data usage policy and cite the dataset "
                  "in your publications.")
        ).pack(anchor="w", pady=(0, 12))

        btns = ttk.Frame(frame)
        btns.pack(fill="x")
        ttk.Button(btns, text="Dataset website",
                   command=lambda: webbrowser.open(DATASET_URL)).pack(side="left")
        ttk.Button(btns, text="Project on GitHub",
                   command=lambda: webbrowser.open(REPO_URL)).pack(side="left", padx=8)
        ttk.Button(btns, text="Close", command=self.destroy).pack(side="right")

        self.bind("<Escape>", lambda _e: self.destroy())
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.grab_set()


# ============================================================
# MAIN APPLICATION
# ============================================================

class App(tk.Tk):
    LAST = 6        # position of the Download step (the same in both workflows)

    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w = min(1180, max(600, sw - 80))
        h = min(800, max(480, sh - 120))
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2 - 20)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(min(1020, w), min(700, h))
        try:
            self.iconbitmap(default="icon.ico")
        except Exception:
            pass

        self._setup_style()

        # thread -> UI queue
        self.uiq: "queue.Queue[dict]" = queue.Queue()

        # catalog data (None = not loaded yet)
        # models:        list of model entries
        # scenarios:     {model: [scenario entries]}
        # ensembles:     {model: [ensemble entries]}
        # params_by_model: {model: {ensemble: {variable: entry}}}
        self.models: Optional[List[Dict[str, Optional[str]]]] = None
        self.scenarios: Optional[Dict[str, List[Dict[str, Optional[str]]]]] = None
        self.ensembles: Optional[Dict[str, List[Dict[str, Optional[str]]]]] = None
        self.params_by_model: Optional[Dict[str, Dict[str, Dict[str, Dict[str, Optional[str]]]]]] = None

        # selections
        self.sel_models: List[str] = []
        self.sel_scenario: Optional[str] = None
        self.sel_ensembles: List[str] = []
        self.sel_params: List[str] = []
        self.download_items: List[Dict] = []

        # wizard state: `order` lists the page ids in the order of the workflow;
        # `pos` is the position that is showing, `max_pos` the furthest one reached.
        self.flow = FLOW_MODEL
        self.order: List[int] = list(FLOW_ORDERS[FLOW_MODEL])
        self.pos = 0
        self.max_pos = 0
        self._load_failures = 0            # models that could not be scanned (variables first)

        # background tasks
        self._cat_cancel: Optional[threading.Event] = None
        self._cat_gen = 0
        self._cat_busy = False
        self._cat_kind = ""
        self._refresh_flag = False
        self._queue_version_text = ""
        self._queue_area_text = ""         # e.g. "N38.5 S36.5 W44 E46.5" for a study-area queue
        self.download_thread: Optional[threading.Thread] = None
        self.is_downloading = False
        self.is_paused = False
        self.closing = False
        self._suppress_traces = True
        self._space_checking = False       # free-space probe running (see start_download)
        self._progress_err_logged = False  # log a progress-refresh error only once

        # widgets created later that other methods need
        self.area_entries: List[ttk.Entry] = []
        self.sp_workers = None
        self.sp_segments = None
        self.models_sub = None
        self.var_sub = None
        self.var_common_cb = None
        self._cur_file_name = ""
        self._dl_subset = False            # the running queue is a study-area queue
        self._samples: "deque[Tuple[float, int]]" = deque()   # (time, bytes) for the speed window

        # stats
        self.tracker = ProgressTracker()
        self._speed = 0.0
        self._last_sample_ts = 0.0
        self._last_sample_bytes = 0
        self._file_bar_mode = "determinate"

        resume_event.set()
        stop_event.clear()

        cfg = self._read_config()
        cfg_version = cfg.get("version")
        if not isinstance(cfg_version, str) or not cfg_version.strip():
            cfg_version = DEFAULT_VERSION_FILTER

        def cfg_text(key: str) -> str:
            v = cfg.get(key)
            return "" if v is None else str(v)

        cfg_area = cfg.get("area_mode")
        if cfg_area not in (AREA_GLOBE, AREA_SUBSET):
            cfg_area = AREA_GLOBE
        cfg_flow = cfg.get("flow")
        if cfg_flow not in FLOW_ORDERS:
            cfg_flow = FLOW_MODEL
        self.flow = cfg_flow
        self.order = list(FLOW_ORDERS[cfg_flow])
        self.flow_var = tk.StringVar(value=cfg_flow)
        self.out_dir_var = tk.StringVar(value=cfg.get("out_dir") or os.path.abspath("cmip6_downloads"))
        self.y0_var = tk.StringVar(value=str(MIN_YEAR))
        self.y1_var = tk.StringVar(value=str(MAX_YEAR))
        self.version_var = tk.StringVar(value=cfg_version)
        self.workers_var = tk.StringVar(value=str(cfg.get("workers", DEFAULT_WORKERS)))
        self.segments_var = tk.StringVar(value=str(cfg.get("segments", DEFAULT_SEGMENTS)))
        self.delete_partial_var = tk.BooleanVar(value=bool(cfg.get("delete_partial", False)))
        self.common_only_var = tk.BooleanVar(value=False)
        self.ens_common_only_var = tk.BooleanVar(value=False)
        self.all_ens_var = tk.BooleanVar(value=bool(cfg.get("all_ens", False)))
        self.area_mode_var = tk.StringVar(value=cfg_area)
        self.north_var = tk.StringVar(value=cfg_text("north"))
        self.south_var = tk.StringVar(value=cfg_text("south"))
        self.west_var = tk.StringVar(value=cfg_text("west"))
        self.east_var = tk.StringVar(value=cfg_text("east"))
        self.area_msg_var = tk.StringVar(value="")
        self.adv_note_var = tk.StringVar(value="")

        self._build_menu()
        self._build_ui()
        self._bind_shortcuts()

        for var in (self.y0_var, self.y1_var, self.version_var, self.out_dir_var):
            var.trace_add("write", self._on_options_changed)
        for var in (self.area_mode_var, self.north_var, self.south_var,
                    self.west_var, self.east_var):
            var.trace_add("write", self._on_area_changed)
        self._suppress_traces = False

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(UI_TICK_MS, self._tick)

        self._log(f"[INFO] Welcome to {APP_NAME} v{APP_VERSION}.")
        self._apply_flow_texts()
        self._show_step(0)

    # ------------------------------------------------------------
    # Error reporting
    # ------------------------------------------------------------

    def report_callback_exception(self, exc, val, tb):
        """Tk calls this when a callback raises. Log it (file + activity log)
        instead of losing it; the program keeps running."""
        try:
            text = "".join(traceback.format_exception(exc, val, tb))
        except Exception:
            text = f"{exc}: {val}"
        self._safe_log("[ERR] Unexpected UI error (the program keeps running):\n" + text)

    def _safe_log(self, msg: str):
        """Log without ever raising (usable from error handlers)."""
        file_log(msg)
        try:
            self._log(msg)
        except Exception:
            pass

    # ------------------------------------------------------------
    # Style
    # ------------------------------------------------------------

    def _setup_style(self):
        global FONT_FAMILY
        available = set(tkfont.families(self))
        for fam in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Ubuntu",
                    "Noto Sans", "DejaVu Sans", "Arial"):
            if fam in available:
                FONT_FAMILY = fam
                break
        else:
            FONT_FAMILY = tkfont.nametofont("TkDefaultFont").actual("family")
        for name in ("TkDefaultFont", "TkTextFont", "TkHeadingFont"):
            try:
                tkfont.nametofont(name).configure(family=FONT_FAMILY, size=10)
            except tk.TclError:
                pass

        self.configure(bg=BG)
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        f = FONT_FAMILY
        s.configure(".", background=BG, foreground=TEXT, font=(f, 10))
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=TEXT)
        s.configure("TLabelframe", background=BG, bordercolor=BORDER)
        s.configure("TLabelframe.Label", background=BG, foreground=TEXT, font=(f, 10, "bold"))
        s.configure("TCheckbutton", background=BG)
        s.map("TCheckbutton", background=[("active", BG)])
        s.configure("TRadiobutton", background=BG)
        s.map("TRadiobutton", background=[("active", BG)])
        s.configure("TButton", padding=(12, 6))
        s.configure("Primary.TButton", background=ACCENT, foreground="white",
                    font=(f, 10, "bold"), padding=(20, 8), borderwidth=0)
        s.map("Primary.TButton",
              background=[("disabled", "#bfdbfe"), ("pressed", "#1e40af"), ("active", "#1d4ed8")],
              foreground=[("disabled", "#ffffff")])
        s.configure("Title.TLabel", font=(f, 18, "bold"))
        s.configure("Sub.TLabel", foreground=MUTED, font=(f, 10))
        s.configure("Hint.TLabel", foreground=MUTED, font=(f, 9))
        s.configure("Ctx.TLabel", foreground=ACCENT, font=(f, 10, "bold"))
        s.configure("Treeview", rowheight=24, background="white", fieldbackground="white")
        s.configure("Treeview.Heading", font=(f, 10, "bold"))
        s.configure("Horizontal.TProgressbar", background=ACCENT, troughcolor="#e2e8f0",
                    bordercolor="#e2e8f0", lightcolor=ACCENT, darkcolor=ACCENT)

    # ------------------------------------------------------------
    # Config persistence
    # ------------------------------------------------------------

    def _read_config(self) -> dict:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_config(self):
        data = {
            "out_dir": self.out_dir_var.get().strip(),
            "version": self.version_var.get(),
            "workers": self._read_int(self.workers_var, 1, 16, DEFAULT_WORKERS),
            "segments": self._read_int(self.segments_var, 1, 32, DEFAULT_SEGMENTS),
            "delete_partial": bool(self.delete_partial_var.get()),
            "area_mode": self.area_mode_var.get(),
            "north": self.north_var.get().strip(),
            "south": self.south_var.get().strip(),
            "west": self.west_var.get().strip(),
            "east": self.east_var.get().strip(),
            "flow": self.flow,
            "all_ens": bool(self.all_ens_var.get()),
        }
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
        except Exception:
            pass

    @staticmethod
    def _read_int(var: tk.StringVar, lo: int, hi: int, default: int) -> int:
        try:
            value = int(var.get().strip())
        except (ValueError, tk.TclError):
            return default
        return max(lo, min(hi, value))

    # ------------------------------------------------------------
    # Menu / shortcuts
    # ------------------------------------------------------------

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open output folder", command=self.open_output_folder)
        file_menu.add_command(label="Clear catalog cache", command=self._clear_catalog_cache)
        file_menu.add_separator()
        file_menu.add_command(label="Quit\tCtrl+Q", command=self.on_close)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show / hide activity log\tCtrl+L", command=self._toggle_log)
        view_menu.add_command(label="Refresh current list\tF5", command=self._refresh_current)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Quick guide\tF1", command=self.show_guide)
        help_menu.add_command(label="Keyboard shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="Dataset website", command=lambda: webbrowser.open(DATASET_URL))
        help_menu.add_separator()
        help_menu.add_command(label="About", command=lambda: AboutDialog(self))

    def _bind_shortcuts(self):
        self.bind("<F1>", lambda _e: self.show_guide())
        self.bind("<F5>", lambda _e: self._refresh_current())
        self.bind("<Control-q>", lambda _e: self.on_close())
        self.bind("<Control-l>", lambda _e: self._toggle_log())
        self.bind("<Alt-Right>", lambda _e: self._next_if_possible())
        self.bind("<Alt-Left>", lambda _e: self._back())

    def show_guide(self):
        messagebox.showinfo("Quick guide", QUICK_GUIDE, parent=self)

    def show_shortcuts(self):
        messagebox.showinfo("Keyboard shortcuts", SHORTCUTS, parent=self)

    # ------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------

    def _build_ui(self):
        # status bar (packed first so it stays at the very bottom)
        status = tk.Frame(self, bg=SIDEBAR_BG, highlightbackground=BORDER, highlightthickness=1)
        status.pack(side="bottom", fill="x")
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(status, textvariable=self.status_var, bg=SIDEBAR_BG, fg=TEXT,
                 anchor="w", padx=12, pady=5).pack(side="left", fill="x", expand=True)
        self.btn_log = ttk.Button(status, text="Show log \u25B4", command=self._toggle_log)
        self.btn_log.pack(side="right", padx=8, pady=3)
        self.btn_cancel = ttk.Button(status, text="Cancel", command=self._cancel_clicked)
        self.busy_bar = ttk.Progressbar(status, mode="indeterminate", length=120)
        # busy bar / cancel button are packed only while a catalog task runs

        # header
        header = tk.Frame(self, bg=HEADER_BG)
        header.pack(side="top", fill="x")
        tk.Label(header, text="NASA NEX-GDDP-CMIP6 Downloader", bg=HEADER_BG, fg="white",
                 font=(FONT_FAMILY, 15, "bold")).pack(side="left", padx=20, pady=(12, 12))
        tk.Label(header, text="Download downscaled climate projections in a few simple steps",
                 bg=HEADER_BG, fg="#93c5fd", font=(FONT_FAMILY, 10)).pack(side="left", pady=(14, 12))
        tk.Label(header, text=f"v{APP_VERSION}", bg=HEADER_BG, fg="#93c5fd").pack(
            side="right", padx=20)

        # activity log (hidden by default)
        self.log_frame = ttk.LabelFrame(self, text="Activity log", padding=6)
        self.log_text = tk.Text(self.log_frame, height=8, wrap="word", state="normal")
        log_sb = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_sb.set)
        log_btns = ttk.Frame(self.log_frame)
        log_btns.pack(side="right", fill="y", padx=(6, 0))
        ttk.Button(log_btns, text="Clear", command=self._clear_log).pack()
        log_sb.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)
        self._log_visible = False

        # body
        self.body = ttk.Frame(self)
        self.body.pack(side="top", fill="both", expand=True)

        self.sidebar = StepSidebar(self.body, self._step_names(), self._sidebar_clicked,
                                   self.flow_var, self._on_workflow_changed)
        self.sidebar.pack(side="left", fill="y")
        tk.Frame(self.body, bg=BORDER, width=1).pack(side="left", fill="y")

        main = ttk.Frame(self.body, padding=(26, 20, 26, 12))
        main.pack(side="left", fill="both", expand=True)

        # navigation bar
        nav = ttk.Frame(main)
        nav.pack(side="bottom", fill="x", pady=(12, 0))
        self.btn_back = ttk.Button(nav, text="\u2190 Back", command=self._back)
        self.btn_back.pack(side="left")
        self.btn_next = ttk.Button(nav, text="Next \u2192", style="Primary.TButton",
                                   command=self._advance)
        self.btn_next.pack(side="right")
        self.next_hint_var = tk.StringVar(value="")
        ttk.Label(nav, textvariable=self.next_hint_var, style="Hint.TLabel").pack(
            side="right", padx=14)

        # pages (stacked)
        container = ttk.Frame(main)
        container.pack(side="top", fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        n_steps = len(PAGE_NAMES)
        self.pages: List[ttk.Frame] = []
        self.ctx_vars: List[tk.StringVar] = [tk.StringVar() for _ in range(n_steps)]
        for _ in range(n_steps):
            page = ttk.Frame(container)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages.append(page)

        self._build_page_model(self.pages[P_MODELS])
        self._build_page_scenario(self.pages[P_SCENARIO])
        self._build_page_ensembles(self.pages[P_ENSEMBLES])
        self._build_page_variables(self.pages[P_VARIABLES])
        self._build_page_area(self.pages[P_AREA])
        self._build_page_options(self.pages[P_OPTIONS])
        self._build_page_download(self.pages[P_DOWNLOAD])

    def _page_header(self, page, title: str, subtitle: str, ctx_index: Optional[int] = None):
        ttk.Label(page, text=title, style="Title.TLabel").pack(anchor="w")
        sub = ttk.Label(page, text=subtitle, style="Sub.TLabel", wraplength=860,
                        justify="left")
        sub.pack(anchor="w", pady=(2, 8))
        if ctx_index is not None:
            ttk.Label(page, textvariable=self.ctx_vars[ctx_index], style="Ctx.TLabel",
                      wraplength=860, justify="left").pack(anchor="w", pady=(0, 8))
        return sub

    # --- page: models ---
    def _build_page_model(self, page):
        # the subtitle depends on the workflow: see _apply_flow_texts()
        self.models_sub = self._page_header(page, "Choose climate models", "", P_MODELS)
        self.model_list = SelectList(page, multi=True, on_change=self._on_model_change)
        self.model_list.pack(fill="both", expand=True)
        row = ttk.Frame(page)
        row.pack(fill="x", pady=(8, 0))
        ttk.Button(row, text="Refresh list", command=self._refresh_current).pack(side="left")

    # --- page: scenario ---
    def _build_page_scenario(self, page):
        self._page_header(page, "Choose a scenario",
                          "'historical' covers 1950-2014. The SSP scenarios are future "
                          "projections (2015-2100) under different emission pathways. The "
                          "number shows how many models have the scenario; models without "
                          "it are skipped.", P_SCENARIO)
        self.scenario_list = SelectList(page, multi=False, on_change=self._on_scenario_change,
                                        on_activate=self._next_if_possible)
        self.scenario_list.pack(fill="both", expand=True)
        self.scenario_hint_var = tk.StringVar(value="")
        row = ttk.Frame(page)
        row.pack(fill="x", pady=(8, 0))
        ttk.Button(row, text="Refresh list", command=self._refresh_current).pack(side="left")
        ttk.Label(row, textvariable=self.scenario_hint_var, style="Ctx.TLabel").pack(
            side="left", padx=14)

    # --- page: ensembles ---
    def _build_page_ensembles(self, page):
        self._page_header(page, "Choose ensemble members",
                          "An ensemble (rXiXpXfX) is one realization of the model run. "
                          "Most users only need r1i1p1f1. Click items to select or deselect "
                          "them, or tick the box below to take every ensemble each model "
                          "has. The number shows how many models have each ensemble.",
                          P_ENSEMBLES)
        ttk.Checkbutton(page, text="All ensembles of every model  (each model downloads "
                                   "all the ensembles it has)",
                        variable=self.all_ens_var,
                        command=self._on_all_ens_toggled).pack(anchor="w", pady=(0, 8))
        self.ensemble_list = SelectList(page, multi=True, on_change=self._on_ensemble_change)
        self.ensemble_list.pack(fill="both", expand=True)
        row = ttk.Frame(page)
        row.pack(fill="x", pady=(8, 0))
        ttk.Button(row, text="Refresh list", command=self._refresh_current).pack(side="left")
        ttk.Checkbutton(row, text="Only show ensembles shared by every selected model",
                        variable=self.ens_common_only_var,
                        command=self._refresh_ensemble_list).pack(side="left", padx=14)

    # --- page: variables ---
    def _build_page_variables(self, page):
        # the subtitle depends on the workflow: see _apply_flow_texts()
        self.var_sub = self._page_header(page, "Choose climate variables", "", P_VARIABLES)
        self.var_list = SelectList(page, multi=True, on_change=self._on_variable_change)
        self.var_list.pack(fill="both", expand=True)
        row = ttk.Frame(page)
        row.pack(fill="x", pady=(8, 0))
        ttk.Button(row, text="Refresh list", command=self._refresh_current).pack(side="left")
        self.var_common_cb = ttk.Checkbutton(row, text="Only show variables shared by every model",
                                             variable=self.common_only_var,
                                             command=self._refresh_variable_list)
        self.var_common_cb.pack(side="left", padx=14)

    # --- page 5: area (new in 1.1) ---
    def _build_page_area(self, page):
        self._page_header(page, "Choose the area",
                          "Download complete global files, or only a rectangular study area. "
                          "For a study area the NASA server cuts the data first, so every "
                          "file is much smaller and downloads faster.", 4)

        mode = ttk.LabelFrame(page, text="Area", padding=12)
        mode.pack(fill="x", pady=(0, 10))
        ttk.Radiobutton(mode, text="Whole globe  (complete files, as in earlier versions)",
                        value=AREA_GLOBE, variable=self.area_mode_var).pack(anchor="w")
        ttk.Radiobutton(mode, text="Study area  (bounding box: north / south / west / east)",
                        value=AREA_SUBSET, variable=self.area_mode_var).pack(anchor="w",
                                                                            pady=(6, 0))

        box = ttk.LabelFrame(page, text="Bounding box (decimal degrees)", padding=12)
        box.pack(fill="x", pady=(0, 10))
        for c in range(3):
            box.columnconfigure(c, weight=1, uniform="bbox")

        def cell(row: int, col: int, label: str, var: tk.StringVar):
            f = ttk.Frame(box)
            f.grid(row=row, column=col, padx=8, pady=4)
            ttk.Label(f, text=label).pack(anchor="center")
            ent = ttk.Entry(f, textvariable=var, width=14, justify="center")
            ent.pack(anchor="center", pady=(2, 0))
            self.area_entries.append(ent)

        cell(0, 1, "North (maximum latitude)", self.north_var)
        cell(1, 0, "West (minimum longitude)", self.west_var)
        cell(1, 2, "East (maximum longitude)", self.east_var)
        cell(2, 1, "South (minimum latitude)", self.south_var)

        self.area_msg_label = ttk.Label(page, textvariable=self.area_msg_var,
                                        style="Hint.TLabel", wraplength=860, justify="left")
        self.area_msg_label.pack(anchor="w", pady=(0, 8))

        ttk.Label(page, style="Hint.TLabel", wraplength=860, justify="left",
                  text=("Latitude: -60 to 90 (south is negative). Longitude: the dataset uses "
                        "0 to 360 degrees east; negative values such as -10 are converted "
                        "automatically (10\u00b0W = 350). Example: North 38.5, South 36.5, "
                        "West 44, East 46.5. You can type Persian digits too.")
                  ).pack(anchor="w", pady=(0, 4))
        ttk.Label(page, style="Hint.TLabel", wraplength=860, justify="left",
                  text=("The server returns whole 0.25\u00b0 grid cells that fall inside the "
                        "box, so give a box a little larger than your basin. Every file keeps "
                        "all days of its year; only the area is cut.")
                  ).pack(anchor="w", pady=(0, 4))
        ttk.Label(page, style="Hint.TLabel", wraplength=860, justify="left",
                  text=("Study-area files are saved in a folder named subset_<box> and keep "
                        "their original names. The server builds these files on the fly, so an "
                        "interrupted file cannot be resumed part-way; it is simply downloaded "
                        "again (the files are small).")
                  ).pack(anchor="w")
        self._update_area_widgets()

    # --- page 6: options ---
    def _build_page_options(self, page):
        self._page_header(page, "Download options",
                          "Choose where to save the files and which years to include. "
                          "Then press 'Find files' to build the download list.", 5)

        # save location
        lf = ttk.LabelFrame(page, text="Save location", padding=12)
        lf.pack(fill="x", pady=(0, 10))
        row = ttk.Frame(lf)
        row.pack(fill="x")
        ttk.Entry(row, textvariable=self.out_dir_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse\u2026", command=self.browse_dir).pack(side="left", padx=(8, 0))
        ttk.Label(lf, style="Hint.TLabel",
                  text="Files are organised as  <folder> / <model> / <scenario> / "
                       "<ensemble> / <variable> /   (study areas: <folder> / subset_<box> / "
                       "<model> / ...)").pack(anchor="w", pady=(6, 0))

        # years
        yf = ttk.LabelFrame(page, text="Time period (inclusive)", padding=12)
        yf.pack(fill="x", pady=(0, 10))
        row = ttk.Frame(yf)
        row.pack(fill="x")
        ttk.Label(row, text="From").pack(side="left")
        ttk.Entry(row, textvariable=self.y0_var, width=7).pack(side="left", padx=(6, 12))
        ttk.Label(row, text="to").pack(side="left")
        ttk.Entry(row, textvariable=self.y1_var, width=7).pack(side="left", padx=(6, 18))
        for text, a, b in (("All years", MIN_YEAR, MAX_YEAR),
                           ("Historical (1950-2014)", 1950, 2014),
                           ("Future (2015-2100)", 2015, 2100)):
            ttk.Button(row, text=text,
                       command=lambda a=a, b=b: (self.y0_var.set(str(a)), self.y1_var.set(str(b)))
                       ).pack(side="left", padx=(0, 6))
        ttk.Label(yf, style="Hint.TLabel",
                  text="Every file that overlaps this period is included "
                       "(the dataset provides one file per year).").pack(anchor="w", pady=(6, 0))

        # version
        vf = ttk.LabelFrame(page, text="File version", padding=12)
        vf.pack(fill="x", pady=(0, 10))
        row = ttk.Frame(vf)
        row.pack(fill="x")
        ttk.Combobox(row, textvariable=self.version_var, width=28,
                     values=(LATEST_VERSION_LABEL, "_v2.0.nc", "_v1.1.nc", ALL_VERSIONS_LABEL)
                     ).pack(side="left")
        ttk.Label(vf, style="Hint.TLabel", wraplength=820, justify="left",
                  text="'Latest version of each file' keeps only the highest version of every "
                       "model / variable / year. Any other text lists only files whose name "
                       "contains it. 'All versions' lists every file (this may include the "
                       "same year in more than one version).").pack(anchor="w", pady=(6, 0))

        # advanced
        af = ttk.LabelFrame(page, text="Advanced", padding=12)
        af.pack(fill="x")
        row = ttk.Frame(af)
        row.pack(fill="x")
        ttk.Label(row, text="Parallel connections:").pack(side="left")
        self.sp_workers = ttk.Spinbox(row, from_=1, to=16, textvariable=self.workers_var, width=5)
        self.sp_workers.pack(side="left", padx=(6, 20))
        ttk.Label(row, text="Segments per file:").pack(side="left")
        self.sp_segments = ttk.Spinbox(row, from_=1, to=32, textvariable=self.segments_var, width=5)
        self.sp_segments.pack(side="left", padx=(6, 20))
        ttk.Checkbutton(row, text="Delete partial files when I press Stop",
                        variable=self.delete_partial_var).pack(side="left")
        ttk.Label(af, style="Hint.TLabel", wraplength=820, justify="left",
                  text="Each file is split into segments that are downloaded over several "
                       "connections at once. The defaults work well for most networks. "
                       "Keep partial files (default) if you want to resume later.").pack(
            anchor="w", pady=(6, 0))
        ttk.Label(af, textvariable=self.adv_note_var, style="Ctx.TLabel", wraplength=820,
                  justify="left").pack(anchor="w", pady=(6, 0))

    # --- page 7: download ---
    def _build_page_download(self, page):
        self._page_header(page, "Download",
                          "Review the file list, then press Start download. "
                          "Files that already exist are skipped.", 6)

        top = ttk.Frame(page)
        top.pack(fill="x")
        self.queue_info_var = tk.StringVar(value="No files yet.")
        ttk.Label(top, textvariable=self.queue_info_var, style="Ctx.TLabel").pack(side="left")
        ttk.Button(top, text="Open output folder",
                   command=self.open_output_folder).pack(side="right")

        tf = ttk.Frame(page)
        tf.pack(fill="both", expand=True, pady=(8, 8))
        cols = ("status", "years", "filename", "folder")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", height=6)
        for col, text, width, stretch in (("status", "Status", 100, False),
                                          ("years", "Year(s)", 90, False),
                                          ("filename", "File", 330, True),
                                          ("folder", "Folder", 300, True)):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w", stretch=stretch)
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)
        self.tree.tag_configure("downloading", foreground=ACCENT)
        self.tree.tag_configure("done", foreground=GREEN)
        self.tree.tag_configure("skipped", foreground=MUTED)
        self.tree.tag_configure("failed", foreground=RED)

        ctl = ttk.Frame(page)
        ctl.pack(fill="x")
        self.btn_start = ttk.Button(ctl, text="Start download", style="Primary.TButton",
                                    command=self.start_download)
        self.btn_pause = ttk.Button(ctl, text="Pause", command=self.pause_download, state="disabled")
        self.btn_resume = ttk.Button(ctl, text="Resume", command=self.resume_download, state="disabled")
        self.btn_stop = ttk.Button(ctl, text="Stop", command=self.stop_download, state="disabled")
        self.btn_start.pack(side="left")
        self.btn_pause.pack(side="left", padx=(10, 0))
        self.btn_resume.pack(side="left", padx=(6, 0))
        self.btn_stop.pack(side="left", padx=(6, 0))

        pf = ttk.LabelFrame(page, text="Progress", padding=12)
        pf.pack(fill="x", pady=(10, 0))
        self.cur_file_var = tk.StringVar(value="Current file: -")
        ttk.Label(pf, textvariable=self.cur_file_var).pack(anchor="w")
        self.pb_file = ttk.Progressbar(pf, orient="horizontal", mode="determinate")
        self.pb_file.pack(fill="x", pady=(4, 8))
        self.overall_var = tk.StringVar(value="Overall: 0 / 0 files")
        ttk.Label(pf, textvariable=self.overall_var).pack(anchor="w")
        self.pb_overall = ttk.Progressbar(pf, orient="horizontal", mode="determinate")
        self.pb_overall.pack(fill="x", pady=(4, 10))

        grid = ttk.Frame(pf)
        grid.pack(fill="x")
        self.speed_var = tk.StringVar(value="-")
        self.avg_var = tk.StringVar(value="-")
        self.downloaded_var = tk.StringVar(value="-")
        self.eta_var = tk.StringVar(value="-")
        self.elapsed_var = tk.StringVar(value="-")
        self.remaining_var = tk.StringVar(value="-")
        self.rate_var = tk.StringVar(value="-")
        self.perfile_var = tk.StringVar(value="-")
        stats = (("Speed", self.speed_var), ("Average", self.avg_var),
                 ("Downloaded", self.downloaded_var), ("Time left", self.eta_var),
                 ("Elapsed", self.elapsed_var), ("Files left", self.remaining_var),
                 ("Files/min", self.rate_var), ("Time/file", self.perfile_var))
        for i, (label, var) in enumerate(stats):
            r, c = divmod(i, 3)
            ttk.Label(grid, text=label + ":", style="Hint.TLabel").grid(
                row=r, column=c * 2, sticky="w", padx=(0, 6), pady=2)
            ttk.Label(grid, textvariable=var, font=(FONT_FAMILY, 10, "bold")).grid(
                row=r, column=c * 2 + 1, sticky="w", padx=(0, 26), pady=2)

    # ------------------------------------------------------------
    # Log / status
    # ------------------------------------------------------------

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _log(self, msg: str):
        file_log(msg)
        self.log_text.insert("end", msg + "\n")
        try:
            lines = int(self.log_text.index("end-1c").split(".")[0])
            if lines > MAX_LOG_LINES:
                self.log_text.delete("1.0", f"{lines - TRIM_LOG_TO_LINES + 1}.0")
        except Exception:
            pass
        self.log_text.see("end")

    def _clear_log(self):
        self.log_text.delete("1.0", "end")

    def _toggle_log(self):
        if self._log_visible:
            self.log_frame.pack_forget()
            self.btn_log.configure(text="Show log \u25B4")
        else:
            self.log_frame.pack(side="bottom", fill="x", padx=8, pady=(0, 6), before=self.body)
            self.btn_log.configure(text="Hide log \u25BE")
        self._log_visible = not self._log_visible

    def post_ui(self, event: dict):
        self.uiq.put(event)

    def post_log(self, msg: str):
        self.post_ui({"type": "log", "msg": msg})

    # ------------------------------------------------------------
    # Event pump
    # ------------------------------------------------------------

    def _tick(self):
        """Process queued events and refresh the progress display.

        The next tick is ALWAYS scheduled (finally), so an error in one handler
        can never stop the UI from updating."""
        if self.closing:
            return
        try:
            for _ in range(300):
                try:
                    ev = self.uiq.get_nowait()
                except queue.Empty:
                    break
                try:
                    self._handle_event(ev)
                except Exception:
                    self._safe_log("[ERR] UI event error:\n" + traceback.format_exc())

            if self.is_downloading:
                try:
                    self._refresh_progress()
                except Exception:
                    if not self._progress_err_logged:
                        self._progress_err_logged = True
                        self._safe_log("[ERR] Progress update error:\n" + traceback.format_exc())
        except Exception:
            file_log("[ERR] Tick error:\n" + traceback.format_exc())
        finally:
            if not self.closing:
                try:
                    self.after(UI_TICK_MS, self._tick)
                except Exception:
                    pass

    def _handle_event(self, ev: dict):
        et = ev.get("type")

        if et == "log":
            self._log(ev["msg"])

        elif et == "status":
            if ev.get("gen") is None or ev["gen"] == self._cat_gen:
                self._set_status(ev["msg"])

        elif et in ("cat_result", "cat_error"):
            if ev["gen"] != self._cat_gen:
                return                       # stale result of a cancelled task
            self._cat_busy = False
            self._set_busy(False)
            kind = ev["kind"]
            if et == "cat_error":
                self._log(f"[ERR] {kind}: {ev['error']}")
                data = None
            else:
                data = ev["data"]
            handler = {
                "models": self._on_models_loaded,
                "scenarios": self._on_scenarios_loaded,
                "ensembles": self._on_ensembles_loaded,
                "params": self._on_params_loaded,
                "scenarios_all": self._on_scenarios_all_loaded,
                "scan": self._on_scan_loaded,
                "queue": self._on_queue_built,
            }[kind]
            handler(data)
            self._refresh_ui_state()

        elif et == "space_probe":
            self._on_space_probe(ev)

        elif et == "dl_file_start":
            self._cur_file_name = ev["filename"]
            self.cur_file_var.set(f"Current file: {ev['filename']}")
            self._tree_set_status(ev["index"], "Downloading", "downloading", see=True)

        elif et == "dl_file_done":
            label, tag = {
                "ok": ("Done", "done"),
                "skipped": ("Skipped", "skipped"),
                "failed": ("Failed", "failed"),
                "stopped": ("Stopped", ""),
            }.get(ev["status"], (ev["status"], ""))
            self._tree_set_status(ev["index"], label, tag)

        elif et == "dl_finished":
            self._on_download_finished(ev)

    # ------------------------------------------------------------
    # Study area (new in 1.1)
    # ------------------------------------------------------------

    def _area_bbox(self) -> Optional[Dict[str, float]]:
        """The validated bounding box, or None (whole globe, or invalid input)."""
        if self.area_mode_var.get() != AREA_SUBSET:
            return None
        try:
            return parse_bbox(self.north_var.get(), self.south_var.get(),
                              self.west_var.get(), self.east_var.get())
        except ValueError:
            return None

    def _area_error(self) -> str:
        """'' when the area choice is usable, otherwise a message for the user."""
        if self.area_mode_var.get() != AREA_SUBSET:
            return ""
        try:
            parse_bbox(self.north_var.get(), self.south_var.get(),
                       self.west_var.get(), self.east_var.get())
        except ValueError as e:
            return str(e)
        return ""

    def _area_label(self) -> str:
        if self.area_mode_var.get() != AREA_SUBSET:
            return "Whole globe"
        b = self._area_bbox()
        return format_bbox(b) if b else "Study area (incomplete)"

    def _update_area_widgets(self):
        subset = self.area_mode_var.get() == AREA_SUBSET
        for ent in self.area_entries:
            ent.configure(state="normal" if subset else "disabled")
        if not subset:
            self.area_msg_var.set("Complete global files will be downloaded, as in "
                                  "earlier versions.")
            color = MUTED
        else:
            err = self._area_error()
            if err:
                self.area_msg_var.set(err)
                color = RED
            else:
                b = self._area_bbox()
                assert b is not None
                cols, rows = bbox_cells(b)
                self.area_msg_var.set(
                    f"Study area {format_bbox(b)}  \u2022  about {cols} x {rows} grid cells "
                    f"({GRID_STEP:g}\u00b0 each) per day.")
                color = GREEN
        self.area_msg_label.configure(foreground=color)

    def _on_area_changed(self, *_):
        if self._suppress_traces or self.is_downloading:
            return
        if self.max_pos > P_AREA or self.download_items:
            self._invalidate_from(P_AREA)
        self._update_area_widgets()
        self._refresh_ui_state()

    def _update_options_note(self):
        """Explain on the Options page which advanced settings apply."""
        subset = self.area_mode_var.get() == AREA_SUBSET
        state = "disabled" if subset else "normal"
        for sp in (self.sp_workers, self.sp_segments):
            if sp is not None:
                sp.configure(state=state)
        if subset:
            self.adv_note_var.set(
                "Study-area mode: each file is downloaded over a single connection, so "
                "'Parallel connections' and 'Segments per file' are not used. Partial files "
                "are always removed when a download stops.")
        else:
            self.adv_note_var.set("")

    # ------------------------------------------------------------
    # Wizard navigation
    # ------------------------------------------------------------

    @property
    def current(self) -> int:
        """Id of the page that is showing (one of the P_* constants)."""
        return self.order[self.pos]

    def _page_pos(self, page: int) -> int:
        return self.order.index(page)

    def _step_names(self) -> List[str]:
        return [PAGE_NAMES[p] for p in self.order]

    def _show_step(self, pos: int):
        self.pos = pos
        self.pages[self.order[pos]].tkraise()
        self._enter_step(self.order[pos])
        self._refresh_ui_state()

    def _enter_step(self, page: int):
        var_flow = self.flow == FLOW_VARIABLE
        if page == P_MODELS:
            if var_flow:
                if self.params_by_model is None:
                    self._load_scan()
                else:
                    self._populate_models_for_variables()
            elif self.models is None:
                self._load_models()
        elif page == P_SCENARIO:
            if self.scenarios is None:
                if var_flow:
                    self._load_scenarios_all()
                else:
                    self._load_scenarios()
        elif page == P_ENSEMBLES:
            if var_flow:
                if self.ensemble_list.count() == 0:
                    self._refresh_ensemble_list()
            elif self.ensembles is None:
                self._load_ensembles()
        elif page == P_VARIABLES:
            if var_flow:
                if self.var_list.count() == 0:
                    self._populate_static_variables()
            elif self.params_by_model is None:
                self._load_parameters()
        elif page == P_AREA:
            self._update_area_widgets()
        elif page == P_OPTIONS:
            self._update_options_note()

    def _can_proceed(self, page: int) -> bool:
        if page == P_MODELS:
            if self.flow == FLOW_VARIABLE:
                return len(self.sel_models) > 0
            return len(self.sel_models) > 0 and bool(self.models)
        if page == P_SCENARIO:
            return self.sel_scenario is not None
        if page == P_ENSEMBLES:
            if self.all_ens_var.get():
                return bool(self.ensembles)
            return len(self.sel_ensembles) > 0
        if page == P_VARIABLES:
            return len(self.sel_params) > 0
        if page == P_AREA:
            return self._area_error() == ""
        return page == P_OPTIONS

    def _nav_blocked(self) -> bool:
        return self.is_downloading or self._cat_busy or self._space_checking

    def _advance(self):
        page = self.current
        if self._nav_blocked() or page == P_DOWNLOAD or not self._can_proceed(page):
            return
        if page == P_OPTIONS:
            if self.download_items:
                # Nothing was changed since the list was built: do not scan again.
                self.max_pos = max(self.max_pos, self._page_pos(P_DOWNLOAD))
                self._show_step(self._page_pos(P_DOWNLOAD))
                return
            self._build_queue()
            return
        self.max_pos = max(self.max_pos, self.pos + 1)
        self._show_step(self.pos + 1)

    def _next_if_possible(self):
        self._advance()

    def _back(self):
        if self.is_downloading or self._space_checking or self.pos == 0:
            return
        self._show_step(self.pos - 1)

    def _sidebar_clicked(self, pos: int):
        if self.is_downloading or self._space_checking:
            self._set_status("Stop the download before changing steps.")
            return
        if pos == self.pos or pos > self.max_pos:
            return
        self._show_step(pos)

    # ------------------------------------------------------------
    # Workflow (models first / variables first)
    # ------------------------------------------------------------

    def _on_workflow_changed(self):
        new = self.flow_var.get()
        if new == self.flow:
            return
        if self.is_downloading or self._space_checking:
            self.flow_var.set(self.flow)
            return
        self._cancel_catalog()
        self.flow = new
        self.order = list(FLOW_ORDERS[new])
        self.models = None
        self.scenarios = None
        self.ensembles = None
        self.params_by_model = None
        self.sel_models = []
        self.sel_scenario = None
        self.sel_ensembles = []
        self.sel_params = []
        self._load_failures = 0
        for lst in (self.model_list, self.scenario_list, self.ensemble_list, self.var_list):
            lst.set_items([])
            lst.set_message("")
        self.scenario_hint_var.set("")
        self._clear_queue_state()
        self.max_pos = 0
        self.sidebar.set_names(self._step_names())
        self._apply_flow_texts()
        self._log("[INFO] Workflow: " + ("variables first (scenario, variables, then models "
                                        "are selected automatically)."
                                        if new == FLOW_VARIABLE else "models first."))
        self._show_step(0)

    def _apply_flow_texts(self):
        """Page texts that depend on the workflow."""
        var_flow = self.flow == FLOW_VARIABLE
        if var_flow:
            self.models_sub.configure(
                text="These models have at least one of the variables you chose under the "
                     "chosen scenario; the text after each name shows which. All of them "
                     "are selected: untick any model you do not want. Models that have "
                     "none of the chosen variables are not listed.")
            self.var_sub.configure(
                text="Select every variable you want (for example tasmax, tasmin and pr). "
                     "Next you choose the scenario; the program then finds every model "
                     "that has these variables and selects them for you.")
        else:
            self.models_sub.configure(
                text="Each model is a different global climate simulation. Select one, "
                     "several or all of them, then press Next. A model that lacks a scenario, "
                     "ensemble or variable you choose later is skipped for that item only.")
            self.var_sub.configure(
                text="Select every variable you want to download (for example tasmax, tasmin "
                     "and pr). The number shows how many of the selected models have each "
                     "variable; a model downloads only the variables it has.")
        if self.var_common_cb is not None:
            self.var_common_cb.configure(state="disabled" if var_flow else "normal")

    def _populate_static_variables(self):
        """'Variables first': the nine NEX-GDDP variables, listed before any model
        has been read (the models that have them are found after the scenario)."""
        items = [(v, f"{v}   \u2014   {VARIABLE_HINTS[v]}") for v in KNOWN_VARIABLES]
        self.var_list.set_items(items)
        self.var_list.set_message("Which models have these variables is checked after you "
                                  "choose the scenario.")
        self._on_variable_change()

    def _populate_models_for_variables(self):
        """'Variables first': list (and select) every model that has at least one of
        the chosen variables under the chosen scenario."""
        if self.model_list.count() > 0 or not self.params_by_model:
            return
        rows = models_with_variables(self.params_by_model, self.sel_params)
        total = len(self.params_by_model)
        items: List[Tuple[str, str]] = []
        for model, have, missing in rows:
            label = f"{model}   \u2014   {', '.join(have)}"
            if missing:
                label += f"   (no {', '.join(missing)})"
            items.append((model, label))
        self.model_list.set_items(items)
        self.model_list.select_keys([k for k, _ in items])
        failed = self._load_failures
        if items:
            per_var = ", ".join(
                f"{v} {sum(1 for _, have, _m in rows if v in have)}" for v in self.sel_params)
            msg = (f"{len(items)} of {total} models have at least one of the selected "
                   f"variables and are selected  ({per_var}).")
        else:
            msg = "None of the models has the selected variables under this scenario."
        if failed:
            msg += (f"  {failed} model(s) could not be scanned and are not listed; press "
                    f"'Refresh list' to try again.")
        self.model_list.set_message(msg, error=(not items) or bool(failed))
        self._set_status(f"{len(items)} of {total} models have the selected variables.")
        self._log(f"[INFO] Models with at least one selected variable: {len(items)} of {total}")
        self._on_model_change()

    def _clear_catalog_cache(self):
        if self._cat_busy or self.is_downloading:
            return
        cache_clear()
        self._log("[INFO] Catalog cache cleared. Lists are read from the NASA server again "
                  "the next time they are needed.")
        self._set_status("Catalog cache cleared.")

    def _models_label(self) -> str:
        """Short text describing the selected models."""
        n = len(self.sel_models)
        if n == 0:
            return ""
        if n <= 3:
            return ", ".join(self.sel_models)
        return f"{n} models"

    def _ensembles_label(self) -> str:
        if self.all_ens_var.get():
            return "All ensembles"
        return ", ".join(self.sel_ensembles)

    def _context_text(self, page: int) -> str:
        """What was chosen in the steps that come before `page` (workflow aware)."""
        parts: List[str] = []
        for p in self.order[: self._page_pos(page)]:
            if p == P_MODELS:
                txt = self._models_label()
            elif p == P_SCENARIO:
                txt = self.sel_scenario or ""
            elif p == P_ENSEMBLES:
                txt = self._ensembles_label()
            elif p == P_VARIABLES:
                txt = ", ".join(self.sel_params)
            else:
                txt = ""
            if txt:
                parts.append(txt)
        return "  \u00b7  ".join(parts)

    def _selection_summary(self) -> str:
        base = self._context_text(P_AREA)
        area = self._area_label() if self.sel_params else ""
        return "  \u00b7  ".join(x for x in (base, area) if x)

    def _refresh_ui_state(self):
        # context lines on each page
        for page in (P_MODELS, P_SCENARIO, P_ENSEMBLES, P_VARIABLES, P_AREA):
            self.ctx_vars[page].set(self._context_text(page))
        self.ctx_vars[P_OPTIONS].set(self._selection_summary())
        self.ctx_vars[P_DOWNLOAD].set(self._selection_summary())

        # sidebar (summaries follow the order of the current workflow)
        by_page = {
            P_MODELS: self._models_label(),
            P_SCENARIO: self.sel_scenario or "",
            P_ENSEMBLES: self._ensembles_label(),
            P_VARIABLES: ", ".join(self.sel_params),
            P_AREA: self._area_label() if self.max_pos >= P_AREA else "",
            P_OPTIONS: "",
            P_DOWNLOAD: f"{len(self.download_items)} files" if self.download_items else "",
        }
        if self.max_pos >= P_OPTIONS:
            try:
                y0, y1 = self._parse_years()
                by_page[P_OPTIONS] = f"{y0}\u2013{y1}"
            except ValueError:
                pass
        summaries = [by_page.get(p, "") for p in self.order]
        self.sidebar.update_state(self.pos, self.max_pos, summaries,
                                  not (self.is_downloading or self._space_checking))

        # navigation buttons
        page = self.current
        blocked = self._nav_blocked()
        self.btn_back.configure(
            state="normal" if (self.pos > 0 and not self.is_downloading
                               and not self._space_checking) else "disabled")
        self.btn_next.configure(
            text="Find files \u2192" if page == P_OPTIONS else "Next \u2192")
        if page == P_DOWNLOAD:
            self.btn_next.configure(state="disabled")
            self.next_hint_var.set("")
        else:
            can = self._can_proceed(page) and not blocked
            self.btn_next.configure(state="normal" if can else "disabled")
            hints = {P_MODELS: "Select at least one model to continue",
                     P_SCENARIO: "Select a scenario to continue",
                     P_ENSEMBLES: "Select at least one ensemble, or tick 'All ensembles'",
                     P_VARIABLES: "Select at least one variable"}
            if page == P_AREA:
                hints[P_AREA] = shorten(self._area_error(), 70)
            if self._cat_busy:
                self.next_hint_var.set("")
            elif not self._can_proceed(page):
                self.next_hint_var.set(hints.get(page, ""))
            else:
                self.next_hint_var.set("")

    # ------------------------------------------------------------
    # Invalidation (keeps later steps consistent with earlier choices)
    # ------------------------------------------------------------

    def _reset_scenario_data(self):
        self.scenarios = None
        self.sel_scenario = None
        self.scenario_list.set_items([])
        self.scenario_list.set_message("")
        self.scenario_hint_var.set("")

    def _reset_ensemble_data(self):
        self.ensembles = None
        self.sel_ensembles = []
        self.ensemble_list.set_items([])
        self.ensemble_list.set_message("")

    def _reset_param_data(self):
        self.params_by_model = None
        self.sel_params = []
        self.var_list.set_items([])
        self.var_list.set_message("")

    def _reset_model_choice(self):
        """'Variables first': the model list is rebuilt from the chosen variables."""
        self.sel_models = []
        self.model_list.set_items([])
        self.model_list.set_message("")

    def _reset_ensemble_choice(self):
        """'Variables first': the ensemble data stays, only the choice is reset."""
        self.sel_ensembles = []
        self.ensemble_list.set_items([])
        self.ensemble_list.set_message("")

    def _reset_scan_data(self):
        """'Variables first': forget what the scan of all models found."""
        self.params_by_model = None
        self._reset_ensemble_data()
        self._reset_model_choice()

    def _invalidate_from(self, page: int):
        """The choice made at `page` changed: reset everything that depends on it."""
        self._cancel_catalog()
        if self.flow == FLOW_MODEL:
            if page == P_MODELS:
                self._reset_scenario_data()
                self._reset_ensemble_data()
                self._reset_param_data()
            elif page == P_SCENARIO:
                self._reset_ensemble_data()
                self._reset_param_data()
            elif page == P_ENSEMBLES:
                self._reset_param_data()
        else:
            if page == P_VARIABLES:
                # the scan data stays valid; the model list is rebuilt from the variables
                self._reset_model_choice()
                self._reset_ensemble_choice()
            elif page == P_SCENARIO:
                self._reset_scan_data()
            elif page == P_MODELS:
                self._reset_ensemble_choice()
        self._clear_queue_state()
        self.max_pos = min(self.max_pos, self._page_pos(page))

    def _clear_queue_state(self):
        self.download_items = []
        self._queue_area_text = ""
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self.queue_info_var.set("No files yet.")

    def _on_options_changed(self, *_):
        if self._suppress_traces or self.is_downloading:
            return
        if self.download_items:
            self._invalidate_from(P_OPTIONS)
            self._refresh_ui_state()

    # ------------------------------------------------------------
    # Selection handlers
    # ------------------------------------------------------------

    def _on_model_change(self):
        new = self.model_list.get_selected()
        if new != self.sel_models:
            self.sel_models = new
            self._invalidate_from(P_MODELS)
        self._refresh_ui_state()

    def _on_scenario_change(self):
        sel = self.scenario_list.get_selected()
        new = sel[0] if sel else None
        if new != self.sel_scenario:
            self.sel_scenario = new
            self._invalidate_from(P_SCENARIO)
        self.scenario_hint_var.set(SCENARIO_HINTS.get(new or "", ""))
        self._refresh_ui_state()

    def _on_ensemble_change(self):
        new = self.ensemble_list.get_selected()
        if new != self.sel_ensembles:
            self.sel_ensembles = new
            self._invalidate_from(P_ENSEMBLES)
        self._refresh_ui_state()

    def _on_all_ens_toggled(self):
        """The 'All ensembles of every model' tick box changed."""
        if self.is_downloading:
            return
        self._invalidate_from(P_ENSEMBLES)
        if self.ensembles is not None:
            self._refresh_ensemble_list()
        else:
            self.ensemble_list.set_enabled(not self.all_ens_var.get())
        self._refresh_ui_state()

    def _on_variable_change(self):
        new = self.var_list.get_selected()
        if new != self.sel_params:
            self.sel_params = new
            self._invalidate_from(P_VARIABLES)
        self._refresh_ui_state()

    # ------------------------------------------------------------
    # Catalog tasks (background)
    # ------------------------------------------------------------

    def _set_busy(self, busy: bool, text: str = ""):
        if busy:
            self._set_status(text)
            if not self.busy_bar.winfo_manager():
                self.btn_cancel.pack(side="right", padx=(0, 8), pady=3)
                self.busy_bar.pack(side="right", padx=8, pady=3)
            self.busy_bar.start(12)
        else:
            self.busy_bar.stop()
            self.busy_bar.pack_forget()
            self.btn_cancel.pack_forget()

    def _cancel_catalog(self):
        if self._cat_cancel is not None:
            self._cat_cancel.set()
            self._cat_cancel = None
        self._cat_gen += 1
        if self._cat_busy:
            self._cat_busy = False
            self._set_busy(False)

    def _cancel_clicked(self):
        page = self.current
        self._cancel_catalog()
        lists = {P_MODELS: self.model_list, P_SCENARIO: self.scenario_list,
                 P_ENSEMBLES: self.ensemble_list, P_VARIABLES: self.var_list}
        lst = lists.get(page)
        if lst is not None and lst.count() == 0:
            lst.set_message("Cancelled. Press Refresh list to load again.")
        self._set_status("Cancelled.")
        self._refresh_ui_state()

    def _start_catalog_task(self, kind: str, status_text: str, work: Callable[[CatalogClient], object]):
        self._cancel_catalog()
        cancel = threading.Event()
        self._cat_cancel = cancel
        self._cat_gen += 1
        gen = self._cat_gen
        refresh = self._refresh_flag
        self._refresh_flag = False
        self._cat_busy = True
        self._cat_kind = kind
        self._set_busy(True, status_text)
        self._refresh_ui_state()

        def runner():
            try:
                client = CatalogClient(self.post_ui, cancel, gen, refresh=refresh)
                result = work(client)
                self.post_ui({"type": "cat_result", "gen": gen, "kind": kind, "data": result})
            except Exception as e:
                file_log(f"[ERR] Catalog task '{kind}' failed:\n{traceback.format_exc()}")
                self.post_ui({"type": "cat_error", "gen": gen, "kind": kind, "error": str(e)})

        threading.Thread(target=runner, daemon=True).start()

    def _already_loading(self, kind: str) -> bool:
        return self._cat_busy and self._cat_kind == kind

    @staticmethod
    def _find_entry(entries: Optional[List[Dict[str, Optional[str]]]],
                    title: Optional[str]) -> Optional[Dict[str, Optional[str]]]:
        for e in entries or []:
            if e.get("title") == title:
                return e
        return None

    def _refresh_current(self):
        if self.is_downloading or self._cat_busy or self._space_checking:
            return
        page = self.current
        var_flow = self.flow == FLOW_VARIABLE
        if page == P_MODELS:
            if var_flow:
                # read the models again (catalogs that were fetched fine come from the cache)
                self.params_by_model = None
                self.ensembles = None
                self._reset_model_choice()
                self._reset_ensemble_choice()
            else:
                self.models = None
        elif page == P_SCENARIO:
            self.scenarios = None
        elif page == P_ENSEMBLES:
            if var_flow:
                self._refresh_ensemble_list()
                return
            self.ensembles = None
        elif page == P_VARIABLES:
            if var_flow:
                return                       # the fixed list of the nine variables
            self.params_by_model = None
        else:
            return
        # Models first: bypass / replace the cached catalogs. Variables first reads many
        # catalogs; the ones that were fetched fine are reused and only failed ones are
        # requested again.
        self._refresh_flag = not var_flow
        try:
            self._enter_step(page)
        finally:
            self._refresh_flag = False

    # --- loaders (models first) ---
    def _load_models(self):
        if self._already_loading("models"):
            return
        self.model_list.set_message("")
        self._start_catalog_task("models", "Loading climate models\u2026",
                                 lambda c: c.scan_models())

    def _load_scenarios(self):
        if self._already_loading("scenarios") or not self.sel_models:
            return
        jobs: List[Tuple[str, Dict[str, Optional[str]]]] = []
        for name in self.sel_models:
            model = self._find_entry(self.models, name)
            if model is not None:
                jobs.append((name, model))
        if not jobs:
            return
        self.scenario_list.set_message("")

        def work(client: CatalogClient):
            def prog(done: int, total: int):
                client.status(f"Loading scenarios\u2026 ({done}/{total})")

            res = parallel_map(lambda j: client.list_scenarios(j[1]), jobs, client.cancel,
                               on_done=prog)
            if res is None or any(r is None for r in res):
                return None
            return {name: lst for (name, _), lst in zip(jobs, res)}

        self._start_catalog_task("scenarios", "Loading scenarios\u2026", work)

    def _load_ensembles(self):
        if self._already_loading("ensembles") or not self.sel_scenario \
                or self.scenarios is None:
            return
        jobs: List[Tuple[str, Dict[str, Optional[str]]]] = []
        skipped = 0
        for name in self.sel_models:
            scen = self._find_entry(self.scenarios.get(name), self.sel_scenario)
            if scen is None:
                skipped += 1
                continue
            jobs.append((name, scen))
        if skipped:
            self._log(f"[INFO] {skipped} selected model(s) do not have scenario "
                      f"'{self.sel_scenario}' and are skipped.")
        if not jobs:
            self.ensemble_list.set_items([])
            self.ensemble_list.set_message(
                "None of the selected models has this scenario. Go back and choose "
                "another scenario or other models.", error=True)
            return
        self.ensemble_list.set_message("")

        def work(client: CatalogClient):
            def prog(done: int, total: int):
                client.status(f"Loading ensembles\u2026 ({done}/{total})")

            res = parallel_map(lambda j: client.list_ensembles(j[1]), jobs, client.cancel,
                               on_done=prog)
            if res is None or any(r is None for r in res):
                return None
            return {name: lst for (name, _), lst in zip(jobs, res)}

        self._start_catalog_task("ensembles", "Loading ensembles\u2026", work)

    def _load_parameters(self):
        if self._already_loading("params") or self.ensembles is None:
            return
        if not self.all_ens_var.get() and not self.sel_ensembles:
            return
        jobs: List[Tuple[str, str, Dict[str, Optional[str]]]] = []
        no_ens = 0
        for model_name in self.sel_models:
            found = False
            for e in self.ensembles.get(model_name) or []:
                if self.all_ens_var.get() or e["title"] in self.sel_ensembles:
                    jobs.append((model_name, e["title"], e))
                    found = True
            if not found:
                no_ens += 1
        if no_ens:
            self._log(f"[INFO] {no_ens} selected model(s) have none of the selected "
                      f"ensembles and are skipped.")
        if not jobs:
            self.var_list.set_items([])
            self.var_list.set_message(
                "None of the selected models has the selected ensembles. Go back and "
                "change the ensemble choice.", error=True)
            return
        self.var_list.set_message("")

        def work(client: CatalogClient):
            def prog(done: int, total: int):
                client.status(f"Loading variables\u2026 ({done}/{total})")

            res = parallel_map(lambda j: client.list_parameters(j[2]), jobs, client.cancel,
                               on_done=prog)
            if res is None or any(r is None for r in res):
                return None
            result: Dict[str, Dict[str, Dict[str, Dict[str, Optional[str]]]]] = {}
            for (model_name, ens_name, _e), plist in zip(jobs, res):
                result.setdefault(model_name, {})[ens_name] = {
                    p["title"]: p for p in plist if p.get("title")}
            return result

        self._start_catalog_task("params", "Loading variables\u2026", work)

    # --- loaders (variables first) ---
    def _load_scenarios_all(self):
        """'Variables first': the models and the scenarios of every model."""
        if self._already_loading("scenarios_all"):
            return
        self.scenario_list.set_message("")
        known_models = self.models

        def work(client: CatalogClient):
            models = known_models if known_models is not None else client.scan_models()
            if models is None:
                return None

            def prog(done: int, total: int):
                client.status(f"Loading scenarios\u2026 ({done}/{total} models)")

            res = parallel_map(lambda mdl: client.list_scenarios(mdl), models, client.cancel,
                               on_done=prog)
            if res is None:
                return None
            result = {mdl["title"]: lst for mdl, lst in zip(models, res) if lst is not None}
            if not result:
                return None
            return {"models": models, "scenarios": result,
                    "failures": sum(1 for r in res if r is None)}

        self._start_catalog_task("scenarios_all", "Loading models and scenarios\u2026", work)

    def _load_scan(self):
        """'Variables first': for the chosen scenario, read the ensembles and the
        variables of every model (one catalog per model and per ensemble, read
        several at a time)."""
        if self._already_loading("scan") or not self.sel_scenario or self.scenarios is None:
            return
        jobs: List[Tuple[str, Dict[str, Optional[str]]]] = []
        for name, lst in self.scenarios.items():
            scen = self._find_entry(lst, self.sel_scenario)
            if scen is not None:
                jobs.append((name, scen))
        if not jobs:
            self.model_list.set_items([])
            self.model_list.set_message("No model has this scenario.", error=True)
            return
        self.model_list.set_message("")
        self._log(f"[INFO] Looking for the chosen variables in {len(jobs)} models "
                  f"(scenario '{self.sel_scenario}').")

        def work(client: CatalogClient):
            def prog_e(done: int, total: int):
                client.status(f"Reading models\u2026 ensembles ({done}/{total})")

            res1 = parallel_map(lambda j: client.list_ensembles(j[1]), jobs, client.cancel,
                                on_done=prog_e)
            if res1 is None:
                return None
            failed_models: Set[str] = set()
            ens_result: Dict[str, List[Dict[str, Optional[str]]]] = {}
            pairs: List[Tuple[str, Dict[str, Optional[str]]]] = []
            for (name, _scen), elist in zip(jobs, res1):
                if elist is None:
                    failed_models.add(name)
                    continue
                ens_result[name] = elist
                pairs.extend((name, e) for e in elist)

            def prog_p(done: int, total: int):
                client.status(f"Reading models\u2026 variables ({done}/{total})")

            res2 = parallel_map(lambda pr: client.list_parameters(pr[1]), pairs, client.cancel,
                                on_done=prog_p)
            if res2 is None:
                return None
            per_model: Dict[str, Dict[str, Dict[str, Dict[str, Optional[str]]]]] = {
                name: {} for name in ens_result}
            for (name, e), plist in zip(pairs, res2):
                if plist is None:
                    failed_models.add(name)
                    continue
                per_model[name][e["title"]] = {p["title"]: p for p in plist if p.get("title")}
            par_result = {n: per for n, per in per_model.items() if n not in failed_models}
            ens_result = {n: lst for n, lst in ens_result.items() if n in par_result}
            if not par_result:
                return None
            return {"ensembles": ens_result, "params": par_result,
                    "failures": len(failed_models)}

        self._start_catalog_task("scan", "Reading models\u2026", work)

    # --- loader results ---
    def _on_models_loaded(self, data):
        if data is None:
            self.models = None
            self.model_list.set_items([])
            self.model_list.set_message(
                "Could not load the model list. Check your internet connection and "
                "press 'Refresh list'.", error=True)
            self._set_status("Could not load models.")
            return
        self.models = data
        self.model_list.set_message("" if data else "No models were found.")
        self.model_list.set_items([(m["title"], m["title"]) for m in data])
        self._set_status(f"Loaded {len(data)} models.")
        self._log(f"[INFO] Loaded models: {len(data)}")
        self._on_model_change()

    def _on_scenarios_loaded(self, data):
        if data is None:
            self.scenarios = None
            self.scenario_list.set_items([])
            self.scenario_list.set_message(
                "Could not load scenarios. Check your connection and press 'Refresh list'.",
                error=True)
            self._set_status("Could not load scenarios.")
            return
        self.scenarios = data
        self._load_failures = 0
        self._refresh_scenario_list()

    def _on_scenarios_all_loaded(self, data):
        if data is None:
            self.scenarios = None
            self.scenario_list.set_items([])
            self.scenario_list.set_message(
                "Could not load the models and scenarios. Check your connection and press "
                "'Refresh list'.", error=True)
            self._set_status("Could not load scenarios.")
            return
        self.models = data["models"]
        self.scenarios = data["scenarios"]
        self._load_failures = data.get("failures", 0)
        self._refresh_scenario_list()

    def _refresh_scenario_list(self):
        if self.scenarios is None:
            return
        per_model = {m: {s["title"] for s in lst} for m, lst in self.scenarios.items()}
        counts, total = union_counts(per_model)
        if not counts:
            self.scenario_list.set_items([])
            self.scenario_list.set_message("No scenarios were found for the selected models.")
            self._set_status("No scenarios found.")
            self._on_scenario_change()
            return
        notes: List[str] = []
        if any(n < total for n in counts.values()):
            notes.append("A model that does not have the chosen scenario is skipped.")
        failed = self._load_failures if self.flow == FLOW_VARIABLE else 0
        if failed:
            notes.append(f"{failed} model(s) could not be loaded and are not counted. "
                         f"Press 'Refresh list' to try again.")
        self.scenario_list.set_message("  ".join(notes), error=bool(failed))
        self.scenario_list.set_items(
            [(t, f"{t}   {count_label(n, total)}".rstrip()) for t, n in counts.items()])
        self._set_status(f"Loaded {len(counts)} scenarios.")
        self._log(f"[INFO] Scenarios available: {len(counts)} (models counted: {total})")
        self._on_scenario_change()

    def _on_ensembles_loaded(self, data):
        if data is None:
            self.ensembles = None
            self.ensemble_list.set_items([])
            self.ensemble_list.set_message(
                "Could not load ensembles. Check your connection and press 'Refresh list'.",
                error=True)
            self._set_status("Could not load ensembles.")
            return
        self.ensembles = data
        self._refresh_ensemble_list()

    def _refresh_ensemble_list(self):
        if self.ensembles is None:
            return
        scope = {m: lst for m, lst in self.ensembles.items() if m in self.sel_models}
        per_model = {m: {e["title"] for e in lst} for m, lst in scope.items()}
        counts, total = union_counts(per_model)
        all_ens = self.all_ens_var.get()
        self.ensemble_list.set_enabled(not all_ens)
        if not counts:
            self.ensemble_list.set_items([])
            self.ensemble_list.set_message("No ensembles were found for the selected models.")
            self._on_ensemble_change()
            return
        shown = set(counts)
        notes: List[str] = []
        if all_ens:
            notes.append("All ensembles of every model will be downloaded; the list below "
                         "is for information.")
        common = {t for t, n in counts.items() if n == total}
        if self.ens_common_only_var.get():
            if common:
                shown = common
                if len(counts) > len(common):
                    notes.append(f"{len(counts) - len(common)} ensemble(s) are hidden because "
                                 f"they are not available in every selected model.")
            else:
                notes.append("No ensemble is shared by all selected models; showing all "
                             "ensembles.")
        elif len(counts) > len(common):
            notes.append("A model that lacks a selected ensemble is skipped for it.")
        self.ensemble_list.set_message("  ".join(notes))
        self.ensemble_list.set_items(
            [(t, f"{t}   {count_label(counts[t], total)}".rstrip()) for t in shown])
        if len(shown) == 1 and not all_ens:          # nothing to choose: preselect it
            self.ensemble_list.select_keys(list(shown))
        self._set_status(f"Loaded {len(shown)} ensembles.")
        self._log(f"[INFO] Ensembles available: {len(shown)}")
        self._on_ensemble_change()

    def _on_params_loaded(self, data):
        if data is None:
            self.params_by_model = None
            self.var_list.set_items([])
            self.var_list.set_message(
                "Could not load variables. Check your connection and press 'Refresh list'.",
                error=True)
            self._set_status("Could not load variables.")
            return
        self.params_by_model = data
        self._load_failures = 0
        self._refresh_variable_list()
        self._set_status("Variables loaded.")

    def _on_scan_loaded(self, data):
        if data is None:
            self.params_by_model = None
            self.ensembles = None
            self.model_list.set_items([])
            self.model_list.set_message(
                "Could not read the models. Check your connection and press "
                "'Refresh list'.", error=True)
            self._set_status("Could not read the models.")
            return
        self.ensembles = data["ensembles"]
        self.params_by_model = data["params"]
        self._load_failures = data.get("failures", 0)
        # data of a new scan: whatever was derived from an older one is reset
        self._reset_model_choice()
        self._reset_ensemble_choice()
        self._set_status(f"Read {len(self.params_by_model)} models.")
        self._populate_models_for_variables()

    def _refresh_variable_list(self):
        """Models first: variables of the selected models, with counters."""
        if self.params_by_model is None or self.flow != FLOW_MODEL:
            return
        scope = {m: d for m, d in self.params_by_model.items() if m in self.sel_models}
        per_model = {m: model_variables(per_ens) for m, per_ens in scope.items()}
        counts, total = union_counts(per_model)
        if not counts:
            self.var_list.set_items([])
            self.var_list.set_message("No variables were found for the selected models "
                                      "and ensembles.")
            self._on_variable_change()
            return
        shown = set(counts)
        notes: List[str] = []
        common = {k for k, n in counts.items() if n == total}
        if self.common_only_var.get():
            if common:
                shown = common
                if len(counts) > len(common):
                    notes.append(f"{len(counts) - len(common)} variable(s) are hidden because "
                                 f"they are not available in every model.")
            else:
                notes.append("No variable is shared by all models; showing all variables.")
        elif len(counts) > len(common):
            notes.append("A model that lacks a selected variable is skipped for it only.")
        items = []
        for k in shown:
            hint = VARIABLE_HINTS.get(k)
            label = f"{k}   \u2014   {hint}" if hint else k
            items.append((k, f"{label}   {count_label(counts[k], total)}".rstrip()))
        self.var_list.set_message("  ".join(notes))
        self.var_list.set_items(items)
        self._log(f"[INFO] Variables available: {len(shown)} (models counted: {total})")
        self._on_variable_change()

    # ------------------------------------------------------------
    # Options / queue
    # ------------------------------------------------------------

    def browse_dir(self):
        d = filedialog.askdirectory(title="Select output folder", parent=self)
        if d:
            self.out_dir_var.set(d)

    def open_output_folder(self):
        path = os.path.abspath(os.path.expanduser(self.out_dir_var.get().strip() or "."))
        if os.path.isdir(path):
            open_folder(path)
        else:
            messagebox.showinfo("Open folder", f"The folder does not exist yet:\n{path}", parent=self)

    def _parse_years(self) -> Tuple[int, int]:
        try:
            y0 = int(self.y0_var.get().strip())
            y1 = int(self.y1_var.get().strip())
        except ValueError:
            raise ValueError("Please enter whole numbers for the start and end year.")
        if y0 > y1:
            raise ValueError("The start year must not be after the end year.")
        return y0, y1

    def _version_mode(self) -> Tuple[str, bool]:
        """Return (text_filter, latest_only) for the current version setting."""
        v = self.version_var.get().strip()
        if v == LATEST_VERSION_LABEL:
            return "", True
        if v in ("", ALL_VERSIONS_LABEL):
            return "", False
        return v, False

    def _build_queue(self):
        try:
            y0, y1 = self._parse_years()
        except ValueError as e:
            messagebox.showwarning("Invalid years", str(e), parent=self)
            return
        out_dir_raw = self.out_dir_var.get().strip()
        if not out_dir_raw:
            messagebox.showwarning("Save location", "Please choose an output folder.", parent=self)
            return
        if not (self.sel_models and self.sel_scenario and self.sel_params
                and (self.sel_ensembles or self.all_ens_var.get())
                and self.params_by_model is not None):
            messagebox.showwarning("Incomplete selection",
                                   "Please complete steps 1-4 first.", parent=self)
            return
        chosen = select_download_params(self.params_by_model, self.sel_models,
                                        self.sel_ensembles, self.all_ens_var.get())
        if not chosen:
            messagebox.showwarning("Incomplete selection",
                                   "None of the selected models has the selected "
                                   "ensembles.", parent=self)
            return
        subset: Optional[Dict[str, float]] = None
        if self.area_mode_var.get() == AREA_SUBSET:
            try:
                subset = parse_bbox(self.north_var.get(), self.south_var.get(),
                                    self.west_var.get(), self.east_var.get())
            except ValueError as e:
                messagebox.showwarning("Study area", str(e), parent=self)
                return

        version_text, latest_only = self._version_mode()
        self._queue_version_text = version_text
        self._queue_area_text = format_bbox(subset) if subset else ""
        spec = {
            "models": [m for m in self.sel_models if m in chosen],
            "scenario": self.sel_scenario,
            "params": list(self.sel_params),
            "params_by_model": chosen,
            "out_dir": os.path.abspath(os.path.expanduser(out_dir_raw)),
            "y0": y0,
            "y1": y1,
            "version_filter": version_text,
            "latest_only": latest_only,
            "subset": subset,
        }
        self._log("[INFO] Finding files (this may take a moment)\u2026")
        self._start_catalog_task("queue", "Finding files\u2026",
                                 lambda c: collect_download_items(c, spec))

    def _on_queue_built(self, data):
        if not data:
            self._set_status("Could not build the file list.")
            return
        items = data["items"]
        failures = data["failures"]
        if not items:
            self._set_status("No matching files found.")
            if failures:
                msg = ("No files could be listed because the catalog requests failed. "
                       "Check your connection and try again.")
            elif self._queue_version_text:
                msg = ("No files match your choices. Try a wider year range, or choose "
                       "'Latest version of each file' or 'All versions' in the file "
                       "version box.")
            else:
                msg = ("No files match your choices. Try a wider year range, or choose "
                       "'All versions' in the file version box.")
            messagebox.showinfo("No files found", msg, parent=self)
            return

        self.download_items = items
        self._refresh_queue_tree()
        n_models = len({it["model"] for it in items})
        n_exist = sum(1 for it in items if it.get("exists"))
        info = f"{len(items)} file(s) ready to download"
        if n_exist:
            info += f"  \u2022  {n_exist} already on disk"
        if n_models > 1:
            info += f"  \u2022  {n_models} models"
        if self._queue_area_text:
            info += f"  \u2022  area {self._queue_area_text}"
        self.queue_info_var.set(info)
        self._set_status(f"Found {len(items)} files.")
        self._log(f"[INFO] Queue built: {len(items)} files from {n_models} model(s), "
                  f"{n_exist} already on disk"
                  + (f", study area {self._queue_area_text}" if self._queue_area_text else ""))
        by_var: Dict[str, Set[str]] = {}
        for it in items:
            by_var.setdefault(it.get("variable", "?"), set()).add(it["model"])
        self._log("[INFO] Models per variable: "
                  + "; ".join(f"{v}: {len(ms)}" for v, ms in sorted(by_var.items())))
        self._reset_progress_display()
        self.max_pos = max(self.max_pos, self._page_pos(P_DOWNLOAD))
        self._show_step(self._page_pos(P_DOWNLOAD))
        if failures:
            messagebox.showwarning(
                "Incomplete list",
                f"{failures} catalog request(s) failed, so the list may be incomplete. "
                f"You can go back and press 'Find files' again.", parent=self)

    def _refresh_queue_tree(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for i, it in enumerate(self.download_items[:QUEUE_TABLE_SHOW_LIMIT]):
            exists = bool(it.get("exists"))
            self.tree.insert("", "end", iid=str(i),
                             values=("Skipped" if exists else "Pending", it["year_text"],
                                     it["filename"], it["out_dir"]),
                             tags=("skipped",) if exists else ())
        if len(self.download_items) > QUEUE_TABLE_SHOW_LIMIT:
            self._log(f"[INFO] Large queue: the table shows the first {QUEUE_TABLE_SHOW_LIMIT} "
                      f"rows, but all files will be downloaded.")

    def _tree_set_status(self, index: int, label: str, tag: str, see: bool = False):
        iid = str(index - 1)
        if index - 1 < QUEUE_TABLE_SHOW_LIMIT and self.tree.exists(iid):
            self.tree.set(iid, "status", label)
            self.tree.item(iid, tags=(tag,) if tag else ())
            if see:
                self.tree.see(iid)

    # ------------------------------------------------------------
    # Download control
    # ------------------------------------------------------------

    def _apply_dl_state(self):
        running, paused = self.is_downloading, self.is_paused
        busy = running or self._space_checking
        self.btn_start.configure(state="disabled" if busy else "normal")
        self.btn_stop.configure(state="normal" if running else "disabled")
        self.btn_pause.configure(state="normal" if (running and not paused) else "disabled")
        self.btn_resume.configure(state="normal" if (running and paused) else "disabled")
        self._refresh_ui_state()

    def _reset_progress_display(self):
        n = len(self.download_items)
        n_exist = sum(1 for it in self.download_items if it.get("exists"))
        self.cur_file_var.set("Current file: -")
        self.overall_var.set(f"Overall: {n_exist} / {n} files")
        self.pb_overall.configure(mode="determinate", maximum=max(1, n), value=n_exist)
        self._reset_file_bar()
        self._samples.clear()
        self._speed = 0.0
        for v in (self.speed_var, self.avg_var, self.downloaded_var, self.eta_var,
                  self.elapsed_var, self.remaining_var, self.rate_var, self.perfile_var):
            v.set("-")
        if n:
            self.remaining_var.set(str(max(0, n - n_exist)))

    def _reset_file_bar(self):
        """Stop any animation of the per-file bar and show it empty."""
        try:
            self.pb_file.stop()
        except Exception:
            pass
        self.pb_file.configure(mode="determinate", maximum=1, value=0)
        self._file_bar_mode = "determinate"

    def start_download(self):
        """Validate, then (whole-file mode only) probe the free disk space in a
        background thread (the probe is a network request and must never run on
        the UI thread), then continue in _on_space_probe() -> _launch_download()."""
        if self._space_checking:
            return
        if not self.download_items:
            messagebox.showwarning("Queue empty", "Find files first (step 6).", parent=self)
            return
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showinfo("Busy", "A download is already running.", parent=self)
            return
        if len(self.download_items) >= QUEUE_CONFIRM_THRESHOLD:
            if not messagebox.askyesno(
                    "Confirm", f"The queue has {len(self.download_items)} files.\nStart the download?",
                    parent=self):
                return

        out_dir = os.path.abspath(os.path.expanduser(self.out_dir_var.get().strip()))
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Output folder", f"Cannot create the output folder:\n{e}", parent=self)
            return

        # Refresh the "already on disk" flags (files may have appeared since the scan).
        for it in self.download_items:
            try:
                it["exists"] = os.path.exists(os.path.join(it["out_dir"], it["filename"]))
            except Exception:
                it["exists"] = False

        pending = [it for it in self.download_items if not it.get("exists")]
        # Study-area files are small and their size is not known in advance, so
        # the free-space probe is only done for whole-file downloads.
        if not pending or self.download_items[0].get("subset"):
            self._launch_download(out_dir)
            return

        self._space_checking = True
        self.btn_start.configure(state="disabled")
        self._set_status("Checking free disk space\u2026")
        self._refresh_ui_state()

        url = pending[0]["url"]
        n_pending = len(pending)

        def probe():
            try:
                size, _ = head_info(url)
            except Exception:
                size = None
            self.post_ui({"type": "space_probe", "size": size, "pending": n_pending,
                          "out_dir": out_dir})

        threading.Thread(target=probe, daemon=True).start()

    def _on_space_probe(self, ev: dict):
        self._space_checking = False
        if self.closing:
            return
        out_dir = ev["out_dir"]
        n_pending = ev["pending"]
        size = ev.get("size")
        proceed = True
        try:
            free = shutil.disk_usage(out_dir).free
            if not size:
                self._log(f"[WARN] Could not estimate the space needed for {n_pending} "
                          f"file(s). Free space: {format_bytes(free)}.")
            else:
                need = size * n_pending
                self._log(f"[INFO] Estimated space needed: about {format_bytes(need)} for "
                          f"{n_pending} file(s). Free space: {format_bytes(free)}.")
                if free < need:
                    proceed = messagebox.askyesno(
                        "Low disk space",
                        f"The download needs about {format_bytes(need)} "
                        f"({n_pending} files), but only {format_bytes(free)} is free on "
                        f"the output drive.\n\nContinue anyway?", parent=self)
        except Exception:
            proceed = True
        if not proceed:
            self._set_status("Download cancelled (low disk space).")
            self._apply_dl_state()
            return
        self._launch_download(out_dir)

    def _launch_download(self, out_dir: str):
        if not self.download_items:               # options changed during the probe
            self._apply_dl_state()
            return

        workers = self._read_int(self.workers_var, 1, 16, DEFAULT_WORKERS)
        segments = self._read_int(self.segments_var, 1, 32, DEFAULT_SEGMENTS)
        self.workers_var.set(str(workers))
        self.segments_var.set(str(segments))
        delete_partial = bool(self.delete_partial_var.get())
        self._save_config()

        items = list(self.download_items)
        n_exist = sum(1 for it in items if it.get("exists"))
        subset_mode = bool(items[0].get("subset"))
        self._dl_subset = subset_mode
        stop_event.clear()
        resume_event.set()
        self.tracker.start(len(items), preexisting=n_exist)
        self._speed = 0.0
        self._last_sample_ts = time.monotonic()
        self._last_sample_bytes = 0
        self._progress_err_logged = False

        for i in range(min(len(items), QUEUE_TABLE_SHOW_LIMIT)):
            if items[i].get("exists"):
                self._tree_set_status(i + 1, "Skipped", "skipped")
            else:
                self._tree_set_status(i + 1, "Pending", "")
        self._reset_progress_display()
        self.speed_var.set("Calculating\u2026")
        self.eta_var.set("Calculating\u2026")

        self.is_downloading = True
        self.is_paused = False
        self._apply_dl_state()
        self._set_status(f"Downloading {len(items)} file(s)\u2026")
        if subset_mode:
            self._log(f"[INFO] Download started: {len(items)} files ({n_exist} already on disk), "
                      f"study area {self._queue_area_text}, one connection per file.")
        else:
            self._log(f"[INFO] Download started: {len(items)} files ({n_exist} already on disk), "
                      f"{workers} connection(s), {segments} segment(s) per file.")

        self.download_thread = threading.Thread(
            target=self._run_downloads, args=(items, workers, segments, delete_partial),
            daemon=True, name="download-queue")
        self.download_thread.start()

    def _run_downloads(self, items: List[Dict], workers: int, segments: int, delete_partial: bool):
        try:
            res = run_download_queue(items, workers, segments, delete_partial,
                                     self.tracker, self.post_ui, self.post_log)
        except BaseException as e:           # the UI must always get a 'finished' event
            file_log("[ERR] Download thread error:\n" + traceback.format_exc())
            self.post_log(f"[ERR] Download thread error: {e}")
            res = {"ok": 0, "skipped": 0, "failed": 0, "stopped": True,
                   "disk_full": False, "not_attempted": 0}
        res["type"] = "dl_finished"
        self.post_ui(res)

    def pause_download(self):
        if self.is_downloading and not self.is_paused:
            resume_event.clear()
            self.tracker.pause()
            self.is_paused = True
            self._apply_dl_state()
            self._set_status("Paused.")
            self._log("[INFO] Paused.")

    def resume_download(self):
        if self.is_downloading and self.is_paused:
            resume_event.set()
            self.tracker.resume()
            self.is_paused = False
            self._samples.clear()
            self._apply_dl_state()
            self._set_status("Downloading\u2026")
            self._log("[INFO] Resumed.")

    def stop_download(self):
        if not self.is_downloading:
            return
        stop_event.set()
        resume_event.set()
        self.tracker.resume()
        self.btn_stop.configure(state="disabled")
        self.btn_pause.configure(state="disabled")
        self.btn_resume.configure(state="disabled")
        self._set_status("Stopping\u2026")
        self._log("[INFO] Stop requested\u2026")

    def _on_download_finished(self, ev: dict):
        self.is_downloading = False
        self.is_paused = False
        self.tracker.resume()
        self._refresh_progress()
        self._reset_file_bar()               # an indeterminate bar must not keep moving
        self._apply_dl_state()

        ok, skipped, failed = ev["ok"], ev["skipped"], ev["failed"]
        summary = f"{ok} downloaded, {skipped} skipped, {failed} failed"
        snap = self.tracker.snapshot()
        disk_full = bool(ev.get("disk_full"))
        left = ev.get("not_attempted", 0)
        self._log(f"[INFO] {'Stopped' if ev['stopped'] else 'Finished'}: {summary}. "
                  f"Total downloaded: {format_bytes(snap['session_bytes'])} in "
                  f"{format_duration(snap['active_seconds'])}.")
        if disk_full:
            self._set_status(f"Stopped: disk full ({summary}).")
            messagebox.showerror(
                "Disk full",
                f"The output drive ran out of free space, so the download was stopped "
                f"({summary}; {left} file(s) were not attempted).\n\n"
                f"Free some space, then press 'Start download' again. Completed files "
                f"are skipped and partial files are resumed.", parent=self)
            return
        if ev["stopped"]:
            self._set_status(f"Download stopped ({summary}).")
            return
        self._set_status(f"Download finished ({summary}).")
        if failed:
            messagebox.showwarning(
                "Download finished with errors",
                f"{summary}.\n\nPress 'Start download' again to retry the failed files; "
                f"files that are already complete will be skipped.", parent=self)
        else:
            messagebox.showinfo("Download finished", f"All done: {summary}.", parent=self)

    # ------------------------------------------------------------
    # Progress display
    # ------------------------------------------------------------

    def _set_file_bar(self, total: Optional[int], done: int):
        if total is None or total <= 0:
            if self._file_bar_mode != "indeterminate":
                self.pb_file.configure(mode="indeterminate")
                self.pb_file.start(15)
                self._file_bar_mode = "indeterminate"
            return
        if self._file_bar_mode != "determinate":
            self.pb_file.stop()
            self.pb_file.configure(mode="determinate")
            self._file_bar_mode = "determinate"
        self.pb_file.configure(maximum=total)
        self.pb_file["value"] = min(done, total)

    def _refresh_progress(self):
        snap = self.tracker.snapshot()
        now = time.monotonic()
        subset = self._dl_subset

        if subset:
            # Study areas: the server prepares every file before it sends it, so the
            # speed is the average over a sliding window (the waiting is included).
            self._samples.append((now, snap["session_bytes"]))
            while len(self._samples) > 1 and now - self._samples[0][0] > SUBSET_SPEED_WINDOW:
                self._samples.popleft()
            t0, b0 = self._samples[0]
            if now - t0 >= 1.0:
                self._speed = max(0.0, (snap["session_bytes"] - b0) / (now - t0))
        else:
            # whole files: smoothed speed (exponential moving average over ~0.5 s samples)
            dt = now - self._last_sample_ts
            if dt >= 0.5:
                inst = (snap["session_bytes"] - self._last_sample_bytes) / dt
                self._speed = inst if self._speed <= 0 else (0.35 * inst + 0.65 * self._speed)
                self._last_sample_ts = now
                self._last_sample_bytes = snap["session_bytes"]
        speed = 0.0 if snap["paused"] else self._speed
        avg = snap["session_bytes"] / snap["active_seconds"] if snap["active_seconds"] > 0.5 else 0.0

        total, done = snap["file_total"], snap["file_done"]
        self._set_file_bar(total, done)

        # Files that were already on disk count as finished from the start.
        files_total = snap["files_total"]
        effective = snap["files_done"] + snap["skip_pending"]
        frac = (done / total) if (total and total > 0) else 0.0
        in_progress = 0.0 if snap["cur_flagged"] else min(1.0, frac)
        self.pb_overall.configure(maximum=max(1, files_total))
        self.pb_overall["value"] = min(files_total, effective + in_progress)
        self.overall_var.set(f"Overall: {effective} / {files_total} files")

        if self._cur_file_name:
            parts = []
            if snap["phase"]:
                parts.append(snap["phase"])
            if total:
                parts.append(f"{format_bytes(done)} of {format_bytes(total)}")
            elif done:
                parts.append(format_bytes(done))
            suffix = f"  ({', '.join(parts)})" if parts else ""
            self.cur_file_var.set(f"Current file: {self._cur_file_name}{suffix}")

        self.speed_var.set("Paused" if snap["paused"] else format_speed(speed))
        self.avg_var.set(format_speed(avg) if avg else "-")
        self.downloaded_var.set(format_bytes(snap["session_bytes"]))
        self.elapsed_var.set(format_duration(snap["active_seconds"]))
        self.remaining_var.set(str(max(0, files_total - effective)))

        durs = snap["completed_durations"]
        if durs:
            recent = durs[-10:]
            avg_recent = sum(recent) / len(recent)
            self.rate_var.set(f"{60.0 / avg_recent:.1f}" if avg_recent > 0.001 else "-")
            mean = sum(durs) / len(durs)
            self.perfile_var.set(f"{mean:.1f}s" if mean < 10 else format_duration(mean))

        if snap["paused"]:
            self.eta_var.set("Paused")
        else:
            eta_speed = speed if speed > 0 else avg
            self.eta_var.set(format_eta(compute_eta(snap, eta_speed, subset)))

    # ------------------------------------------------------------
    # Close
    # ------------------------------------------------------------

    def on_close(self):
        if self.closing:
            return
        if self.is_downloading:
            if not messagebox.askyesno(
                    "Quit", "A download is in progress.\n\nQuit anyway? "
                            "Partial files stay on disk unless you chose to delete them, "
                            "so you can resume later.", parent=self):
                return
        self.closing = True
        self._save_config()

        stop_event.set()
        resume_event.set()
        self._cancel_catalog()

        t = self.download_thread
        if t and t.is_alive():
            try:
                t.join(timeout=3.0)
            except Exception:
                pass
        try:
            close_all_sessions()
        finally:
            self.destroy()


# ============================================================
# COMMAND-LINE (HEADLESS) MODE
# ============================================================

def _cli_post(ev: dict):
    """post_ui replacement for the CLI: print log lines and per-file progress."""
    try:
        et = ev.get("type")
        if et == "log":
            print(ev["msg"], flush=True)
            file_log(ev["msg"])
        elif et == "dl_file_start":
            print(f"[{ev['index']}/{ev.get('total', '?')}] {ev['filename']}", flush=True)
    except Exception:
        pass


def _cli_log(msg: str):
    _cli_post({"type": "log", "msg": msg})


def _cli_lookup(entries: Optional[List[Dict[str, Optional[str]]]],
                name: str) -> Optional[Dict[str, Optional[str]]]:
    for e in entries or []:
        if (e.get("title") or "").lower() == name.lower():
            return e
    return None


def _cli_version(value: str) -> Tuple[str, bool]:
    """Map the --version-filter argument to (text_filter, latest_only)."""
    v = (value or "").strip()
    low = v.lower()
    if low in ("latest", LATEST_VERSION_LABEL.lower()):
        return "", True
    if low in ("", "all", ALL_VERSIONS_LABEL.lower()):
        return "", False
    return v, False


def _cli_progress_loop(tracker: ProgressTracker, done: threading.Event, subset: bool = False):
    last_bytes = 0
    last_ts = time.monotonic()
    while not done.wait(10.0):
        snap = tracker.snapshot()
        now = time.monotonic()
        speed = (snap["session_bytes"] - last_bytes) / max(0.001, now - last_ts)
        last_bytes, last_ts = snap["session_bytes"], now
        eta = compute_eta(snap, speed, subset)
        _cli_log(f"[PROGRESS] {snap['files_done']}/{snap['files_total']} files, "
                 f"{format_bytes(snap['session_bytes'])} downloaded, "
                 f"{format_speed(speed)}, time left {format_eta(eta)}")


def run_cli(args) -> int:
    """Headless download: catalogs -> collect_download_items -> run_download_queue.
    args.bbox is None (whole files) or a dict from parse_bbox (study area)."""
    cancel = threading.Event()
    client = CatalogClient(_cli_post, cancel, 0)
    stop_event.clear()
    resume_event.set()
    try:
        models = client.scan_models()
        if models is None:
            _cli_log("[ERR] Could not load the model list.")
            return 1
        by_name = {m["title"]: m for m in models}
        if len(args.models) == 1 and args.models[0].lower() == "all":
            wanted = [m["title"] for m in models]
        else:
            wanted = []
            lower = {k.lower(): k for k in by_name}
            for name in args.models:
                key = lower.get(name.lower())
                if key is None:
                    _cli_log(f"[ERR] Unknown model: {name}")
                    return 2
                if key not in wanted:
                    wanted.append(key)

        params_by_model: Dict[str, Dict[str, Dict[str, Dict[str, Optional[str]]]]] = {}
        ens_names: List[str] = []
        var_names: List[str] = []
        scen_title: Optional[str] = None
        for m in wanted:
            scens = client.list_scenarios(by_name[m])
            if scens is None:
                _cli_log(f"[ERR] Could not load scenarios for {m}.")
                return 1
            sc = _cli_lookup(scens, args.scenario)
            if sc is None:
                _cli_log(f"[WARN] Scenario '{args.scenario}' is not available for {m}; skipped.")
                continue
            scen_title = scen_title or sc["title"]
            ens_list = client.list_ensembles(sc)
            if ens_list is None:
                _cli_log(f"[ERR] Could not load ensembles for {m}.")
                return 1
            if len(args.ensembles) == 1 and args.ensembles[0].lower() == "all":
                ens_to_use = [x["title"] for x in ens_list]     # every ensemble of this model
            else:
                ens_to_use = args.ensembles
            for en in ens_to_use:
                e = _cli_lookup(ens_list, en)
                if e is None:
                    _cli_log(f"[WARN] Ensemble '{en}' is not available for {m}; skipped.")
                    continue
                if e["title"] not in ens_names:
                    ens_names.append(e["title"])
                plist = client.list_parameters(e)
                if plist is None:
                    _cli_log(f"[ERR] Could not load variables for {m} / {e['title']}.")
                    return 1
                by_title = {p["title"]: p for p in plist if p.get("title")}
                low_vars = {k.lower(): k for k in by_title}
                sel: Dict[str, Dict[str, Optional[str]]] = {}
                for v in args.variables:
                    k = low_vars.get(v.lower())
                    if k is None:
                        _cli_log(f"[WARN] Variable '{v}' is not available in {m} / "
                                 f"{e['title']}; skipped.")
                        continue
                    sel[k] = by_title[k]
                    if k not in var_names:
                        var_names.append(k)
                params_by_model.setdefault(m, {})[e["title"]] = sel
        if not params_by_model or not var_names or scen_title is None:
            _cli_log("[ERR] Nothing to download for the given selection.")
            return 2

        version_text, latest_only = _cli_version(args.version_filter)
        bbox = getattr(args, "bbox", None)
        spec = {
            "models": list(params_by_model.keys()),
            "scenario": scen_title,
            "ensembles": ens_names,
            "params": var_names,
            "params_by_model": params_by_model,
            "out_dir": os.path.abspath(os.path.expanduser(args.out)),
            "y0": args.years[0],
            "y1": args.years[1],
            "version_filter": version_text,
            "latest_only": latest_only,
            "subset": bbox,
        }
        if bbox:
            _cli_log(f"[INFO] Study area: {format_bbox(bbox)}")
        data = collect_download_items(client, spec)
        items = data["items"]
        if data["failures"]:
            _cli_log(f"[WARN] {data['failures']} catalog request(s) failed; the list may be incomplete.")
        if not items:
            _cli_log("[ERR] No files match the given selection.")
            return 2
    except KeyboardInterrupt:
        cancel.set()
        _cli_log("[INFO] Interrupted.")
        return 130

    n_exist = sum(1 for it in items if it.get("exists"))
    _cli_log(f"[INFO] Queue built: {len(items)} files ({n_exist} already on disk).")
    tracker = ProgressTracker()
    tracker.start(len(items), preexisting=n_exist)
    workers = max(1, min(16, args.workers))
    segments = max(1, min(32, args.segments))
    result: Dict[str, object] = {}
    done = threading.Event()

    def worker():
        try:
            result.update(run_download_queue(items, workers, segments, False,
                                             tracker, _cli_post, _cli_log))
        except Exception as e:
            _cli_log(f"[ERR] Download error: {e}")
            result.update({"failed": 1, "stopped": True})
        finally:
            done.set()

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    threading.Thread(target=_cli_progress_loop,
                     args=(tracker, done, bool(items[0].get("subset"))), daemon=True).start()
    try:
        while t.is_alive():
            t.join(0.5)
    except KeyboardInterrupt:
        _cli_log("[INFO] Ctrl+C: stopping (partial files are kept)...")
        stop_event.set()
        resume_event.set()
        try:
            t.join(timeout=30)
        except KeyboardInterrupt:
            pass
    _cli_log(f"[INFO] Finished: {result.get('ok', 0)} downloaded, "
             f"{result.get('skipped', 0)} skipped, {result.get('failed', 0)} failed.")
    if result.get("stopped") or stop_event.is_set():
        return 130
    return 1 if (result.get("failed") or result.get("disk_full")) else 0


# ============================================================
# SELF TEST (offline, no tkinter)
# ============================================================

def _expect_value_error(fn, *args, contains: str = ""):
    try:
        fn(*args)
    except ValueError as e:
        assert contains.lower() in str(e).lower(), f"unexpected message: {e}"
        return
    raise AssertionError(f"ValueError expected for {args}")


def _self_test_area():
    """Study-area helpers: validation, URL, folder tag, queue building."""
    b = parse_bbox("43", "41", "36", "38")
    assert b == {"north": 43.0, "south": 41.0, "west": 36.0, "east": 38.0}
    # negative longitudes are converted to 0..360; commas and Persian digits work
    assert parse_bbox("10", "-5", "20", "30,5")["east"] == 30.5
    _expect_value_error(parse_bbox, "10", "-5", "-10", "10", contains="west")
    b3 = parse_bbox("10", "-5", "-20", "-10")
    assert b3["west"] == 340.0 and b3["east"] == 350.0
    b4 = parse_bbox("\u06f3\u06f8.\u06f5", "\u06f3\u06f6.\u06f5", "\u06f4\u06f4", "\u06f4\u06f6\u066b\u06f5")
    assert b4 == {"north": 38.5, "south": 36.5, "west": 44.0, "east": 46.5}
    _expect_value_error(parse_bbox, "", "41", "36", "38", contains="north")
    _expect_value_error(parse_bbox, "abc", "41", "36", "38", contains="number")
    _expect_value_error(parse_bbox, "nan", "41", "36", "38", contains="finite")
    _expect_value_error(parse_bbox, "41", "43", "36", "38", contains="greater")
    _expect_value_error(parse_bbox, "43", "41", "38", "36", contains="less than")
    _expect_value_error(parse_bbox, "95", "41", "36", "38", contains="between")
    _expect_value_error(parse_bbox, "43", "-70", "36", "38", contains="between")
    _expect_value_error(parse_bbox, "43", "41", "36", "400", contains="between")

    assert format_bbox(b4) == "N38.5 S36.5 W44 E46.5"
    assert subset_tag(b4) == "N38p5_S36p5_W44_E46p5"
    assert subset_tag(parse_bbox("10", "-5.25", "20", "30")) == "N10_Sm5p25_W20_E30"
    assert bbox_cells(b) == (8, 8)

    up = ("AMES/NEX/GDDP-CMIP6/ACCESS-CM2/historical/r1i1p1f1/pr/"
          "pr_day_ACCESS-CM2_historical_r1i1p1f1_gn_2014_v2.0.nc")
    url = build_ncss_url(up, "pr", b)
    assert url == (NCSS_BASE + up + "?var=pr&north=43&west=36&east=38&south=41"
                   "&horizStride=1&temporal=all&accept=netcdf4-classic"), url
    assert build_ncss_url("/" + up, "pr", b) == url

    # queue building with a fake catalog client (no network)
    import tempfile

    class _FakeClient:
        def __init__(self):
            self.cancel = threading.Event()
            self.logs: List[str] = []

        def log(self, m):
            self.logs.append(m)

        def status(self, m):
            pass

        def list_urlpaths(self, entry):
            return list(entry["paths"])

    base = "AMES/NEX/GDDP-CMIP6/M/ssp245/r1i1p1f1/pr/pr_day_M_ssp245_r1i1p1f1_gn_"
    paths = [base + "2015_v1.1.nc", base + "2015_v2.0.nc", base + "2016_v2.0.nc", "x/readme.txt"]
    tmp = tempfile.mkdtemp()
    try:
        spec = {"models": ["M"], "scenario": "ssp245", "ensembles": ["r1i1p1f1"],
                "params": ["pr"],
                "params_by_model": {"M": {"r1i1p1f1": {"pr": {"paths": paths}}}},
                "out_dir": tmp, "y0": 2015, "y1": 2015, "version_filter": "",
                "latest_only": True, "subset": None}
        res = collect_download_items(_FakeClient(), spec)
        assert len(res["items"]) == 1 and not res["failures"]
        it = res["items"][0]
        assert it["filename"].endswith("2015_v2.0.nc") and not it["subset"]
        assert it["url"].startswith(FILES_BASE) and "subset_" not in it["out_dir"]

        spec["subset"] = b4
        fc = _FakeClient()
        res = collect_download_items(fc, spec)
        it = res["items"][0]
        assert it["subset"] is True and it["url"].startswith(NCSS_BASE)
        assert "var=pr&north=38.5&west=44&east=46.5&south=36.5" in it["url"]
        assert os.path.join(tmp, "subset_N38p5_S36p5_W44_E46p5", "M", "ssp245",
                            "r1i1p1f1", "pr") == it["out_dir"]
        assert it["filename"] == "pr_day_M_ssp245_r1i1p1f1_gn_2015_v2.0.nc"
        assert any("Example request" in m for m in fc.logs)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _self_test_selection():
    """Counters, 'variables first' model selection and per-model download items."""
    counts, total = union_counts({"A": {"pr", "tasmax"}, "B": {"pr"}, "C": []})
    assert total == 3 and counts == {"pr": 2, "tasmax": 1}, counts
    assert count_label(2, 3) == "[2 of 3 models]" and count_label(1, 1) == ""

    pbm = {"A": {"e1": {"pr": 1, "tasmax": 2}, "e2": {"pr": 3}},
           "B": {"e1": {"pr": 4}}, "C": {"e1": {}}}
    assert models_with_variables(pbm, ["tasmax", "pr"]) == [
        ("A", ["tasmax", "pr"], []), ("B", ["pr"], ["tasmax"])]
    assert models_with_variables(pbm, ["tasmax"]) == [("A", ["tasmax"], [])]
    assert models_with_variables(pbm, ["rsds"]) == []
    assert select_download_params(pbm, ["A", "B"], ["e2"], False) == {"A": {"e2": {"pr": 3}}}
    sel = select_download_params(pbm, ["A", "B"], [], True)
    assert set(sel["A"]) == {"e1", "e2"} and set(sel["B"]) == {"e1"} and "C" not in sel

    import tempfile

    class _FakeClient:
        def __init__(self):
            self.cancel = threading.Event()
            self.logs: List[str] = []

        def log(self, m):
            self.logs.append(m)

        def status(self, m):
            pass

        def list_urlpaths(self, entry):
            return list(entry["paths"])

    def ent(m, e, v):
        return {"paths": [f"AMES/NEX/GDDP-CMIP6/{m}/historical/{e}/{v}/"
                          f"{v}_day_{m}_historical_{e}_gn_2014_v2.0.nc"]}

    # M has pr and tasmax in r1 and only pr in r2; N has only tasmax; P has nothing chosen
    chosen = {"M": {"r1": {"pr": ent("M", "r1", "pr"), "tasmax": ent("M", "r1", "tasmax")},
                    "r2": {"pr": ent("M", "r2", "pr")}},
              "N": {"r1": {"tasmax": ent("N", "r1", "tasmax")}}}
    tmp = tempfile.mkdtemp()
    try:
        spec = {"models": ["M", "N", "P"], "scenario": "historical", "params": ["pr", "tasmax"],
                "params_by_model": chosen, "out_dir": tmp, "y0": 2014, "y1": 2014,
                "version_filter": "", "latest_only": True, "subset": None}
        fc = _FakeClient()
        res = collect_download_items(fc, spec)
        got = {(it["model"], it["ensemble"], it["variable"]) for it in res["items"]}
        assert got == {("M", "r1", "pr"), ("M", "r1", "tasmax"), ("M", "r2", "pr"),
                       ("N", "r1", "tasmax")}, got
        assert not res["failures"]
        assert any("'pr' is not available in 1" in m and "N/r1" in m for m in fc.logs), fc.logs
        assert any("'tasmax' is not available in 1" in m and "M/r2" in m for m in fc.logs)
        assert any("model 'P'" in m for m in fc.logs)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _self_test_speed_and_cache():
    """Parallel catalog helper, disk catalog cache, ETA of study-area downloads."""
    import tempfile
    import time as _time

    # parallel_map keeps the order, survives exceptions, reports progress and cancels
    ev = threading.Event()
    seen_progress: List[int] = []

    def slow_square(x):
        _time.sleep(0.05)
        if x == 3:
            raise RuntimeError("boom")
        return x * x

    t0 = _time.monotonic()
    out = parallel_map(slow_square, list(range(8)), ev, workers=8,
                       on_done=lambda d, t: seen_progress.append(d))
    assert out == [0, 1, 4, None, 16, 25, 36, 49], out
    assert _time.monotonic() - t0 < 0.3                      # 8 x 0.05 s ran in parallel
    assert seen_progress == list(range(1, 9)) and parallel_map(abs, [], ev) == []
    ev.set()
    assert parallel_map(abs, [1, 2], ev) is None             # cancelled
    ev.clear()

    # disk cache: survives a new process (memory cleared), expires, can be cleared
    global CACHE_DIR, CACHE_TTL_SECONDS
    old_dir, old_ttl = CACHE_DIR, CACHE_TTL_SECONDS
    tmp = tempfile.mkdtemp()
    CACHE_DIR = os.path.join(tmp, "cache")
    try:
        cache_clear()
        assert cache_get("http://x/a.xml") is None
        cache_put("http://x/a.xml", b"<a>1</a>")
        cache_put("http://x/b.xml", b"<b>2</b>")
        with _catalog_cache_lock:
            _catalog_cache.clear()                           # as after a restart
        assert cache_get("http://x/a.xml") == b"<a>1</a>"
        assert len([f for f in os.listdir(CACHE_DIR) if f.endswith(".z")]) == 2
        cache_clear(["http://x/a.xml"])
        with _catalog_cache_lock:
            _catalog_cache.clear()
        assert cache_get("http://x/a.xml") is None and cache_get("http://x/b.xml") == b"<b>2</b>"
        with _catalog_cache_lock:
            _catalog_cache.clear()
        CACHE_TTL_SECONDS = -1                               # everything is too old
        assert cache_get("http://x/b.xml") is None
        CACHE_TTL_SECONDS = old_ttl
        with open(os.path.join(CACHE_DIR, "junk.z"), "wb") as fh:
            fh.write(b"not zlib")
        cache_clear()
        assert os.listdir(CACHE_DIR) == [] and cache_get("http://x/b.xml") is None
    finally:
        CACHE_DIR, CACHE_TTL_SECONDS = old_dir, old_ttl
        shutil.rmtree(tmp, ignore_errors=True)

    # Tracker: per-file durations, phase, pause handling
    tr = ProgressTracker()
    tr.start(5)
    tr.begin_file(False)
    tr.set_phase("waiting for the server")
    assert tr.snapshot()["phase"] == "waiting for the server"
    _time.sleep(0.2)
    tr.end_file("ok", False)
    snap = tr.snapshot()
    assert len(snap["completed_durations"]) == 1 and 0.15 < snap["completed_durations"][0] < 0.6
    assert snap["phase"] == ""
    tr.begin_file(False)
    tr.pause()
    _time.sleep(0.3)
    tr.resume()
    tr.end_file("ok", False)
    assert tr.snapshot()["completed_durations"][1] < 0.15    # the pause is not counted

    # ETA of a study-area queue: 8 s per file, tiny files. Bytes per second would be useless.
    snap = {"completed_sizes": [30000, 31000], "completed_durations": [8.0, 8.2, 7.8],
            "file_total": None, "file_done": 0, "cur_elapsed": 3.0, "files_total": 13,
            "files_done": 3, "skip_pending": 0, "cur_flagged": False}
    eta = estimate_eta_files(snap)
    assert abs(eta - ((8.0 - 3.0) + 8.0 * 9)) < 1e-6, eta     # current file + 9 more after it
    assert compute_eta(snap, 1e-9, True) == eta                # a tiny speed does not matter
    wrong = estimate_eta(snap, 1e-5)                           # what version 1.1 used to show
    assert wrong > 86400 * 30 and format_eta(wrong) == "> 30 days"
    assert compute_eta(dict(snap, completed_durations=[]), 5.0, True) is None
    assert format_eta(None) == "Calculating\u2026" and format_eta(75) == "1m 15s"
    assert format_eta(float("inf")) == "> 30 days"
    # whole files still use bytes / speed (falling back to file times when no speed yet)
    snap_g = {"completed_sizes": [100], "completed_durations": [10.0], "file_total": 100,
              "file_done": 50, "cur_elapsed": 5.0, "files_total": 4, "files_done": 1,
              "skip_pending": 1, "cur_flagged": False}
    assert compute_eta(snap_g, 10.0, False) == (50 + 100 * 1) / 10.0
    assert compute_eta(snap_g, 0.0, False) == estimate_eta_files(snap_g)


def _self_test_subset_download():
    """download_subset_file against a tiny local HTTP server (no internet)."""
    import http.server
    import tempfile

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"

        def log_message(self, *a):
            pass

        def _send(self, code, ctype, body, with_len=True):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            if with_len:
                self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/ok.nc":
                self._send(200, "application/x-netcdf", b"CDF\x01" + bytes(range(256)) * 20)
            elif path == "/nolen.nc":
                self._send(200, "application/x-netcdf",
                           b"\x89HDF\r\n\x1a\n" + b"x" * 3000, with_len=False)
            elif path == "/bad.nc":
                self._send(400, "text/html",
                           b"<html><body><h1>Error 400</h1><p>Bounding box has no data</p>"
                           b"</body></html>")
            elif path == "/html.nc":
                self._send(200, "text/html", b"<html>please log in</html>")
            elif path == "/junk.nc":
                self._send(200, "application/octet-stream", b"hello world")
            else:
                self._send(404, "text/plain", b"not found")

    srv = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    session = get_session()
    old_trust = session.trust_env
    session.trust_env = False            # never send the local test through a proxy
    stop_event.clear()
    resume_event.set()
    tmp = tempfile.mkdtemp()
    try:
        def run(name: str):
            tr = ProgressTracker()
            tr.start(1)
            return download_subset_file(f"{base}/{name}?var=pr", tmp, name, tr,
                                        lambda m: None, max_retries=1)

        st, det = run("ok.nc")
        assert st == "ok" and os.path.getsize(det) == 4 + 256 * 20, (st, det)
        assert not os.path.exists(det + ".part")
        assert run("ok.nc")[0] == "skipped"

        st, det = run("nolen.nc")                       # no Content-Length at all
        assert st == "ok" and os.path.getsize(det) == 8 + 3000, (st, det)

        st, det = run("bad.nc")
        assert st == "failed" and "400" in det and "Bounding box has no data" in det, det
        assert not os.path.exists(os.path.join(tmp, "bad.nc"))

        st, det = run("html.nc")
        assert st == "failed" and "text instead of NetCDF" in det, det

        st, det = run("junk.nc")
        assert st == "failed" and "not a valid NetCDF" in det, det
        assert not os.path.exists(os.path.join(tmp, "junk.nc"))
        assert not os.path.exists(os.path.join(tmp, "junk.nc.part"))

        st, det = run("missing.nc")
        assert st == "failed" and "404" in det, det

        # an existing but invalid file is renamed to .bad and fetched again
        with open(os.path.join(tmp, "ok.nc"), "wb") as fh:
            fh.write(b"garbage")
        st, det = run("ok.nc")
        assert st == "ok" and os.path.exists(os.path.join(tmp, "ok.nc.bad"))

        # whole queue through run_download_queue (subset flag selects the engine)
        out2 = os.path.join(tmp, "queue")
        items = [{"url": f"{base}/ok.nc?var=pr", "out_dir": out2, "filename": "ok.nc",
                  "subset": True, "exists": False},
                 {"url": f"{base}/bad.nc?var=pr", "out_dir": out2, "filename": "bad.nc",
                  "subset": True, "exists": False}]
        tr = ProgressTracker()
        tr.start(len(items))
        res = run_download_queue(items, 1, 1, False, tr, lambda ev: None, lambda m: None)
        assert res["ok"] == 1 and res["failed"] == 1 and not res["stopped"], res
    finally:
        session.trust_env = old_trust
        srv.shutdown()
        srv.server_close()
        shutil.rmtree(tmp, ignore_errors=True)


def _self_test():
    assert file_years_from_filename("tasmax_day_M_ssp245_r1i1p1f1_gn_2015_v2.0.nc") == (2015, 2015)
    assert file_years_from_filename("x_2015-2020_v1.1.nc") == (2015, 2020)
    assert file_years_from_filename("x_20150101-20201231.nc") == (2015, 2020)
    assert file_years_from_filename("readme.txt") == (None, None)
    assert years_overlap(2000, 2010, 2005, 2020) and not years_overlap(2000, 2004, 2005, 2020)
    assert not years_overlap(None, None, 2000, 2100)
    ns = "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"
    xml = (f'<catalog xmlns="{ns}"><dataset name="a" urlPath="x/a.nc"/>'
           f'<dataset name="b"><urlPath>y/b.nc</urlPath></dataset></catalog>')
    assert parse_urlpaths(xml.encode("utf-8")) == ["x/a.nc", "y/b.nc"]
    assert parse_urlpaths(xml) == ["x/a.nc", "y/b.nc"]
    assert parse_urlpaths(b"<not xml") == [] and parse_catalog_refs("") == []
    assert href_to_catalog_xml(BASE_CATALOG_XML, "M1/catalog.html", None) == \
        BASE_CATALOG + "/M1/catalog.xml"
    assert href_to_catalog_xml(BASE_CATALOG_XML, None, "M2") == BASE_CATALOG + "/M2/catalog.xml"
    assert version_key("a_v2.0.nc") == (2, 0) and version_key("a.nc") == (0,)
    assert version_key("a_v1.10.nc") > version_key("a_v1.9.nc") > version_key("a.nc")
    assert format_bytes(0) == "0 B" and format_bytes(1024) == "1.00 KB"
    assert format_bytes(1536) == "1.50 KB" and format_speed(1024) == "1.00 KB/s"
    assert format_duration(None) == "-" and format_duration(75) == "1m 15s"
    assert format_duration(3700) == "1h 1m"
    snap = {"completed_sizes": [100], "file_total": 100, "file_done": 50, "files_total": 4,
            "files_done": 1, "skip_pending": 1, "cur_flagged": False}
    assert estimate_eta(snap, 10.0) == (50 + 100 * 1) / 10.0   # 4 - 1 - 1 = 2 real, 1 current
    # unknown size of the current file (study-area downloads): falls back to the average
    snap2 = dict(snap, file_total=None, file_done=0)
    assert estimate_eta(snap2, 10.0) == (100 + 100 * 1) / 10.0
    _self_test_area()
    _self_test_selection()
    _self_test_speed_and_cache()
    _self_test_subset_download()


# ============================================================
# ENTRY POINT
# ============================================================

def _enable_hidpi():
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # type: ignore[attr-defined]
        except Exception:
            pass


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=f"{APP_NAME} v{APP_VERSION}. Without arguments the GUI starts.")
    p.add_argument("--cli", action="store_true", help="headless download (no GUI)")
    p.add_argument("--self-test", action="store_true", help="run offline unit tests and exit")
    p.add_argument("--models", nargs="+", help="model names, or 'all'")
    p.add_argument("--scenario", help="e.g. historical, ssp245")
    p.add_argument("--ensembles", nargs="+", default=["r1i1p1f1"],
                   help="e.g. r1i1p1f1, or 'all' for every ensemble each model has")
    p.add_argument("--variables", nargs="+", help="e.g. tasmax tasmin pr")
    p.add_argument("--years", nargs=2, type=int, metavar=("Y0", "Y1"),
                   default=[MIN_YEAR, MAX_YEAR], help="inclusive year range")
    p.add_argument("--bbox", nargs=4, metavar=("NORTH", "SOUTH", "WEST", "EAST"),
                   help="download only this study area (decimal degrees; longitudes "
                        "may be -180..360). Without it, whole files are downloaded.")
    p.add_argument("--out", default="cmip6_downloads", help="output folder")
    p.add_argument("--version-filter", default="latest",
                   help="'latest' (default), 'all', or text such as _v2.0.nc")
    p.add_argument("--workers", type=int, default=DEFAULT_WORKERS,
                   help="parallel connections (whole-file mode)")
    p.add_argument("--segments", type=int, default=DEFAULT_SEGMENTS,
                   help="segments per file (whole-file mode)")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        _self_test()
        print("Self-test passed.")
        return 0

    setup_file_logging()
    install_crash_handlers()

    if args.cli:
        if not (args.models and args.scenario and args.variables):
            parser.error("--cli requires --models, --scenario and --variables")
        if args.years[0] > args.years[1]:
            parser.error("--years: Y0 must not be greater than Y1")
        if args.bbox:
            try:
                args.bbox = parse_bbox(*args.bbox)
            except ValueError as e:
                parser.error(f"--bbox: {e}")
        try:
            return run_cli(args)
        finally:
            close_all_sessions()

    if not HAVE_TK:
        print("tkinter is not available. Install it, or use --cli.", file=sys.stderr)
        return 1

    _enable_hidpi()
    file_log(f"[INFO] Starting GUI: Python {sys.version.split()[0]}, Tk {tk.TkVersion}, "
             f"platform {sys.platform}")
    app = None
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        stop_event.set()
        resume_event.set()
    except Exception:
        file_log("[FATAL] GUI crashed:\n" + traceback.format_exc())
        raise
    finally:
        stop_event.set()
        resume_event.set()
        close_all_sessions()
        # Release the Tk objects here, on the main thread. Then, if any
        # background thread is still running, leave right away instead of
        # letting the interpreter finalize underneath it.
        app = None
        gc.collect()
        exit_if_threads_alive(0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
