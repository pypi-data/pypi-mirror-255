from pathlib import Path as _Path
import inspect as _inspect


class PkgDataError(Exception):
    """Base class for all PkgData exceptions."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        return


class PkgDataModuleNotFoundError(PkgDataError):
    """Could not find a module to import from the given path."""
    def __init__(self, path: _Path):
        self.module_path = path
        message = f"Could not find a module to import from path '{path}'."
        super().__init__(message)
        return


class PkgDataModuleImportError(PkgDataError):
    """Could not import a module."""
    def __init__(self, name: str, path: _Path):
        self.module_name = name
        self.module_path = path
        message = f"Failed to import module '{name}' from path '{path}'."
        super().__init__(message)
        return


class PkgDataCallerPackageNameError(PkgDataError):
    """Could not determine the name of the caller's package."""
    def __init__(self, stack: list[_inspect.FrameInfo], stack_up: int):
        self.stack: list[_inspect.FrameInfo] = stack
        self.stack_up: int = stack_up
        message = "Could not determine the name of the caller's package; "
        if len(stack) <= stack_up:
            message += (
                f"the input 'stack_up' value was {stack_up}, "
                f"but the call stack has only {len(stack)} frames."
            )
        else:
            caller_frame = stack[stack_up]
            message += (
                f"the caller '{caller_frame.frame.f_globals['__name__']}' "
                f"at stack frame {stack_up} has no package name."
            )
        super().__init__(message)
        return


class PkgDataPackagePathError(PkgDataError):
    """Could not find the local path to an installed package."""
    def __init__(self, name: str):
        self.package_name = name
        message = f"Could not find the local path to the package '{name}'."
        super().__init__(message)
        return
