"""Exceptions raised by PkgData."""


from pathlib import Path as _Path
import inspect as _inspect


class PkgDataException(Exception):
    """Base class for all exceptions raised by PkgData."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        return


class PkgDataStackTooShallowError(PkgDataException):
    """Exception raised when the call stack is too shallow
    to retrieve the caller frame with the given stack level.

    Attributes
    ----------
    stack : list[inspect.FrameInfo]
        Available Call stack frames.
    stack_up : int
        Requested stack level to go up.
    """
    def __init__(self, stack: list[_inspect.FrameInfo], stack_up: int):
        self.stack: list[_inspect.FrameInfo] = stack
        self.stack_up: int = stack_up
        message = (
            "The call stack is too shallow for the requested caller frame; "
            f"the input 'stack_up' argument was {stack_up}, "
            f"but the call stack has only {len(stack)} frames."
        )
        super().__init__(message)
        return


class PkgDataCallerPackageNameError(PkgDataException):
    """Exception raised when the name of the caller's package cannot be determined.

    Attributes
    ----------
    frame_info : inspect.FrameInfo
        Frame information of the caller.
    """
    def __init__(self, frame_info: _inspect.FrameInfo):
        message = (
            "Could not determine the name of the caller's package; "
            f"the caller '{frame_info.frame.f_globals['__name__']}' "
            f"has no package name."
        )
        super().__init__(message)
        self.frame_info: _inspect.FrameInfo = frame_info
        return


class PkgDataModuleNotFoundError(PkgDataException):
    """Exception raised when a module cannot be found at the given path.

    Attributes
    ----------
    module_path : pathlib.Path
        Path to the module as provided by the user.
    """
    def __init__(self, path: _Path):
        self.module_path = path
        message = f"Could not find a module at path '{path}'."
        super().__init__(message)
        return


class PkgDataPackageNotFoundError(PkgDataException):
    """Exception raised when a package cannot be found.

    Attributes
    ----------
    package_name : str
        Name of the missing package.
    available_package_names : tuple[str, ...]
        Names of all available packages.
    """
    def __init__(self, package_name: str, available_package_names: tuple[str, ...]):
        message = (
            f"Could not find an installed package named '{package_name}'. "
            f"Available packages are: {available_package_names}."
        )
        super().__init__(message)
        self.package_name = package_name
        self.available_package_names = available_package_names
        return


class PkgDataDistributionNotFoundError(PkgDataException):
    """Exception raised when a distribution package cannot be found.

    Attributes
    ----------
    distribution_name : str
        Name of the missing package distribution.
    available_distribution_names : tuple[str, ...]
        Names of all available distribution packages.
    """
    def __init__(self, distribution_name: str, available_distribution_names: tuple[str, ...]):
        message = (
            f"Could not find an installed distribution named '{distribution_name}'. "
            f"Available distribution packages are: {available_distribution_names}."
        )
        super().__init__(message)
        self.distribution_name = distribution_name
        self.available_distribution_names = available_distribution_names
        return


class PkgDataMultipleDistributionsError(PkgDataException):
    """Exception raised when multiple distribution packages are found for an import package.

    Attributes
    ----------
    package_name : str
        Name of the import package.
    distribution_names : tuple[str, ...]
        Names of all found distribution packages.
    """
    def __init__(self, package_name: str, distribution_names: tuple[str, ...]):
        message = (
            f"Found multiple distribution packages for the import package '{package_name}': "
            f"{distribution_names}."
        )
        super().__init__(message)
        self.package_name = package_name
        self.distribution_names = distribution_names
        return


class PkgDataModuleImportError(PkgDataException):
    """Exception raised when a module cannot be imported."""
    def __init__(self, name: str, path: _Path):
        self.module_name = name
        self.module_path = path
        message = f"Failed to import module '{name}' from path '{path}'."
        super().__init__(message)
        return


class PkgDataPackagePathError(PkgDataException):
    """Could not find the local path to an installed package."""
    def __init__(self, name: str):
        self.package_name = name
        message = f"Could not find the local path to the package '{name}'."
        super().__init__(message)
        return
