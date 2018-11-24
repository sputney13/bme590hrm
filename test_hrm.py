import pytest
import csv
import warnings
import json
import hrm


def test_main():
    with pytest.raises(TypeError):
        hrm.main()

    outfile1 = hrm.main("test_data1.csv")
    outfile2 = hrm.main("test_data1.csv", 0, 45)
    assert outfile1 is not None
    assert outfile2 is not None


def test_verify_csv_file():
    with pytest.raises(FileNotFoundError):
        hrm.verify_csv_file('test_data.csv')

    save_file1 = hrm.verify_csv_file('test_data1.csv')
    assert save_file1 == 'test_data1'


def test_store_csv_data():
    global time1
    global time21
    global voltage21
    global time32
    global voltage1
    global voltage32
    time1, voltage1 = hrm.store_csv_data('test_data1.csv')
    time21, voltage21 = hrm.store_csv_data('test_data21.csv')
    time28, voltage28 = hrm.store_csv_data('test_data28.csv')
    time32, voltage32 = hrm.store_csv_data('test_data32.csv')

    assert (time1[0], voltage1[0]) == (0, -0.145)
    assert (time21[6000], voltage21[6000]) == (8.333, -0.1875)
    assert (time28[325], voltage28[325]) == (0.903, -0.285)
    assert (time32[8669], voltage32[8669]) == (12.04, 550.0)


def test_voltage_range_error():
    voltage = [1, 2, 3, 5]
    voltage2 = [-1, 2, -3, 0.5]

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        new_voltage1 = hrm.voltage_range_error(voltage)

    new_voltage2 = hrm.voltage_range_error(voltage2)

    assert len(w) == 1
    assert "Voltage outside normal ECG range. Scaling data."\
           in str(w[-1].message)
    assert max(new_voltage1) <= 4
    assert new_voltage2 == voltage2


@pytest.mark.parametrize("a,expected", [
    ([0, 1, 3, 5], (0, 5)),
    ([-3, 4, 5, -7], (-7, 5)),
    ([-7.2, -7.3, 1.2, 1.3], (-7.3, 1.3))
])
def test_find_voltage_extrema(a, expected):
    assert hrm.find_voltage_extrema(a) == expected


@pytest.mark.parametrize("a,expected", [
    ([0, 1, 3, 5], 5),
    ([.03, .010, 1], .97),
    ([2, 3.5, 4.6, 7.8], 5.8)
])
def test_find_duration(a, expected):
    assert hrm.find_duration(a) == expected


def test_set_perfect_beat():
    global perfect_voltage
    perfect_time, perfect_voltage = hrm.set_perfect_beat()

    assert perfect_time[100] == time21[100]
    assert perfect_voltage[100] == voltage21[100]


def test_correlate_perfect_beat():
    global correlate_voltage1
    global correlate_voltage32
    new_voltage32 = hrm.voltage_range_error(voltage32)
    correlate_voltage1 = hrm.correlate_perfect_beat(voltage1,
                                                    perfect_voltage)
    correlate_voltage32 = hrm.correlate_perfect_beat(new_voltage32,
                                                     perfect_voltage)

    assert correlate_voltage1.all() > -6
    assert correlate_voltage32.all() > -30


def test_detect_beats():
    num_beats1, beats1 = hrm.detect_beats(time1, correlate_voltage1)
    num_beats32, beats32 = hrm.detect_beats(time32, correlate_voltage32)

    assert num_beats1 == 34
    assert len(beats1) == 34
    assert beats1[0] < 0.5
    assert num_beats32 == 19
    assert len(beats32) == 19
    assert beats32[0] < 0.5


def test_user_truncated_time():
    global trunc_time1
    global trunc_voltage1
    global trunc_time32
    global trunc_voltage32
    trunc_time1, trunc_voltage1 = hrm.user_truncated_time(
        0, 5, time1, correlate_voltage1)
    trunc_time32, trunc_voltage32 = hrm.user_truncated_time(
        12, 60, time32, correlate_voltage32)

    assert trunc_time1[0] >= 0
    assert trunc_time1[-1] <= 5
    assert trunc_time32[0] >= 12
    assert trunc_time32[-1] <= 60
    assert len(trunc_voltage1) == len(trunc_time1)
    assert len(trunc_voltage32) == len(trunc_time32)


def test_user_truncated_beats():
    trunc_num_beats1 = \
        hrm.user_truncated_beats(trunc_time1, trunc_voltage1)
    trunc_num_beats32 = \
        hrm.user_truncated_beats(trunc_time32, trunc_voltage32)

    assert trunc_num_beats1 == 7
    assert trunc_num_beats32 == 3


@pytest.mark.parametrize("a,b,expected", [
    ([0, 1, 3, 5], 5, 60),
    ([0, .010, 1.0], 2, 120),
    ([2, 3.5, 4.6, 12.0], 30, 180)
])
def test_calculate_mean_bpm(a, b, expected):
    assert hrm.calculate_mean_bpm(a, b) == expected


def test_generate_metrics_dict():
    metrics1 = hrm.generate_metrics_dict(77, (-1, 2), 33.2,
                                         4, [1, 7.8, 10, 23.4])

    assert metrics1["mean_hr_bpm"] == 77
    assert metrics1["voltage_extremes"] == (-1, 2)
    assert metrics1["duration"] == 33.2
    assert metrics1["num_beats"] == 4
    assert len(metrics1["beats"]) == 4
    assert metrics1["beats"][0] == 1


def test_write_json_file():
    json_file = open("test_data1.json")
    new_metrics = json.loads(json_file.read())

    assert new_metrics["mean_hr_bpm"] < 73.5
    assert new_metrics["voltage_extremes"] == [-0.68, 1.05]
    assert new_metrics["duration"] == 27.775
    assert new_metrics["num_beats"] == 34
    assert len(new_metrics["beats"]) == 34
    assert new_metrics["beats"][0] == 0.281
