from importlib.resources import files as _files
import inspect as _inspect
from pathlib import Path as _Path

from pkgdata import exception as _exception


def get_from_name(name: str = "", root: bool = False, stack_up: int = 0) -> _Path:
    """Get the local path to an installed package.

    Parameters
    ----------
    name : str, optional
        Fully qualified name of the package, e.g., "some_package" or "some_package.some_subpackage".
        If not provided, the name of the caller's package is used.
    root : bool, default: False
        Whether to return the path to the package's root directory,
        even if `name` corresponds to a subpackage.
    stack_up : int, default: 0
        Number of frames to go up in the call stack to determine the caller's package name,
        when `name` is not provided.

    Returns
    -------
    path : pathlib.Path
        Path to the package.

    Raises
    ------
    pkgdata.exception.PkgDataPackagePathError
        If the local path to the package cannot be determined.
    pkgdata.exception.PkgDataCallerPackageNameError
        If 'name' is not provided
        and the name of the caller's package cannot be automatically determined.
    """
    if not name:
        name = _get_caller_name(stack_up=stack_up)
    if root:
        name = name.split(".")[0]
    try:
        path = _Path(_files(name))
    except Exception as e:
        raise _exception.PkgDataPackagePathError(name=name) from e
    return path


def _get_caller_name(stack_up: int = 0) -> str:
    """Get the name of the caller's package.

    Parameters
    ----------
    stack_up : int, default: 0
        Number of frames to go up in the call stack to determine the caller's package name.

    Returns
    -------
    name : str
        Name of the caller's package.

    Raises
    ------
    pkgdata.exception.PkgDataCallerPackageNameError
        If the name of the caller's package cannot be automatically determined.
    """
    stack = _inspect.stack()
    # Get the caller's frame
    # Since this is a helper function for other functions, we need to at least go up 2 frames
    # to get the direct external caller's package name
    try:
        caller_frame = stack[2 + stack_up]
    except IndexError:
        raise _exception.PkgDataCallerPackageNameError(stack=stack[2:], stack_up=stack_up)
    # Get the caller's package name from the frame
    package_name = caller_frame.frame.f_globals["__package__"]
    if package_name is None:
        raise _exception.PkgDataCallerPackageNameError(stack=stack[2:], stack_up=stack_up)
    return package_name
