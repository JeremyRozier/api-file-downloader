"""Module which contains functions which parse filenames"""

from mimetypes import guess_extension, guess_type
import unicodedata
import os
import re
import sys
from urllib.parse import urlparse
import aiofiles
from aiohttp import ClientResponse
from mainbot.constants import RegexPatterns
from .timestamp_functions import get_beg_info_element


def get_valid_filename(filename) -> str:
    """
    Returns the given string converted to a string that can be used for a clean
    filename. Removes leading and trailing spaces; converts other spaces to
    underscores; and removes anything that is not an alphanumeric, dash,
    underscore, or dot.

    Args:
        - filename (str): The name we want to save a file under.

    Returns (str) : The given string converted to a string that can be used for a clean
    filename. Removes leading and trailing spaces; converts other spaces to
    underscores; and removes anything that is not an alphanumeric, dash,
    underscore, or dot.
    """
    while "." in filename:
        tuple_before_after = os.path.splitext(filename)
        if guess_type(tuple_before_after[1]) is not None:
            filename = tuple_before_after[0]
        else:
            filename = filename.replace(".", "")

    valid_filename = str(filename).strip().replace(" ", "_")
    valid_filename = RegexPatterns.FILENAME_FORBIDDEN_CHARS.sub(
        "", valid_filename
    )
    valid_filename = unicodedata.normalize("NFKD", valid_filename)
    valid_filename = "".join(
        [c for c in valid_filename if not unicodedata.combining(c)]
    )
    return valid_filename


def get_nb_origin_same_filename(folder_path: str, filename: str) -> int:
    """
    Returns for a given filename the number of files
    already saved in the folder path which match with this pattern
    rf{filename}(_d+)?, or 0 if there aren't any conflicts.

    Args:
        - folder_path (str): The path where the file will be saved.
        - filename (str): The filename the file is meant to be saved under.

    Returns (int): The number of files already saved in folder_path
    which match with this pattern rf{filename}(_d+)?,
    or 0 if there aren't any conflicts
    """
    list_files = [
        os.path.splitext(f)[0]
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]
    list_same_file = [f for f in list_files if f == filename]
    if len(list_same_file) == 0:
        return 0

    pattern = rf"{filename}(_\d+)?"
    list_similar = [f for f in list_files if re.match(pattern, f)]
    return len(list_similar)


def get_filename_nb(folder_path: str, filename: str):
    filename_nb = filename
    if os.path.exists(folder_path):
        nb_same_filename = get_nb_origin_same_filename(folder_path, filename)
        if nb_same_filename > 0:
            filename_nb = f"{filename}_{nb_same_filename}"
    return filename_nb


def get_file_extension(
    file_url: str, file_content_type: str, object_module: str
) -> str:
    """Gets the extension of the file with its informations.

    Args:
        - file_url (str): The url pointing directly to the location where
        the file is stored.
        - file_content_type (str): The content type associated to the file
        got in the response of a get request.
        - object_module (str): The module name of the file we want to save.

    Returns (str): The extension of the file. If the extension could not be found,
    returns the empty string.
    Example : ".txt".
    """
    if object_module == "folder":
        extension = ".zip"
    elif object_module == "quiz":
        extension = ""
    else:
        extension = guess_extension(file_content_type)
        if extension is None or extension == ".html":
            parsed = urlparse(file_url)
            extension = os.path.splitext(parsed.path)[1].lower()
            if len(extension) == 0:
                extension = ""

    return extension


def turn_cwd_to_execution_dir():
    """Turn the current directory into execution directory.

    Returns: None
    """
    execution_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(execution_dir)


def get_info_element(data_name: str, start_date_timestamp: int) -> str:
    """Get the info element interval associated to the data.

    Args:
        - data_name (str): The name of the data.
        - start_date_timestamp (int): The timestamp value when the data
        has been created.

    Returns (str): The info element interval associated to the data.
    Example: "23-24"
    """
    match_info_element = RegexPatterns.info_element_REGEX.search(data_name)
    if match_info_element is not None:
        return match_info_element.group(0)
    beg_info_element = get_beg_info_element(start_date_timestamp)
    end_info_element = beg_info_element + 1
    return f"{str(beg_info_element)[-2:]}-{str(end_info_element)[-2:]}"


async def write_with_error_handling(
    path_with_filename: str,
    content_to_write: str,
):
    try:
        async with aiofiles.open(path_with_filename, mode="w") as file:
            await file.write(content_to_write)
    except FileNotFoundError:
        nb_chars_above_limit = len(path_with_filename) - 260 + 1
        async with aiofiles.open(
            path_with_filename[:-nb_chars_above_limit], mode="w"
        ) as file:
            await file.write(content_to_write)


async def write_binary_with_error_handling(
    path_with_filename: str, content_to_write: ClientResponse
):
    try:
        async with aiofiles.open(path_with_filename, mode="wb") as file:
            async for chunk in content_to_write.content.iter_chunked(1024):
                await file.write(chunk)
    except FileNotFoundError:
        nb_chars_above_limit = len(path_with_filename) - 260 + 1
        async with aiofiles.open(
            path_with_filename[:-nb_chars_above_limit], mode="wb"
        ) as file:
            async for chunk in content_to_write.content.iter_chunked(1024):
                await file.write(chunk)


def get_object_folder_path(
    info_element: str, data_name: str, other_info_name: str
) -> str:
    """Creates a folder path for the given
    data name and other_info name.

    Args:
        data_name (str): The data name used for making the path.
        other_info_name (str): The other_info name used for making the path.

    Returns (str): The folder path for the given arguments.
    """
    folder_path = os.path.join(
        "Fichiers_Example1",
        get_valid_filename(info_element),
        get_valid_filename(data_name),
        get_valid_filename(other_info_name),
    )
    return folder_path
