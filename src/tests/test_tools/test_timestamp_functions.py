from datetime import datetime
from mainbot.tools.timestamp_functions import (
    get_beg_info_element,
    get_base64_from_datetime,
    long_from_base64,
    long_to_base64,
)


def test_get_beg_info_element():
    test_date_1 = datetime(2024, 2, 18)
    test_date_2 = datetime(2023, 8, 30)
    timestamp_1 = round(test_date_1.timestamp())
    timestamp_2 = round(test_date_2.timestamp())
    assert get_beg_info_element(timestamp_1) == 2023
    assert get_beg_info_element(timestamp_2) == 2023


def test_long_from_base64():
    assert long_from_base64("ZAxSpSL") == 1718813889675


def test_long_to_base64():
    assert long_to_base64(1718813889675) == "ZAxSpSL"


def test_get_base64_from_datetime():
    test_datetime = datetime(2024, 2, 18)
    assert get_base64_from_datetime(test_datetime) == "Y25TEWA"
