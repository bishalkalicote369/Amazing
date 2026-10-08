from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class ConfigModel:
    """
    Configuration for maze generation
    """
    HEIGHT: int
    WIDTH: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool = True
    SEED: Optional[int | None] = None


def _parse_key_values(file_path: str) -> dict[str, str]:
    """
    Parse the configuration file in key and value pairs

    Lines starts with # are comment and blank lines
    should be skip and each line must have key and value sep by '='

    Args:
        file_path: path to configuration file

    Returns:
        dictonary of key and value all string

    Raises:
        FileNotFoundError: if  there is no any config file
        ConfigError: if line has invalid syntax and duplicate keys
        PersmissionError: if permission is denied to open file

    """
    raw_config: dict[str, str] = {}

    with open(file_path, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, 1):
            stripped: str = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            if "=" not in stripped:
                raise ConfigError(
                    f"Syntax error in config file in line {line_num}"
                )

            if stripped.count("=") != 1:
                raise ConfigError(
                    f"Syntax error in config file in line {line_num}"
                )

            key, value = stripped.split("=", 1)
            if not key or not value:
                raise ConfigError(
                    f"Syntax error in config {key} in line {line_num}"
                )
            if key in raw_config:
                raise ConfigError(
                     f"Found duplictes of {key} config file in line {line_num}"
                )
            raw_config[key] = value
    return raw_config


def _required_keys(raw_config: dict[str, str]) -> None:
    """
    Ensure that all required configuration is present

    Args:
        raw_config: dictonary or key and value from configuration file

    Raises:
        ConfigError if required key is missing
    """

    required_keys: set[str] = {
        "WIDTH", "HEIGHT",
        "ENTRY", "EXIT",
        "OUTPUT_FILE", "PERFECT"
    }
    missing_key = required_keys - raw_config.keys()
    if missing_key:
        raise ConfigError("[Error]: Missing the required keys")


def _parse_positive_int(key: str, value: str) -> int:
    """
    Parse the positive int from str

    Args:
        key: key from required keys
        value: the string value which needed to be type caste to int

    Raises:
        ConfigError if value is negative and failed in type cast
    """

    try:
        parsed_value = int(value.strip())
    except ValueError as error:
        raise ConfigError(
            f"{key} must be a valid integer string."
        ) from error

    if parsed_value <= 0:
        raise ConfigError(f"{key} must be positive")

    return parsed_value


def _parse_coordinates(key: str, value: str) -> tuple[int, int]:
    """
    parse the cordinate in x,y format

    Args:
        key: key from required keys
        value: raw cordinate string

    Return;
        return the tuple of coordinate

    Raises:
        ConfigError: if value is not valid in cordinate
    """

    if "," not in value:
        raise ConfigError(
            f"Syntax error in cordinates for {key} must be seperated by ','"
            )
    if value.count(",") != 1:
        raise ConfigError(
            f"Syntax error in coordinates {key}. expected only one comma"
        )
    x_str, y_str = value.split(",")
    x_str, y_str = x_str.strip(), y_str.strip()

    if not x_str or not y_str:
        raise ConfigError(
           f"Syntax error in coordinates {key}: empty cordinate value."
        )

    try:
        x, y = int(x_str), int(y_str)
        if x < 0 or y < 0:
            raise ValueError("Coordinates must be positive")
        return x, y
    except ValueError as error:
        raise ConfigError(
            f"Syntax error in coordinate for '{key}': "
            f"coordinates must be valid integers. {error}"
        )


def _parse_bool(key: str, value: str) -> bool:
    """
    Parse the boolean configuration value

    Args:
        key: key from congih
        value: raw boolean value

    Return:
        Returns the parsed bool value

    Raises:
        ConfigError: if non supporting bool is provided
    """

    normal_value = value.strip()

    if normal_value == "True":
        return True
    elif normal_value == "False":
        return False
    raise ConfigError(
        f"Invalid configuration for {key}"
    )


def _parse_opt(key: str | None, value: str | None) -> int | None:
    """
    Parse an optional int configuration value

    Args:
        key: the optional key
        value: str value or none if value is not provided

    Return:
        int value or None id value is not provided

    Raises:
        ConfigError if value is negative and failed in type cast
    """
    if value is None or not value.strip():
        return None

    try:
        parsed_value = int(value.strip())
    except ValueError as error:
        raise ConfigError(
            f"{key} must be a valid integer string."
        ) from error

    if parsed_value <= 0:
        raise ConfigError(f"{key} must be positive")

    return parsed_value


def _parse_file_name(key: str, value: str) -> str:
    """
    Ensure that file is ready to be written

    Args:
        key: output file key
        value: normally file name to write the output

    Return:
        the valid file name ends with .txt

    Raises:
        ConfigError  if extension does not match .txt
    """
    if not value.strip():
        raise ConfigError("File name needed to write the output of the maze")

    if not value.strip().endswith(".txt"):
        raise ConfigError(
            f"{key} doesn't have extension "
            "to write in the file, eg: <filename>.txt"
            )
    return value


def _in_bounds(height: int, width: int, coordinates: tuple[int, int]) -> bool:
    row, col = coordinates
    return 0 <= row < height and 0 <= col < width


def load_config(file_path: str) -> ConfigModel:
    """
    Load, parse, and validate the configuration file for the maze

    Args:
        file_path: path to configuration file

    Returns:
        an instance of the confifmodel

    Raises:
        FileNotFoundError: if  there is no any config file
        ConfigError: if there is some problem durung parsing
        PersmissionError: if permission is denied to open file

    """

    raw_config: dict[str, str] = _parse_key_values(file_path)
    _required_keys(raw_config)
    height = _parse_positive_int("HEIGHT", raw_config["HEIGHT"])
    width = _parse_positive_int("WIDTH", raw_config["WIDTH"])
    entry = _parse_coordinates("ENTRY", raw_config["ENTRY"])
    exit = _parse_coordinates("EXIT", raw_config["EXIT"])
    output_file = _parse_file_name("OUTPUT_FILE", raw_config["OUTPUT_FILE"])
    perfect = _parse_bool("PERFECT", raw_config["PERFECT"])
    seed = _parse_opt("SEED", raw_config.get("SEED"))

    if not _in_bounds(height, width, entry):
        raise ConfigError("Entry should be in maze bounds")
    if not _in_bounds(height, width, exit):
        raise ConfigError("Exit should be in maze bounds")
    if entry == exit:
        raise ConfigError("Entry and Exit should be different")
    return ConfigModel(
        WIDTH=width,
        HEIGHT=height,
        ENTRY=entry,
        EXIT=exit,
        OUTPUT_FILE=output_file,
        PERFECT=perfect,
        SEED=seed
    )
