import csv
import pytest
import hrm


def test_read_csv_data():
    """ Checks that a proper, existing .csv file has been inputted

    Args:

    Returns:

    """
    with pytest.raises(FileNotFoundError):
        hrm.read_csv_data('test_data.csv')


def test_store_csv_data():
    """ Checks that only floats are stored to time and voltage

    Args:

    Returns:

    """
    readcsv = ([1.0, 3.0], [2.0, 4.0])
    falsecsv = ([1.0, 'string'], [2.0, 4.0])
    (time1, voltage1) = hrm.store_csv_data(readcsv)
    (time2, voltage2) = hrm.store_csv_data(falsecsv)
    assert (time1, voltage1) == ([1.0, 2.0], [3.0, 4.0])
    assert (time2, voltage2) == ([2.0], [4.0])
