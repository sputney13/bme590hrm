import csv
import pytest
import hrm


def test_read_csv_data_reader():
    """ Checks that a proper csv file has been inputted, or gives error

    Args:

    Returns:

    """
    with pytest.raises(FileNotFoundError):
        hrm.read_csv_data('test_data.csv')


def test_read_csv_data_store():
    """ Checks that csv data is stored, and that non-floats are skipped

    Args:

    Returns:

    """
    time1, voltage1 = hrm.read_csv_data('test_data1.csv')
    time2, voltage2 = hrm.read_csv_data('test_data28.csv')
    assert (time1[0], voltage1[0]) == (0, -0.145)
    assert (time2[325], voltage2[325]) == (0.903, -0.285)
