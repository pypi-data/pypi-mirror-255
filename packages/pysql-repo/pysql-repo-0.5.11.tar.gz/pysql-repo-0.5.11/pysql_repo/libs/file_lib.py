# MODULES
import json
from pathlib import Path
from typing import Any, Dict, List, Union


from typing import List, Dict, Union
from pathlib import Path
import json


def open_json_file(path: Path, encoding: str = "utf-8") -> Union[List[Dict], Dict]:
    """
    Opens a JSON file and returns its contents as a Python object.

    Args:
        path (Path): The path to the JSON file.
        encoding (str, optional): The encoding of the file. Defaults to "utf-8".

    Returns:
        Union[List[Dict], Dict]: The contents of the JSON file as a Python object.

    Raises:
        FileNotFoundError: If the specified path does not exist.
        FileExistsError: If the specified path is not a file.
    """
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist")

    if not path.is_file():
        raise FileExistsError(f"Path {path} is not a file")

    with open(path, encoding=encoding) as json_file:
        raw_data = json.load(json_file)

    return raw_data


def open_file(path: Path, encoding: str = "utf-8") -> bytes:
    """
    Opens a file at the given path and returns its content as bytes.

    Args:
        path (Path): The path to the file.
        encoding (str, optional): The encoding to use when reading the file. Defaults to "utf-8".

    Returns:
        bytes: The content of the file as bytes.

    Raises:
        FileNotFoundError: If the file does not exist at the given path.
        FileExistsError: If the path exists but is not a file.
    """
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist")

    if not path.is_file():
        raise FileExistsError(f"Path {path} is not a file")

    with open(path, encoding=encoding) as file:
        raw_data = file.read()
        raw_data = raw_data.encode(encoding)

    return raw_data


def save_json_file(
    path: Path,
    data: Any,
    encoding: str = "utf-8",
):
    """
    Save data as a JSON file at the specified path.

    Args:
        path (Path): The path where the JSON file will be saved.
        data (Any): The data to be saved as JSON.
        encoding (str, optional): The encoding to be used when writing the file. Defaults to "utf-8".
    """
    if path.exists():
        return

    with open(path, "w", encoding=encoding) as file:
        file.write(json.dumps(data))


def save_file(
    path: Path,
    data: bytes,
    encoding: str = "utf-8",
    new_line: str = "\n",
):
    """
    Save the given data to a file at the specified path.

    Args:
        path (Path): The path where the file should be saved.
        data (bytes): The data to be saved.
        encoding (str, optional): The encoding to be used when writing the file. Defaults to "utf-8".
        new_line (str, optional): The newline character to be used when writing the file. Defaults to "\n".
    """
    if path.exists():
        return

    text_data = data.decode(encoding)

    with open(path, "w", encoding=encoding, newline=new_line) as file:
        file.write(text_data)
