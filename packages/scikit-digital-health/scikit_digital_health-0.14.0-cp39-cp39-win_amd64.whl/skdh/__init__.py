"""
Scikit Digital Health (:mod:`skdh`)
===================================

.. currentmodule:: skdh

Pipeline Processing
-------------------

.. autosummary::
    :toctree: generated/

    Pipeline
"""


# start delvewheel patch
def _delvewheel_patch_1_5_2():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'scikit_digital_health.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-scikit_digital_health-0.14.0')
        if os.path.isfile(load_order_filepath):
            with open(os.path.join(libs_dir, '.load-order-scikit_digital_health-0.14.0')) as file:
                load_order = file.read().split()
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(ctypes.c_wchar_p(lib_path), None, 0x00000008):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_5_2()
del _delvewheel_patch_1_5_2
# end delvewheel patch

from sys import version_info

if version_info >= (3, 8):
    import importlib.metadata

    __version__ = importlib.metadata.version("scikit-digital-health")
else:  # pragma: no cover
    import importlib_metadata

    __version__ = importlib_metadata.version("scikit-digital-health")

__minimum_version__ = "0.9.10"

from skdh.pipeline import Pipeline
from skdh.base import BaseProcess, handle_process_returns

from skdh import utility
from skdh import io
from skdh import preprocessing
from skdh import sleep
from skdh import activity
from skdh import gait_old
from skdh import gait
from skdh import sit2stand
from skdh import features
from skdh import context

__skdh_version__ = __version__


__all__ = [
    "Pipeline",
    "BaseProcess",
    "activity",
    "gait_old",
    "gait",
    "sit2stand",
    "io",
    "sleep",
    "preprocessing",
    "features",
    "utility",
    "context",
    "__skdh_version__",
]