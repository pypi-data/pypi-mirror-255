# Copyright 2023-2024 Vincent Jacques

"""
The ``lincs`` package
=====================

This is the main module for the *lincs* library.
It contains general information (version, GPU availability, *etc.*) and items of general usage (*e.g.* the exception for invalid data).
"""


# start delvewheel patch
def _delvewheel_patch_1_5_2():
    import os
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, '.'))
    if os.path.isdir(libs_dir):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_5_2()
del _delvewheel_patch_1_5_2
# end delvewheel patch

# General exceptions
from liblincs import DataValidationException, LearningFailureException

# General utilities
from liblincs import UniformRandomBitsGenerator

# Classification
from . import classification

# General information
__version__ = "1.1.0a16"
has_gpu = hasattr(classification, "ImproveProfilesWithAccuracyHeuristicOnGpu")

try:
    del visualization
except NameError:
    pass

try:
    del description
except NameError:
    pass

try:
    del command_line_interface
except NameError:
    pass