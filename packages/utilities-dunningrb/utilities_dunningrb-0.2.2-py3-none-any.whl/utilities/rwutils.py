"""Define utility methods to read from and write to various filetypes.
"""
from __future__ import annotations

import copy
import csv
import json
import logging
import pickle
import shutil
from collections import defaultdict
from datetime import datetime
from itertools import zip_longest
from pathlib import Path
from xml.etree import ElementTree as eTree

import blosc
import yaml

from utilities import dictutils, listutils, pathutils
from decorators.timing import timing

logger = logging.getLogger(__name__)

READFILE_EXTENSIONS = [".csv", ".dat", ".json", ".yaml", ".yml"]
WRITEFILE_EXTENSION = []


def combine_json_to_csv(
    filepaths: list[Path], *, savetocsv: Path, savetojson: Path
) -> None:
    """Takes in a listutils of filepaths, assumed to be all type <<JSON>>, and combines them in a
    single JSON file and a single CSV file stored at SAVETO.
    """
    logger.info(f"Starting work in combine_json_to_csv.")

    suffixes = list(set([f.suffix.lower() for f in filepaths]))

    if not all([confirm_filetype(f, "json") for f in filepaths]):
        err_msg = f"All filepath must be of type JSON. Received: {suffixes}."
        raise ValueError(err_msg)

    if not confirm_filetype(savetocsv, "csv"):
        err_msg = (
            f"Parameter savetocsv must have extension <csv>. Received: {savetocsv}."
        )
        raise ValueError(err_msg)

    if not confirm_filetype(savetojson, "json"):
        err_msg = (
            f"Parameter savetojson must have extension <json>. Received: {savetojson}."
        )
        raise ValueError(err_msg)

    savetoparent = filepaths[0].parent

    if not savetoparent.is_dir():
        err_msg = f"Directory {savetoparent} does not exist."
        raise ValueError(err_msg)

    data = {}
    for f in filepaths:
        if f.is_file():
            filedata = readfile(f)
            if filedata:
                data.update(filedata)
            else:
                logger.warning(f"File {f} has no data. Was this expected?")
        else:
            logger.warning(f"File {f} does not exist. Skipping it.")
            continue

    writefile(savetocsv, data=data)
    writefile(savetojson, data=data)


def confirm_filetype(filepath: Path, extensions: str | list) -> bool:
    """Return boolean True if the given filepath has an extension in the list of given
    extensions. Note that the given extensions must input the period (.) in the string:

        Good: extensions = [".yml", ".yaml"]
        Bad: extensions = ["yml", "yaml"]
    """
    suffix = filepath.suffix
    return any(suffix.lower() == ext.lower() for ext in extensions)


def create_backup_file(filepath: Path) -> None:
    """Create a backup of the given file, appending a datestamp to the filename."""
    if not filepath.exists():
        logger.warning(f"{filepath} does not exist. Nothing to do.")
        return

    today = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    fileparent = filepath.parent
    filestem = filepath.stem
    filesuffix = filepath.suffix
    newfilename = f"{today}-{filestem}{filesuffix}"
    newfilepath = f"{fileparent}/{newfilename}"

    logger.info(f"{filepath} copied to {newfilepath}.")

    try:
        shutil.copy2(filepath, newfilepath)
    except FileNotFoundError as e:
        err_msg = f"Error copying file. Source: {filepath} or Destination: {newfilepath} not found."
        raise FileNotFoundError(err_msg) from e


def __handle_csv(
    filepath: Path,
    *,
    as_lists: bool,
    as_rows: bool,
    columns: list[int] | None,
    data: dict | list,
    exclude_keys: list,
    max_rows: int,
    mode: str,
    with_header: bool,
) -> None:
    """Receives Path filepath and booleans as_lists and as_rows, and calls the appropriate method
    to write a CSV file.
    """
    if as_lists and as_rows:
        err_msg = (
            f"At least one of parameters <as_lists>, <as_rows> must be False. "
            f"Received: as_lists {as_lists}; as_rows: {as_rows}."
        )
        raise ValueError(err_msg)

    if as_lists:
        write_csvfile_lists(filepath, data=data, exclude_keys=exclude_keys, mode=mode)
    elif as_rows:
        write_csvfile_rows(
            filepath, columns=columns, data=data, mode=mode, with_header=with_header
        )
    else:
        write_csvfile(filepath, data=data, max_rows=max_rows, mode=mode)


def read_csvfile(filepath: Path, delimiter: str = ",") -> list[list]:
    """Takes in a filepath and loads the data in the CSV file into a listutils of lists, one outer
    listutils for each row of the file. Each inner listutils contains the individual data elements
    for a particular row.
    """
    with open(filepath, "r", newline="\n") as f:
        lines = f.readlines()

    return [line.strip().split(delimiter) for line in lines]


def read_datfile(filepath: Path) -> dict:
    """Takes in filepath and loads the data in the DAT file into a dictionary. It is assumed the
    DAT file is blosc-compressed pickle of a Python dictionary object.
    """
    with open(filepath, "rb") as f:
        try:
            data = pickle.loads(blosc.decompress(f.read()))
        except EOFError as e:  # no other blosc exception?
            warn_msg = f"Could not load cached data from {filepath}: {e.__str__()}."
            logger.warning(warn_msg)
            data = {}

    return data


def readfile(filepath: Path) -> list | dict | None:
    """Takes in a stringutils or Path instance, calls the appropriate read method based on the
    filename extension, and returns the content of the file.
    """
    if not filepath.is_file():
        logger.warning(f"{filepath} does not exist. Nothing to do.")
        return

    if filepath.suffix in READFILE_EXTENSIONS:
        return {
            ".csv": read_csvfile,
            ".dat": read_datfile,
            ".json": read_jsonfile,
            ".yaml": read_yamlfile,
            ".yml": read_yamlfile,
        }[filepath.suffix](filepath)
    else:
        err_msg = (
            f"Filepath must have one of the following extensions: "
            f"{listutils.get_string(READFILE_EXTENSIONS)}. Received: {filepath}."
        )
        raise ValueError(err_msg)


def read_jsonfile(filepath: Path) -> list | dict:
    """Takes in a stringutils or Path instance and loads the data in the file (type JSON) into
    either a listutils or dictionary.
    """
    with open(filepath, "r") as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError as e:
            err_msg = f"Could not read JSON file {filepath}."
            raise json.decoder.JSONDecodeError(err_msg, str(filepath), 0) from e
    return data


def read_yamlfile(filepath: Path) -> list | dict:
    """Takes in a stringutils or Path instance and loads the data in the file (type YAML) into
    either a listutils or dictionary.
    """
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    return data


def set_mode(filepath: Path) -> str:
    """Set the mode flag based on the incoming filepath. If the file exists, mode is set to
    <<a>>. If it does not exist, mode is set to <<w>>.
    """
    return {True: "a", False: "w"}[filepath.is_file()]


def write_csvfile(
    filepath: Path,
    *,
    data: dict,
    max_rows: int = None,
    exclude_keys: list = None,
    mode: str = "w",
) -> None:
    """Write the given data dictionary to one or more CSV files. Each k-v pair of the data
    dictionary represents one row of data, and v is itself a dictionary for which the keys
    correspond to the column headers. It is assumed that all such dictionaries have the same
    key-set. If each v of the k-v pairs is a list as opposed to a dictionary,
    use write_csvfile_lists instead of this method.

    If max rows is given, write this many rows (including the header) in a CSV file, and create
    as many CSV files as necessary to write the entire data dictionary. A suffix ("-#", starting
    with "-1") is added to each filename based on the given filepath.

    Any key names provided in the optional exclude keys listutils will be ignored.
    """
    if not data:
        return

    def _write_csvdata(
        data: dict, filepath: Path, mode: str, exclude_keys: list[str] = None
    ):
        exclude_keys = [] if exclude_keys is None else exclude_keys

        with open(filepath, mode, newline="") as f:
            # Get the column names from the first row of the data map--- we assume all rows have the
            # same keys--- but only if mode == "w". If writing in append mode, assume that we
            # already have the header row.

            column_names = [k for k in list(data.values())[0] if k not in exclude_keys]
            writer = csv.DictWriter(f, column_names)

            if mode == "w":
                writer.writeheader()

            for row_key, row_data in data.items():
                row = {}
                for col_name in column_names:
                    try:
                        row[col_name] = row_data[col_name]
                    except KeyError:
                        warn_msg = f"Column name missing from row data: {col_name}."
                        logger.warning(warn_msg)
                        row[col_name] = "missing"
                writer.writerow(row)

    if max_rows is not None:
        if not isinstance(max_rows, int) or max_rows < 2:
            err_msg = f"Parameter <max_rows> must be a positive integer >= 2. Received {max_rows}."
            raise ValueError(err_msg)

    data = dictutils.get_pure_dict(data)
    exclude_keys = [] if exclude_keys is None else exclude_keys
    working_filepath = Path(copy.deepcopy(filepath))

    if max_rows:
        filecounter = 1
        for subdata in dictutils.divide_dict_into_smaller_dicts(
            data=data, size=max_rows
        ):
            _write_csvdata(subdata, working_filepath, mode)
            filecounter += 1
            working_filepath = pathutils.add_suffix_to_path(
                path=filepath, suffix=str(filecounter)
            )
    else:
        _write_csvdata(data, working_filepath, mode, exclude_keys)


def write_csvfile_lists(
    filepath: Path, *, data: dict | defaultdict, mode: str = "w", exclude_keys=None,
) -> None:
    """Write the given data dictionary to a CSV file. Each k-v pair of the data dictionary
    represents one column of data, and v is a list of the values in a column. If each v in the kv
    pairs is a dictionary as opposed to a list, use write_csvfile instead of this method.

    Any key names provided in the optional exclude keys list will be ignored.
    """
    data = dictutils.get_pure_dict(data)

    if exclude_keys is None:
        exclude_keys = []

    column_names = [k for k in list(data.keys()) if k not in exclude_keys]
    column_lists = [v for k, v in data.items() if k not in exclude_keys]

    rows = zip_longest(*column_lists, fillvalue="")

    with open(filepath, mode, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        for row in rows:
            writer.writerow(row)


def write_csvfile_rows(
    filepath: Path,
    *,
    columns: list[int] | None = None,
    data: list[list],
    mode: str = "w",
    with_header: bool = False,
) -> None:
    """Write the given data dictionary to a CSV file. Data is a list of lists, with each list
    comprising one row of data. If optional with_header is True, column headers are read from
    the first list in the data. If optional col_indexes is given, only the columns corresponding
    to the given indexes will be written with all others ignored.
    """
    if with_header:
        column_names = [i for i in data.pop(0)]
    else:
        column_names = []

    if columns:
        rows = [[i[j] for j in columns] for i in data]
    else:
        rows = [i for i in data]

    with open(filepath, mode, newline="") as f:
        writer = csv.writer(f)
        if column_names:
            writer.writerow(column_names)
        for row in rows:
            writer.writerow(row)


def write_datfile(filepath: Path, *, data: dict) -> None:
    """Takes in a filepath and a data dictionary, blosc-compresses a pickle of the data,
    and writes the compressed pickle to disk as a DAT file.
    """
    if filepath.is_file():
        current = readfile(filepath)
        data.update(current)

    with open(filepath, "wb") as f:
        f.write(blosc.compress(pickle.dumps(data)))


@timing
def writefile(
    filepath: Path,
    *,
    as_lists: bool = False,
    as_rows: bool = False,
    columns: list[int] | None = None,
    data: dict | list,
    exclude_keys: list = None,
    max_rows: int = None,
    mode: str = "w",
    root: eTree.Element = None,
    with_header: bool = False,
) -> None:
    """Takes in a stringutils or Path instance filepath, a data dictionary or list, and one or
    more optional parameters, and calls the appropriate write method based on the filepath
    extension.

    NOTES:

        (1) If the filepath extension is ".csv":

            (a) If parameter <<as_lists>> is False, parameter <<exclude_keys>> is ignored.
            (b) If parameter <<as_rows>> is False, parameter <<col_indexes>> is ignored.

        (2) If the filepath extension is NOT ".csv", parameters <<as_lists>>, <<as_rows>>,
            <<exclude_keys>>, and <<col_indexes>> are ignored.
        (3) If the filepath extension is ".dat", parameter <<data>> must be of type <<dict>>.
        (4) If the filepath extension is ".dat" OR ".xml", parameter <<mode>> is ignored.
        (5) If the filepath extension is ".xml", parameter <<root>> is required.
        (6) If the filepath extension is NOT ".xml", parameter <<root>> is ignored.
    """
    suffix = filepath.suffix

    if suffix == ".csv":
        __handle_csv(
            filepath,
            data=data,
            as_lists=as_lists,
            as_rows=as_rows,
            exclude_keys=exclude_keys,
            mode=mode,
            with_header=with_header,
            max_rows=max_rows,
            columns=columns,
        )
    elif filepath.suffix == ".dat":
        write_datfile(filepath, data=data)
    elif filepath.suffix == ".json":
        write_jsonfile(filepath, data=data, mode=mode)
    elif filepath.suffix in [".yaml", "yml"]:
        write_yamlfile(filepath, data=data, mode=mode)
    elif filepath.suffix == ".xml":
        write_xmlfile(filepath, root=root)
    else:
        warn_msg = (
            f"Unrecognized file extension: {filepath.suffix}. Data WAS NOT WRITTEN to "
            f"disk. Filepath: {str(filepath)}."
        )
        logger.warning(warn_msg)
        return

    logger.info(f"Data written to file: {filepath}.")


def write_jsonfile(filepath: Path, *, data: dict | list, mode: str = "w") -> None:
    """Takes in a data dictionary or listutils, a stringutils or Path instance and writes the data
    dictionary or listutils to the specified pathutils in JSON format. If appending, the incoming
    data must be of the same type as that extracted from the given filepath. If it is not,
    this method raises ValueError.
    """
    if mode == "a":
        try:
            existing_data = read_jsonfile(filepath)
        except FileNotFoundError:
            logger.warning(f"Filepath {filepath} not found.")
            pass
        else:
            if type(data) != type(existing_data):
                err_msg = (
                    f"Cannot merge data objects of different types. Received {type(data)} "
                    f"with append mode, but existing data is of type {type(existing_data)}."
                )
                raise ValueError(err_msg)
            if isinstance(existing_data, list):
                data += existing_data
            elif isinstance(existing_data, dict):
                data = {**existing_data, **data}

    with open(filepath, "w") as f:
        json.dump(data, f)


def write_xmlfile(filepath: Path, *, root: eTree.Element) -> None:
    """Takes in a stringutils or Path instance filepath and an eTree.Element object, which should
    be the root of an eTree.ElementTree object, and coerces it and its children into
    nicely-formatted XML and writes the data to file. Relies on an internally-defined recursive
    method.

    See: https://stackoverflow.com/a/65808327
    """

    def _format_xml(
        element: eTree.Element,
        parent: eTree.Element = None,
        index: int = -1,
        depth: int = 0,
    ) -> None:
        """Format the incoming element and, recursively, its children into nicely-formatted
        XML."""
        for i, node in enumerate(element):
            _format_xml(node, element, i, depth + 1)  # Recursive call.

        if parent is not None:
            if index == 0:
                parent.text = "\n" + ("\t" * depth)
            else:
                parent[index - 1].tail = "\n" + ("\t" * depth)

            if index == len(parent) - 1:
                element.tail = "\n" + ("\t" * (depth - 1))

    _format_xml(root)
    tree = eTree.ElementTree(root)
    tree.write(filepath)


def write_yamlfile(filepath: Path, *, data: dict | list, mode: str = "w") -> None:
    """Takes in a data dictionary or listutils, a stringutils or Path instance, and an optional
    boolean flag and writes the data dictionary or listutils to the specified pathutils in YAML
    format. If appending, the incoming data must be of the same type as that extracted from the
    given filepath. If it is not, this method raises ValueError.
    """
    if mode == "a":
        try:
            existing_data = read_yamlfile(filepath)
        except FileNotFoundError:
            logger.warning(f"File not found: {filepath}.")
            pass
        else:
            if type(data) != type(existing_data):
                err_msg = (
                    f"Cannot merge data objects of different types. Received {type(data)} "
                    f"with append mode, but existing data is of type {type(existing_data)}."
                )
                raise ValueError(err_msg)

            if isinstance(existing_data, list):
                data += existing_data
            elif isinstance(existing_data, dict):
                data = {**existing_data, **data}

    with open(filepath, "w") as f:
        yaml.dump(data, f)
