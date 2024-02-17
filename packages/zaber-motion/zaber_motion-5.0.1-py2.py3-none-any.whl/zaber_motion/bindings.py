from ctypes import c_void_p, c_int, c_int64, c_uint8, CFUNCTYPE
from typing import Any
import platform
import sys
import importlib
from .version import __version__


def _load_library() -> Any:
    is64bit = sys.maxsize > 2**32
    os_system = platform.system().lower()
    os_machine = platform.machine().lower()

    if os_system == "darwin":
        arch = "uni"
    else:
        if os_machine.startswith("aarch64") or os_machine.startswith("arm"):
            arch = "arm64" if is64bit else "arm"
        else:
            arch = "amd64" if is64bit else "386"

    ext = ""
    if os_system == "linux":
        ext = ".so"
    if os_system == "darwin":
        ext = ".dylib"

    lib_name = f"zaber-motion-lib-{os_system}-{arch}{ext}"
    module_name = f"zaber_motion_bindings_{os_system}"
    binding_module = importlib.import_module(module_name)
    if __version__ != binding_module.__version__:
        raise RuntimeError((
            f"The dependent module {module_name} is not compatible with "
            f"zaber_motion ({__version__} != {binding_module.__version__}). "
            f"Please install the correct version {module_name}=={__version__}."))
    return binding_module.load_library(lib_name)


lib = _load_library()

CALLBACK = CFUNCTYPE(None, c_void_p, c_int64)

c_call = lib.call
c_call.argtypes = [c_void_p, c_int64, CALLBACK, c_uint8]
c_call.restype = c_int

c_set_event_handler = lib.setEventHandler
c_set_event_handler.argtypes = [c_int64, CALLBACK]
c_set_event_handler.restype = None
