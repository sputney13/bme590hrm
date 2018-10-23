import csv
import pytest
import hrm


def test_verify_csv_file():
    """ Checks that a proper csv file has been inputted, or gives error

    Args:

    Returns:

    """
    with pytest.raises(FileNotFoundError):
        hrm.verify_csv_file('test_data.csv')


def test_store_csv_data():
    """ Checks that csv data is stored, and that non-floats are skipped

    Args:

    Returns:

    """
    time1, voltage1 = hrm.store_csv_data('test_data1.csv')
    time2, voltage2 = hrm.store_csv_data('test_data28.csv')
    assert (time1[0], voltage1[0]) == (0, -0.145)
    assert (time2[325], voltage2[325]) == (0.903, -0.285)
