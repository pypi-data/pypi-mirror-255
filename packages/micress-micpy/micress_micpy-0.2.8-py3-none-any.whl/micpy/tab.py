"""This module provides methods to read and parse tabular files."""

import io
import re

import pandas as pd
from pandas import DataFrame

__all__ = ["read", "parse", "FormatError"]


class FormatError(Exception):
    """Raised when there's a problem with the format of the tabular file."""


def parse(
    string: str, parse_header: bool = True, ignore_invalid_header: bool = True
) -> DataFrame:
    """Parse a tabular file and return the content as a pandas DataFrame.

    Args:
        string (str): The content of a tabular file as a string.
        parse_header (bool, optional): Whether to parse the header. Defaults to True.
        ignore_invalid_header (bool, optional): Whether to ignore invalid headers.
            Defaults to True.

    Raises:
        FormatError: If the number of columns in the header does not match the body.

    Returns:
        DataFrame: The content of the file as a pandas DataFrame.
    """
    lines = string.splitlines()
    return _parse_lines(lines, parse_header, ignore_invalid_header)


def read(
    filename: str, parse_header: bool = True, ignore_invalid_header: bool = True
) -> DataFrame:
    """Read a tabular file and return the content as a pandas DataFrame.

    Args:
        filename (str): Path to the file.
        parse_header (bool, optional): Whether to parse the header. Defaults to True.
        ignore_invalid_header (bool, optional): Whether to ignore invalid headers.
            Defaults to True.

    Raises:
        FormatError: If the number of columns in the header does not match the body.

    Returns:
        DataFrame: The content of the file as a pandas DataFrame.
    """
    with open(filename, mode="r", encoding="utf8") as file:
        lines = file.readlines()
    return _parse_lines(lines, parse_header, ignore_invalid_header)


def _parse_lines(
    lines: list[str], parse_header: bool = True, ignore_invalid_header: bool = True
) -> DataFrame:
    if parse_header:
        header, body = _separate_header_and_body(lines)
        df = _read_body(body)

        if header:
            if len(header) == len(df.columns):
                df.columns = header
            elif not ignore_invalid_header:
                raise FormatError(
                    "Number of columns in header does not match the body."
                )
    else:
        df = _read_body(lines)

    return df


def _separate_header_and_body(lines: list[str]) -> tuple[list[str], list[str]]:
    header_lines = []
    body_start_index = 0
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith("##"):
            continue
        if line.startswith("#"):
            header_lines.append(line)
        else:
            body_start_index = i
            break

    header = _process_header(header_lines)
    body = lines[body_start_index:]
    return header, body


def _read_body(lines: list[str]) -> DataFrame:
    content = "\n".join(lines)
    return pd.read_csv(
        io.StringIO(content),
        comment="#",
        delimiter=r"\s+",
        header=None,
        skip_blank_lines=True,
    )


def _process_header(header_lines: list[str]) -> list[str]:
    stripped_header = [line[1:].strip() for line in header_lines]
    rows = [re.split(r"\s{2,}", line) for line in stripped_header if line]
    columns = list(zip(*rows))
    return [" ".join(filter(lambda x: x != "-", column)).strip() for column in columns]
