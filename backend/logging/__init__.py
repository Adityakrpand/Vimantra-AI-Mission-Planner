from __future__ import annotations

import importlib.util
import sysconfig
from pathlib import Path

_STDLIB_LOGGING_PATH = Path(sysconfig.get_path("stdlib")) / "logging" / "__init__.py"
_SPEC = importlib.util.spec_from_file_location("_vimantra_stdlib_logging", _STDLIB_LOGGING_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("Unable to load Python standard logging package.")

_stdlib_logging = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_stdlib_logging)

for _name in dir(_stdlib_logging):
    if _name.startswith("__") and _name not in {"__all__", "__doc__"}:
        continue
    globals()[_name] = getattr(_stdlib_logging, _name)

__all__ = list(getattr(_stdlib_logging, "__all__", []))
