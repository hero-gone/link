import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _is_m3u(path: pathlib.Path) -> bool:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
        return first_line == "#EXTM3U"
    except Exception:
        return False


# Include *.json files plus known JSON files without .json extension
_EXTRA_JSON = [REPO_ROOT / "chat_app_json"]
JSON_FILES = sorted(
    list(REPO_ROOT.glob("*.json"))
    + [p for p in _EXTRA_JSON if p.exists()]
)
M3U_FILES = sorted(
    [p for p in REPO_ROOT.iterdir() if p.suffix in (".m3u8", ".m3u")]
    + [p for p in REPO_ROOT.iterdir() if p.suffix == ".ts" and _is_m3u(p)]
)
BASH_SCRIPTS = [REPO_ROOT / "mdmlink"]


@pytest.fixture(params=[str(p) for p in JSON_FILES], ids=[p.name for p in JSON_FILES])
def json_file(request):
    return pathlib.Path(request.param)


@pytest.fixture(
    params=[str(p) for p in M3U_FILES],
    ids=[p.name for p in M3U_FILES],
)
def m3u_file(request):
    return pathlib.Path(request.param)


@pytest.fixture(
    params=[str(p) for p in BASH_SCRIPTS],
    ids=[p.name for p in BASH_SCRIPTS],
)
def bash_script(request):
    return pathlib.Path(request.param)
