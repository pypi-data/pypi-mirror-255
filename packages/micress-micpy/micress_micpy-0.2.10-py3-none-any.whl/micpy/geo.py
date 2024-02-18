"""This module provides methods to read and write geometry files."""

import enum
import gzip

from typing import Tuple
from pathlib import Path

import numpy as np
from numpy import ndarray

__all__ = [
    "Type",
    "GeometryFileError",
    "GeometryFileNotFoundError",
    "MultipleGeometryFilesError",
    "find",
    "read",
    "read_ndarray",
    "write",
    "write_ndarray",
]


BASIC_MODEL = [
    ("basic_header", np.int32),
    ("shape", np.int32, (3,)),
    ("spacing", np.float32, (3,)),
    ("basic_footer", np.int32),
]

EXTENSION_MODEL = [
    ("extension_header", np.int32),
    ("version", np.string_, 10),
    ("compile_date", np.string_, 10),
    ("run_date", np.string_, 10),
    ("platform", np.string_, 10),
    ("precision", np.string_, 10),
    ("extension_footer", np.int32),
]


class Type(enum.Enum):
    """Data type of geometry file."""

    BASIC = np.dtype(BASIC_MODEL)
    EXTENDED = np.dtype(BASIC_MODEL + EXTENSION_MODEL)


class GeometryFileError(Exception):
    """Base exception for geometry file errors."""


class GeometryFileNotFoundError(GeometryFileError):
    """Raised when a geometry file is not found."""


class MultipleGeometryFilesError(GeometryFileError):
    """Raised when multiple potential geometry files are found."""


def find(filename: str) -> str:
    """Find the geometry file for a given binary file.

    This method assumes that (a) both files share a common basename and (b) the
    file extension of the geometry file starts with either `.geoF` or `_geoF`.

    Args:
        filename (str): Filename of a binary file.

    Returns:
        Path: Path to the geometry file.
    """
    basename = _get_basename(Path(filename))
    matches = list(basename.parent.glob(f"{basename.name}[._]geoF*"))

    if not matches:
        raise GeometryFileNotFoundError("Geometry file not found")

    first_match, *other_matches = matches
    if other_matches:
        raise MultipleGeometryFilesError("Multiple geometry files found")

    return Path(first_match)


def read(filename: str, type: Type = Type.EXTENDED, compressed: bool = True) -> dict:
    """Read a geometry file.

    Args:
        filename (str): Filename of a geometry file.
        type (Type, optional): Data type to be read.
        compressed (bool, optional): True if file is compressed, False otherwise.
            Defaults to True.

    Returns:
        dict: Dictionary representation of the geometry file.
    """
    array_data = read_ndarray(filename, type, compressed)
    return _ndarray_to_dict(array_data)


def read_ndarray(
    filename: str, type: Type = Type.EXTENDED, compressed: bool = True
) -> ndarray:
    """Read a geometry file.

    Args:
        filename (str): Filename of a geometry file.
        type (Type, optional): Data type to be read. Defaults to Type.EXTENDED.
        compressed (bool, optional): True if file is compressed, False otherwise.
            Defaults to True.

    Returns:
        ndarray: NumPy array representation of the geometry file.
    """
    opener = gzip.open if compressed else open
    with opener(filename, "rb") as f:
        return np.frombuffer(f.read(type.value.itemsize), dtype=type.value)


def write(
    filename: str,
    data: dict,
    type: Type = Type.EXTENDED,
    compressed: bool = True,
):
    """Write a geometry file.

    Args:
        filename (str): Filename of a geometry file.
        data (dict): Dictionary representation of a geometry file.
        type (Type, optional): Data type to be written. Defaults to Type.EXTENDED.
        compressed (bool, optional): True if file should be compressed, False otherwise.
            Defaults to True.
    """
    array_data = _dict_to_ndarray(data, type)
    write_ndarray(filename, array_data, compressed)


def write_ndarray(filename: str, data: ndarray, compressed: bool = True):
    """Write a geometry file.

    Args:
        filename (str): Filename of a geometry file.
        data (ndarray): NumPy array representation of a geometry file.
        compressed (bool, optional): True if file should be compressed, False otherwise.
            Defaults to True.
    """
    if not _validate_data_type(data):
        raise ValueError("Invalid data type")
    if not _validate_header_footer(data):
        raise ValueError("Mismatched header and footer sizes")

    opener = gzip.open if compressed else open
    with opener(filename, mode="wb") as f:
        f.write(data.tobytes())


def get_basic(
    filename: str, shape: Tuple[int, int, int], spacing: Tuple[float, float, float]
) -> Tuple[str, dict, Type]:
    """Create a basic geometry.

    Args:
        filename (str): Filename of a binary file.
        shape (tuple): Shape of the geometry.
        spacing (tuple): Spacing of the geometry.
    """
    geo_filename = _get_basename(Path(filename)).with_suffix(".geoF")
    geo_data = {
        "basic_header": 24,
        "shape": shape,
        "spacing": spacing,
        "basic_footer": 24,
    }
    return geo_filename, geo_data, Type.BASIC


def _get_basename(path: Path) -> Path:
    """Extract the basename from a binary filename.

    A specific check for the '.mcr' extension is added due to historical naming
    conventions related to the association of binary files and their geometry files.
    """
    if not path.name:
        raise ValueError("Filename is empty")

    if path.suffix.lower() == ".mcr":
        split = path.stem.rsplit("_", 1)
        if len(split) == 2:
            return path.parent / split[0]

    return path.with_suffix("")


def _validate_data_type(data: np.ndarray) -> bool:
    """Validate the data type."""
    if not isinstance(data, np.ndarray):
        return False

    return any(data.dtype == dtype.value for dtype in Type)


def _validate_header_footer(data: np.ndarray) -> bool:
    """Validate the header and footer sizes."""

    def _are_valid_sizes(header: int, footer: int, model: list) -> bool:
        size = np.dtype(model).itemsize - (2 * np.int32(0).itemsize)
        return header == size and footer == size

    if not _are_valid_sizes(data["basic_header"], data["basic_footer"], BASIC_MODEL):
        return False

    if data.dtype == Type.EXTENDED.value and not _are_valid_sizes(
        data["extension_header"], data["extension_footer"], EXTENSION_MODEL
    ):
        return False

    return True


def _ndarray_to_dict(data: np.ndarray) -> dict:
    if not isinstance(data, np.ndarray) or data.size != 1:
        raise ValueError("Input is not a valid structured ndarray")

    record = data[0]

    def extract_value(value):
        if isinstance(value, np.ndarray):
            return value.tolist()
        return value

    return {field: extract_value(record[field]) for field in data.dtype.names}


def _dict_to_ndarray(data_dict: dict, type: Type) -> np.ndarray:
    if set(data_dict.keys()) != set(type.value.names):
        raise ValueError("Input dictionary does not match data type")

    structured_array = np.zeros(1, dtype=type.value)
    for key, value in data_dict.items():
        structured_array[key] = value

    return structured_array
