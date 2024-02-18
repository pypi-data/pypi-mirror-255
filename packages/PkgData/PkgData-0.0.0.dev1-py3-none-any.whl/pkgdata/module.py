from types import ModuleType as _ModuleType
import importlib.util as _importlib_util
import sys as _sys
from pathlib import Path as _Path

from pkgdata import exception as _exception


def import_from_path(path: str | _Path, name: str | None = None) -> _ModuleType:
    """Import a Python module from a local path.

    Parameters
    ----------
    path : str | pathlib.Path
        Local path to the module.
        If the path corresponds to a directory,
        the `__init__.py` file in the directory is imported.
    name : str | None, default: None
        Name to assign to the imported module.
        If not provided (i.e., None), the name is determined from the path as follows:
        - If the path corresponds to a directory, the directory name is used.
        - If the path corresponds to a `__init__.py` file, the parent directory name is used.
        - Otherwise, the filename is used.

    Returns
    -------
    module : types.ModuleType
        The imported module.

    Raises
    ------
    pkgdata.exception.PkgDataModuleNotFoundError
        If no module file can be found at the given path.
    pkgdata.exception.PkgDataModuleImportError
        If the module cannot be imported.

    References
    ----------
    - [Python Documentation: importlib — The implementation of import: Importing a source file directly](https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly)
    """
    path = _Path(path).resolve()
    if path.is_dir():
        path = path / "__init__.py"
    if not path.exists():
        raise _exception.PkgDataModuleNotFoundError(path=path)
    if name is None:
        name = path.parent.stem if path.name == "__init__.py" else path.stem
    try:
        spec = _importlib_util.spec_from_file_location(name=name, location=path)
        module = _importlib_util.module_from_spec(spec)
        _sys.modules[name] = module
        spec.loader.exec_module(module)
    except Exception as e:
        raise _exception.PkgDataModuleImportError(name=name, path=path) from e
    return module
