"""This module provides methods to read and write binary files."""

from dataclasses import dataclass
from typing import Callable, IO, List, Tuple, Generator

import gzip
import os
import warnings
import zlib

import numpy as np
import matplotlib.pyplot as mpl
from matplotlib.pyplot import Axes
from matplotlib.ticker import MaxNLocator

from micpy import geo
from micpy import utils

__all__ = ["File"]


@dataclass
class Chunk:
    """A chunk of uncompressed binary data."""

    DEFAULT_SIZE = 8388608

    data: bytes
    decompressobj: zlib.decompressobj = None

    @staticmethod
    def iterate(
        file: IO[bytes],
        chunk_size: int,
        compressed: bool = True,
        offset: int = 0,
        decompressobj: zlib.decompressobj = None,
    ) -> Generator["Chunk", None, None]:
        """Yield chunks of uncompressed binary data."""
        file.seek(offset)

        if decompressobj:
            decompressobj = decompressobj.copy()
        else:
            decompressobj = (
                zlib.decompressobj(zlib.MAX_WBITS | 32) if compressed else None
            )

        while True:
            data = file.read(chunk_size)
            if data == b"":
                break

            if compressed:
                prev_decompressobj = decompressobj
                decompressobj = prev_decompressobj.copy()
                data = decompressobj.decompress(data)

            yield Chunk(data, prev_decompressobj if compressed else None)


class Footer:
    """A field footer."""

    TYPE = [("length", np.int32)]
    SIZE = np.dtype(TYPE).itemsize

    def __init__(self, length: int = 0):
        data = np.array((length,), dtype=self.TYPE)
        self.body_length = data["length"]

    def to_bytes(self):
        """Convert the footer to bytes."""
        return np.array((self.body_length,), dtype=self.TYPE).tobytes()


class Header:
    """A field header."""

    TYPE = [("size", np.int32), ("time", np.float32), ("length", np.int32)]
    SIZE = np.dtype(TYPE).itemsize

    def __init__(self, size: int, time: float, length: int):
        self.size = size
        self.time = round(float(time), 7)
        self.body_length = length

        self.field_size = Header.SIZE + 4 * self.body_length + Footer.SIZE

        if not self.size == self.field_size - 8:
            raise ValueError("Invalid header")

    @staticmethod
    def from_bytes(data: bytes):
        """Create a new header from bytes."""
        kwargs = np.frombuffer(data[: Header.SIZE], dtype=Header.TYPE)
        return Header(*kwargs[0].item())

    def to_bytes(self):
        """Convert the header to bytes."""
        return np.array(
            (self.size, self.time, self.body_length), dtype=Header.TYPE
        ).tobytes()

    @staticmethod
    def read(filename: str, compressed: bool = True) -> "Header":
        """Read the header of a binary file."""
        file_open = gzip.open if compressed else open

        with file_open(filename, "rb") as file:
            file.seek(0)
            data = file.read(Header.SIZE)
            return Header.from_bytes(data)


@dataclass
class Position:
    """A field position in a binary file."""

    id: int
    time: float
    chunk_id: int
    chunk_offset: int
    decompressobj: zlib.decompressobj
    chunk_size: int
    field_size: int
    file: IO[bytes]

    @staticmethod
    def iterate_params(
        file: IO[bytes], position: int, compressed: bool, chunk_size: int
    ):
        if position:
            return (
                position.file,
                position.decompressobj is not None,
                position.chunk_size,
                position.field_size,
                position.id,
                position.chunk_id[0],
                position.chunk_offset[0],
                position.decompressobj.copy() if position.decompressobj else None,
                position.chunk_id[0] * position.chunk_size,
            )

        header = Header.read(file.name, compressed)
        return (file, compressed, chunk_size, header.field_size, 0, 0, 0, None, 0)

    @staticmethod
    def iterate(
        file: IO[bytes] = None,
        compressed: bool = True,
        chunk_size: int = Chunk.DEFAULT_SIZE,
        position: "Position" = None,
    ) -> Generator["Position", None, None]:
        """Yield positions of fields in a binary file."""

        (
            file,
            compressed,
            chunk_size,
            field_size,
            field_id,
            chunk_id,
            chunk_offset,
            decompressobj,
            offset,
        ) = Position.iterate_params(file, position, compressed, chunk_size)

        field_buffer = b""
        prev_chunk_id = chunk_id
        prev_chunk_offset = chunk_offset

        for chunk in Chunk.iterate(
            file,
            chunk_size=chunk_size,
            compressed=compressed,
            offset=offset,
            decompressobj=decompressobj,
        ):
            chunk_buffer = chunk.data

            if chunk_offset:
                chunk_buffer = chunk_buffer[chunk_offset:]

            while chunk_buffer:
                if len(field_buffer) == 0:
                    decompressobj = chunk.decompressobj
                    prev_chunk_id = chunk_id
                    prev_chunk_offset = chunk_offset

                required_size = field_size - len(field_buffer)
                required_buff = chunk_buffer[:required_size]
                field_buffer += required_buff
                chunk_buffer = chunk_buffer[required_size:]
                chunk_offset += len(required_buff)

                if len(field_buffer) == field_size:
                    yield Position(
                        id=field_id,
                        time=Header.from_bytes(field_buffer).time,
                        chunk_id=(prev_chunk_id, chunk_id),
                        chunk_offset=(prev_chunk_offset, chunk_offset),
                        chunk_size=chunk_size,
                        field_size=field_size,
                        decompressobj=decompressobj,
                        file=file,
                    )
                    field_id += 1
                    field_buffer = b""

            chunk_id += 1
            chunk_offset = 0


class Index(List[Position]):
    """An index of fields in a binary file."""

    @staticmethod
    def from_file(
        file: IO[bytes],
        show_progress: bool = True,
        chunk_size: int = Chunk.DEFAULT_SIZE,
        compressed: bool = True,
    ):
        """Build an index from a binary file."""
        iterator = Position.iterate(file, chunk_size=chunk_size, compressed=compressed)

        if show_progress:
            iterator = utils.progress_indicator(
                iterator, description="Indexing", unit="Field"
            )

        return Index(iterator)

    @staticmethod
    def from_filename(
        filename: str,
        show_progress: bool = True,
        chunk_size: int = Chunk.DEFAULT_SIZE,
        compressed: bool = True,
    ):
        """Build an index from a binary file."""
        file = open(filename, "rb")
        return Index.from_file(file, show_progress, chunk_size, compressed)


class Field(np.ndarray):
    """A field."""

    def __new__(cls, data, time: float, spacing: float = None):
        obj = np.asarray(data).view(cls)
        obj.time = round(float(time), 7)
        obj.spacing = spacing
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return

        # pylint: disable=attribute-defined-outside-init
        self.time = getattr(obj, "time", None)
        self.spacing = getattr(obj, "spacing", None)

    @staticmethod
    def from_bytes(data: bytes, shape=None, spacing=None):
        """Create a new time step from bytes."""

        header = Header.from_bytes(data)

        start, end, count = (
            header.SIZE,
            header.field_size,
            header.body_length,
        )

        data = data[start:end]
        data = np.frombuffer(data, count=count, dtype="float32")
        if np.all(np.isclose(data, data.astype("int32"))):
            data = data.astype("int32")

        if shape is not None:
            data = data.reshape(shape)

        return Field(data, time=header.time, spacing=spacing)

    def to_bytes(self):
        """Convert the field to bytes."""
        header = Header(
            size=self.size * self.itemsize + 8,
            time=self.time,
            length=self.size,
        )
        footer = Footer(length=self.size)

        return header.to_bytes() + self.tobytes() + footer.to_bytes()

    @staticmethod
    def dimensions(shape: Tuple[int, int, int]) -> int:
        """Get the number of dimensions of a shape."""
        x, y, _ = shape

        if y == 1:
            if x == 1:
                return 1
            return 2
        return 3

    @staticmethod
    def read(position: Position, shape=None, spacing=None) -> "Field":
        """Read a field from a binary file."""
        file_offset = position.chunk_id[0] * position.chunk_size
        position.file.seek(file_offset)

        decompressobj = (
            position.decompressobj.copy() if position.decompressobj else None
        )

        field_buffer = b""

        while True:
            chunk_data = position.file.read(position.chunk_size)

            if not chunk_data:
                break

            data = decompressobj.decompress(chunk_data) if decompressobj else chunk_data

            if field_buffer == b"":
                field_buffer = data[position.chunk_offset[0] :]
            else:
                field_buffer += data

            if len(field_buffer) >= position.field_size:
                break

        field_data = field_buffer[: position.field_size]

        return Field.from_bytes(field_data, shape=shape, spacing=spacing)

    def write(self, file: IO[bytes]):
        """Write the field to a binary file."""
        file.write(self.to_bytes())

    def get_slice(self, plane: str, slice_id: int):
        """Get a slice of the field."""

        if plane not in ["xy", "xz", "yz", "zy", "zx", "yx"]:
            raise ValueError("Invalid plane")

        dimensions = Field.dimensions(self.shape)

        x, _, z = self.shape

        reshape_operations = {
            1: lambda data: data.reshape((z, 1)),
            2: lambda data: data.reshape((z, x)),
            3: lambda data: data,
        }

        data = reshape_operations[dimensions](self)

        slice_operations = {
            1: {
                "xz": lambda data: data,
                "zx": lambda data: data.T,
                "xy": lambda data: data[slice_id : slice_id + 1],
                "yx": lambda data: data[slice_id : slice_id + 1],
                "zy": lambda data: data.T,
                "yz": lambda data: data,
            },
            2: {
                "xz": lambda data: data,
                "zx": lambda data: data.T,
                "xy": lambda data: data[slice_id : slice_id + 1],
                "yx": lambda data: data[slice_id : slice_id + 1].T,
                "zy": lambda data: data.T[slice_id : slice_id + 1],
                "yz": lambda data: data.T[slice_id : slice_id + 1].T,
            },
            3: {
                "xy": lambda data: data[slice_id, :, :],
                "yx": lambda data: data[slice_id, :, :].T,
                "xz": lambda data: data[:, slice_id, :],
                "zx": lambda data: data[:, slice_id, :].T,
                "yz": lambda data: data[:, :, slice_id],
                "zy": lambda data: data[:, :, slice_id].T,
            },
        }

        return slice_operations[dimensions][plane](data)

    # pylint: disable=too-many-arguments
    def plot(
        self,
        plane: str = "xz",
        slice_id: int = 0,
        title: str = None,
        xlabel: str = None,
        ylabel: str = None,
        figsize: Tuple[float, float] = None,
        dpi: int = None,
        aspect: str = "equal",
        ax: Axes = None,
        cax: Axes = None,
        vmin: float = None,
        vmax: float = None,
        cmap: str = "micpy",
    ):
        """Plot a slice of the field.

        Args:
            plane (str, optional): Plane of the slice. Defaults to "xz".
            slice_id (int, optional): Slice ID. Defaults to 0.
            title (str, optional): Title of the plot. Defaults to None.
            xlabel (str, optional): Label of the x-axis. Defaults to None (auto).
            ylabel (str, optional): Label of the y-axis. Defaults to None (auto).
            figsize (Tuple[float, float], optional): Figure size. Defaults to None (auto).
            dpi (int, optional): Figure DPI. Defaults to None (auto).
            aspect (str, optional): Aspect ratio. Defaults to "equal".
            ax (Axes, optional): Axes to plot on. Defaults to None.
            cax (Axes, optional): Axes to plot color bar on. Defaults to None.
            vmin (float, optional): Minimum value of the color bar. Defaults to None.
            vmax (float, optional): Maximum value of the color bar. Defaults to None.
            cmap (str, optional): Color map. Defaults to "micpy".

        Returns:
            Tuple[Figure, Axes]: Figure and axes of the plot.
        """
        slice = self.get_slice(plane, slice_id)

        fig, ax = (
            mpl.subplots(figsize=figsize, dpi=dpi)
            if ax is None
            else (ax.get_figure(), ax)
        )

        if title is not None:
            ax.set_title(title)
        else:
            ax.set_title(f"t={np.round(self.time, 7)}s")
        if xlabel is not None:
            ax.set_xlabel(xlabel)
        else:
            ax.set_xlabel(plane[0])
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        else:
            ax.set_ylabel(plane[1])
        if aspect is not None:
            ax.set_aspect(aspect)
        ax.set_frame_on(False)

        mesh = ax.pcolormesh(slice, cmap=cmap, vmin=vmin, vmax=vmax)

        bar = mpl.colorbar(mesh, ax=ax, cax=cax)
        bar.locator = MaxNLocator(integer=np.issubdtype(slice.dtype, np.integer))
        bar.outline.set_visible(False)
        bar.update_ticks()

        return fig, ax


class FieldList(List[Field]):
    """A list of fields."""

    def __init__(self, fields: List[Field] = None):
        super().__init__(fields if fields else [])

    def append(self, field: Field):
        """Append a field to the list."""
        super().append(field)

    def extend(self, fields: List[Field]):
        """Extend the list with fields."""
        super().extend(fields)

    def write(self, filename: str, compressed: bool = True, write_geo: bool = True):
        """Write the fields to a binary file."""
        file_open = gzip.open if compressed else open
        with file_open(filename, "wb") as file:
            for field in self:
                field.write(file)

        if write_geo:
            geo_filename, geo_data, geo_type = geo.get_basic(
                filename, self[0].shape, self[0].spacing
            )
            geo.write(geo_filename, geo_data, geo_type, compressed=compressed)

    # pylint: disable=too-many-arguments
    def plot(
        self,
        cols: int = None,
        normalize: bool = False,
        sharex: bool = False,
        sharey: bool = False,
        figsize: Tuple[float, float] = None,
        dpi: int = None,
        **kwargs,
    ):
        """Plot the fields in a grid.

        Args:
            cols (int, optional): Number of columns. Defaults to None (auto).
            normalize (bool, optional): Normalize the color bar. Defaults to False.
            sharex (bool, optional): Share x-axis. Defaults to False.
            sharey (bool, optional): Share y-axis. Defaults to False.
            figsize (Tuple[float, float], optional): Figure size. Defaults to None (auto).
            dpi (int, optional): Figure DPI. Defaults to None (auto).
            **kwargs: Keyword arguments passed to Field.plot().

        Returns:
            Tuple[Figure, Axes]: Figure and axes of the plot.
        """

        if cols is None:
            cols = int(np.sqrt(len(self)))

        rows = (len(self) + cols - 1) // cols

        fig, ax = mpl.subplots(
            rows, cols, figsize=figsize, dpi=dpi, sharex=sharex, sharey=sharey
        )

        vmin = (
            min(field.min() for field in self)
            if normalize
            else kwargs.pop("vmin", None)
        )
        vmax = (
            max(field.max() for field in self)
            if normalize
            else kwargs.pop("vmax", None)
        )

        flat_ax = ax.flatten()

        for i, field in enumerate(self):
            field.plot(ax=flat_ax[i], vmin=vmin, vmax=vmax, **kwargs)

        for i in range(len(self), len(ax)):
            fig.delaxes(flat_ax[i])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig.tight_layout()

        return fig, ax


class File:
    """A binary file."""

    def __init__(self, filename: str):
        """Initialize a binary file.

        Args:
            filename (str): File name.

        Raises:
            FileNotFoundError: If file is not found.
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"File not found: {filename}")

        self._filename = filename

        self._file: IO[bytes] = None
        self._index: Index = None
        self._chunk_size: int = None
        self._compressed: bool = None

        self.shape: np.ndarray[(3,), np.int32] = None
        self.spacing: np.ndarray[(3,), np.float32] = None

        try:
            self.find_geo()
        except (geo.GeometryFileNotFoundError, geo.MultipleGeometryFilesError):
            print(
                "Caution: A geometry file was not found. "
                "To read a geometry from a designated location, use the read_geo() method. "
                "Alternatively, you can manually set the geometry by executing set_geo()."
            )

    def __getitem__(self, key: int or slice or list or Callable[[Field], bool]):
        return self.read(key)

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __iter__(self):
        return self.iterate()

    def open(self, force: bool = False):
        """Open the file.

        Args:
            force (bool, optional): Force open the file. Defaults to False.
            show_progress (bool, optional): Show progress bar. Defaults to True.
        """
        if force or not self._file:
            self._file = open(self._filename, "rb")

        return self

    def close(self):
        """Close the file."""
        self._file.close()
        self._file = None
        self._index = None

    def index(
        self,
        show_progress: bool = True,
        chunk_size: int = Chunk.DEFAULT_SIZE,
        compressed: bool = None,
        force: bool = False,
    ) -> Index:
        """Build an index of the file.

        Args:
            show_progress (bool, optional): Show progress bar. Defaults to True.
            chunk_size (int, optional): Chunk size in bytes. Defaults to 8388608 (8 MiB).
            compressed (bool, optional): True if file is compressed, False otherwise.
                Defaults to None (auto).
            force (bool, optional): Force rebuild of the index. Defaults to False.

        Returns:
            Index: Index of the file.
        """
        self._compressed = (
            utils.is_compressed(self._filename) if compressed is None else compressed
        )

        self.open()
        if force or not self._index or chunk_size != self._chunk_size:
            self._index = Index.from_file(
                self._file,
                show_progress=show_progress,
                chunk_size=chunk_size,
                compressed=self._compressed,
            )
            self._chunk_size = chunk_size

        return self._index

    def times(self) -> List[float]:
        """Get the times of the fields in the file.

        Returns:
            List[float]: List of times.
        """
        return [position.time for position in self.index()]

    def set_geo(self, shape: Tuple[int, int, int], spacing: Tuple[float, float, float]):
        """Set the geometry.

        Args:
            shape (Tuple[int, int, int]): Shape of the geometry.
            spacing (Tuple[float, float, float]): Spacing of the geometry.
        """

        self.shape = np.array(shape)
        self.spacing = np.array(spacing)

        self.print_geo()

    def read_geo(
        self, filename: str, type: geo.Type = geo.Type.EXTENDED, compressed: bool = True
    ):
        """Read geometry from a file.

        Args:
            filename (str): Filename of a geometry file.
            type (Type, optional): Data type to be read. Defaults to Type.EXTENDED.
            compressed (bool, optional): True if file is compressed, False otherwise.
                Defaults to True.
        """
        geo_dict = geo.read(filename, type=type, compressed=compressed)
        self.set_geo(geo_dict["shape"], geo_dict["spacing"])

    def find_geo(self, type: geo.Type = geo.Type.EXTENDED, compressed: bool = None):
        """Find geometry file and read it.

        Args:
            type (Type, optional): Data type to be read. Defaults to Type.EXTENDED.
            compressed (bool, optional): True if file is compressed, False otherwise.
                Defaults to None (auto).

        Raises:
            GeometryFileNotFoundError: If no geometry file is found.
            MultipleGeometryFilesError: If multiple geometry files are found.
        """
        filename = geo.find(self._filename)

        if compressed is None:
            compressed = utils.is_compressed(filename)

        self.read_geo(filename, type=type, compressed=compressed)

    def print_geo(self):
        """Get a string representation of the geometry."""

        if self.shape is None or self.spacing is None:
            print("Geometry: None")
            return

        dimensions = Field.dimensions(self.shape)
        cells = self.shape
        spacing = np.round(self.spacing, 7)
        size = cells * spacing

        print(
            f"Geometry: {dimensions}-Dimensional Grid\n"
            f"Grid Size: {tuple(size)}μm³\n"
            f"Grid Shape (Cell Count): {tuple(cells)}\n"
            f"Grid Spacing (Cell Size): {tuple(spacing)}μm³"
        )

    def iterate(self, show_progress: bool = True):
        """Iterate over fields in the file.

        Args:
            show_progress (bool, optional): Show progress bar. Defaults to True.

        Returns:
            Field: Field data.
        """
        self.index(show_progress=show_progress)

        for position in self._index:
            yield Field.read(position, shape=self.shape, spacing=self.spacing)

    def read(
        self,
        key: int or slice or list or Callable[[Field], bool] = None,
        show_progress: bool = True,
    ):
        """Read a field from the file.

        Args:
            key (int or list or slice or Callable[[Field], bool], optional): Field ID,
                list of field IDs, a slice object, or a condition function.
                Defaults to None.
            show_progress (bool, optional): Show progress bar. Defaults to True.

        Returns:
            Field: Field data.
        """

        def read_field(self, field_id: int or slice or list):
            position = self._index[field_id]
            return Field.read(position, shape=self.shape, spacing=self.spacing)

        self.index(show_progress=show_progress)

        if key is None:
            return FieldList(self.iterate())
        if isinstance(key, int):
            return read_field(self, key)
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            key = list(range(len(self._index))[start:stop:step])
        if isinstance(key, list):
            return FieldList([read_field(self, i) for i in key])
        if isinstance(key, Callable):
            return FieldList([field for field in self.iterate() if key(field)])

        raise TypeError("Invalid argument type")


try:
    utils.register_colormaps()
except ValueError:
    pass
