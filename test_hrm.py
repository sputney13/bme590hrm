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
    global voltage1
    global time1
    time1, voltage1 = hrm.store_csv_data('test_data1.csv')
    time2, voltage2 = hrm.store_csv_data('test_data28.csv')
    assert (time1[0], voltage1[0]) == (0, -0.145)
    assert (time2[325], voltage2[325]) == (0.903, -0.285)


def test_find_voltage_extrema():
    """ Verifies that max/min voltage values are stored

    Args:

    Returns:

    """
    voltage_extremes = hrm.find_voltage_extrema(voltage1)
    assert voltage_extremes == (-0.68, 1.05)


def test_find_duration():
    """ Verifies that the proper time duration of the strip is calculated

    Args:

    Returns:

    """
    duration = hrm.find_duration(time1)
    assert duration == 27.772


def test_set_perfect_beat():
    """ Verifies the perfect beat is cut from the data properly

    Args:

    Returns:

    """
    global perfect_voltage
    perfect_time, perfect_voltage = hrm.set_perfect_beat()
    time, voltage = hrm.store_csv_data("test_data21.csv")
    assert perfect_time[100] == time[100]
    assert perfect_voltage[100] == voltage[100]


def test_correlate_perfect_beat():
    """ Verifies the voltage was properly correlated with the data

    Args:

    Returns:

    """
    global correlate_voltage
    correlate_voltage = hrm.correlate_perfect_beat(voltage1,
                                                   perfect_voltage)
    assert correlate_voltage.all() > -6


def test_detect_beats():
    """ Verifies beat detector stores proper beat number and beat times

    Args:

    Returns:

    """
    num_beats, beat_times = hrm.detect_beats(time1, correlate_voltage)
    assert num_beats == 35
    assert len(beat_times) == 35
    assert beat_times[0] < 0.5
