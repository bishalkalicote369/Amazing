import pytest
from unittest.mock import mock_open, patch
from io_utils.configs import (
    ConfigModel,
    _parse_key_values,
    _required_keys,
    _parse_positive_int,
    _parse_coordinates,
    _parse_bool,
    _parse_opt,
    load_config,
)

# ==========================================
# 1. Tests for _parse_key_values
# ==========================================

def test_parse_key_values_success():
    valid_data = (
        "WIDTH=10\n"
        "# This is a comment\n"
        "\n"
        "HEIGHT=20\n"
        "OUTPUT_FILE=maze.txt"
    )
    with patch("builtins.open", mock_open(read_data=valid_data)):
        result = _parse_key_values("fake_path.ini")
        assert result == {"WIDTH": "10", "HEIGHT": "20", "OUTPUT_FILE": "maze.txt"}


@pytest.mark.parametrize(
    "invalid_data, match_phrase",
    [
        ("WIDTH", "Syntax error in config file in line 1"),
        ("WIDTH=10=20", "Syntax error in config file in line 1"),
        ("WIDTH=", "Syntax error in config"),
        ("=10", "Syntax error in config"),
        ("WIDTH=10\nWIDTH=20", "Found duplictes of WIDTH config file in line 2"),
    ],
)
def test_parse_key_values_syntax_errors(invalid_data, match_phrase):
    with patch("builtins.open", mock_open(read_data=invalid_data)):
        with pytest.raises(ValueError, match=match_phrase):
            _parse_key_values("fake_path.ini")


def test_parse_key_values_file_not_found():
    with pytest.raises(FileNotFoundError):
        _parse_key_values("non_existent_file.ini")


# ==========================================
# 2. Tests for _required_keys
# ==========================================

def test_required_keys_success():
    valid_keys = {
        "WIDTH": "10", "HEIGHT": "20", "ENTRY": "0,0",
        "EXIT": "9,9", "OUTPUT_FILE": "out.txt", "PERFECT": "True"
    }
    # Should not raise any error
    _required_keys(valid_keys)


def test_required_keys_missing():
    invalid_keys = {"WIDTH": "10", "HEIGHT": "20"}
    with pytest.raises(ValueError, match=r"\[Error\]: Missing the required keys"):
        _required_keys(invalid_keys)


# ==========================================
# 3. Tests for _parse_positive_int
# ==========================================

def test_parse_positive_int_success():
    assert _parse_positive_int("WIDTH", "5") == 5


@pytest.mark.parametrize("invalid_val", ["0", "-5"])
def test_parse_positive_int_invalid(invalid_val):
    with pytest.raises(ValueError, match="WIDTH must be positive"):
        _parse_positive_int("WIDTH", invalid_val)


# ==========================================
# 4. Tests for _parse_coordinates
# ==========================================

def test_parse_coordinates_success():
    assert _parse_coordinates("ENTRY", "1,2") == (1, 2)
    assert _parse_coordinates("ENTRY", " 3 , 4 ") == (3, 4)  # tests trimming spaces


@pytest.mark.parametrize(
    "invalid_coord, match_phrase",
    [
        ("1", "must be seperated by ','"),
        ("1,2,3", "expected only one comma"),
        ("1,", "empty cordinate value"),
        (",2", "empty cordinate value"),
        ("-1,2", "Coordinates must be positive"),
        ("abc,2", "coordinates must be valid integers"),
    ],
)
def test_parse_coordinates_invalid(invalid_coord, match_phrase):
    with pytest.raises(ValueError, match=match_phrase):
        _parse_coordinates("ENTRY", invalid_coord)


# ==========================================
# 5. Tests for _parse_bool
# ==========================================

@pytest.mark.parametrize("val, expected", [("True", True), ("False", False), (" True ", True)])
def test_parse_bool_success(val, expected):
    assert _parse_bool("PERFECT", val) is expected


def test_parse_bool_invalid():
    with pytest.raises(ValueError, match="Invalid configuration for PERFECT"):
        _parse_bool("PERFECT", "Yes")


# ==========================================
# 6. Tests for _parse_opt
# ==========================================

def test_parse_opt_success_and_none():
    assert _parse_opt("SEED", "42") == 42
    assert _parse_opt("SEED", None) is None


def test_parse_opt_invalid():
    with pytest.raises(ValueError, match="Value must be a valid integer string"):
        _parse_opt("SEED", "abc")


# ==========================================
# 7. Integration/End-to-End Test for load_config
# ==========================================

def test_load_config_full_integration(tmp_path):
    # Using tmp_path fixture to generate a real temporary file securely
    config_file = tmp_path / "maze_config.ini"
    config_content = (
        "WIDTH=15\n"
        "HEIGHT=25\n"
        "ENTRY=0,1\n"
        "EXIT=14,24\n"
        "OUTPUT_FILE=maze_output.png\n"
        "PERFECT=False\n"
        "SEED=12345\n"
    )
    config_file.write_text(config_content, encoding="utf-8")

    config = load_config(str(config_file))

    assert isinstance(config, ConfigModel)
    # Be aware: Your ConfigModel signature accepts (HEIGHT, WIDTH, ...),
    # but inside load_config you passed width first: ConfigModel(width, height, ...)
    # Checking against how load_config maps fields:
    assert config.HEIGHT == 15
    assert config.WIDTH == 25
    assert config.ENTRY == (0, 1)
    assert config.EXIT == (14, 24)
    assert config.OUTPUT_FILE == "maze_output.png"
    assert config.PERFECT is False
    assert config.SEED == 12345
