"""
utils package — explicitly import all submodules so 
'from utils import db_manager' always works regardless of 
how Python resolves the package path.
"""
import os as _os
import sys as _sys
import importlib as _importlib

# Ensure the project root (parent of this utils/ folder) is on sys.path
_pkg_dir = _os.path.dirname(_os.path.abspath(__file__))
_project_root = _os.path.dirname(_pkg_dir)
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)

# Explicitly load each submodule and bind it as a package attribute
for _mod_name in ("db_manager", "ai_helpers", "pdf_generator"):
    try:
        _mod = _importlib.import_module(f"utils.{_mod_name}")
        globals()[_mod_name] = _mod
    except Exception:
        # Fall back to direct file load
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            _mod_name,
            _os.path.join(_pkg_dir, f"{_mod_name}.py")
        )
        if _spec:
            _m = _ilu.module_from_spec(_spec)
            _sys.modules[f"utils.{_mod_name}"] = _m
            _spec.loader.exec_module(_m)
            globals()[_mod_name] = _m

from utils import db_manager, ai_helpers, pdf_generator  # noqa: E402

__all__ = ["db_manager", "ai_helpers", "pdf_generator"]
