from __future__ import annotations

import importlib.util
import sysconfig
from pathlib import Path

_STDLIB_CONFIG_PATH = Path(sysconfig.get_path("stdlib")) / "logging" / "config.py"
_SPEC = importlib.util.spec_from_file_location(
    "_vimantra_stdlib_logging_config",
    _STDLIB_CONFIG_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("Unable to load Python standard logging config module.")

_stdlib_config = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_stdlib_config)

for _name in dir(_stdlib_config):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_stdlib_config, _name)
