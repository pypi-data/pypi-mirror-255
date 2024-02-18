"""Utility functions for the OpenDAPI client."""

import importlib
import inspect
import logging
import os
import re
from typing import List

logger = logging.getLogger(__name__)


def get_root_dir_fullpath(current_filepath: str, root_dir_name: str):
    """Get the full path of the root directory"""
    return os.path.join(
        f"/{root_dir_name}".join(
            os.path.dirname(os.path.abspath(current_filepath)).split(root_dir_name)[:-1]
        ),
        root_dir_name,
    )


def find_subclasses_in_directory(
    root_dir: str, base_class, exclude_dirs: List[str] = None
):
    """Find subclasses of a base class in modules in a root_dir"""
    subclasses = []
    exclude_dirs_pattern = re.compile(r"^(?:" + "|".join(exclude_dirs) + r")$")
    for root, dirs, filenames in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if not exclude_dirs_pattern.match(d)]
        filenames = [f for f in filenames if f.endswith(".py")]
        for filename in filenames:
            py_file = os.path.join(root, filename)
            rel_py_file = py_file.split(f"{root_dir}/")[1]
            module_name = rel_py_file.replace("/", ".").replace(".py", "")
            try:
                module = importlib.import_module(module_name)
                for _, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, base_class)
                        and obj != base_class
                        and obj not in subclasses
                    ):
                        subclasses.append(obj)
            except ImportError:
                logger.warning("Could not import module %s", module_name)
    return subclasses
