import pytest
import csv
import warnings
import json
import hrm


def test_main():
    with pytest.raises(TypeError):
        hrm.main()

    outfile1 = hrm.main("test_data1.csv")
    outfile2 = hrm.main("test_data1.csv", 0, 5)
    assert outfile1 is not None
    assert outfile2 is not None


def test_verify_csv_file():
    with pytest.raises(FileNotFoundError):
        hrm.verify_csv_file('test_data.csv')

    save_file1 = hrm.verify_csv_file('test_data1.csv')
    assert save_file1 == 'test_data1'


def test_store_csv_data():
    global voltage1
    global time1
    global voltage21
    global time21
    global voltage28
    global time28
    global voltage32
    global time32
    time1, voltage1 = hrm.store_csv_data('test_data1.csv')
    time21, voltage21 = hrm.store_csv_data('test_data21.csv')
    time28, voltage28 = hrm.store_csv_data('test_data28.csv')
    time32, voltage32 = hrm.store_csv_data('test_data32.csv')

    assert (time1[0], voltage1[0]) == (0, -0.145)
    assert (time21[6000], voltage21[6000]) == (8.333, -0.1875)
    assert (time28[325], voltage28[325]) == (0.903, -0.285)
    assert (time32[8669], voltage32[8669]) == (12.04, 550.0)


def test_voltage_range_error():
    global new_voltage32
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        new_voltage32 = hrm.voltage_range_error(voltage32)

    new_voltage1 = hrm.voltage_range_error(voltage1)

    assert len(w) == 1
    assert "Voltage outside normal ECG range. Scaling data."\
           in str(w[-1].message)
    assert max(new_voltage32) <= 4
    assert new_voltage1 == voltage1


def test_find_voltage_extrema():
    global voltage_extremes1
    global voltage_extremes32
    voltage_extremes1 = hrm.find_voltage_extrema(voltage1)
    voltage_extremes32 = hrm.find_voltage_extrema(new_voltage32)
    scale_volt_min = -375 / 151.5625

    assert voltage_extremes1 == (-0.68, 1.05)
    assert voltage_extremes32 == (scale_volt_min, 4.0)


def test_find_duration():
    global duration1
    global duration32
    duration1 = hrm.find_duration(time1)
    duration32 = hrm.find_duration(time32)

    assert duration1 == 27.772
    assert duration32 < 13.887


def test_set_perfect_beat():
    global perfect_voltage
    perfect_time, perfect_voltage = hrm.set_perfect_beat()

    assert perfect_time[100] == time21[100]
    assert perfect_voltage[100] == voltage21[100]


def test_correlate_perfect_beat():
    global correlate_voltage1
    global correlate_voltage32
    correlate_voltage1 = hrm.correlate_perfect_beat(voltage1,
                                                    perfect_voltage)
    correlate_voltage32 = hrm.correlate_perfect_beat(new_voltage32,
                                                     perfect_voltage)

    assert correlate_voltage1.all() > -6
    assert correlate_voltage32.all() > -30


def test_detect_beats():
    global num_beats1
    global beats1
    global num_beats32
    global beats32
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
    global trunc_num_beats1
    global trunc_num_beats32

    trunc_num_beats1 = \
        hrm.user_truncated_beats(trunc_time1, trunc_voltage1)
    trunc_num_beats32 = \
        hrm.user_truncated_beats(trunc_time32, trunc_voltage32)

    assert trunc_num_beats1 == 7
    assert trunc_num_beats32 == 3


def test_calculate_mean_bpm():
    global mean_hr_bpm1
    global mean_hr_bpm32
    mean_hr_bpm1 = hrm.calculate_mean_bpm(trunc_time1, trunc_num_beats1)
    mean_hr_bpm32 = hrm.calculate_mean_bpm(trunc_time32, trunc_num_beats32)

    assert mean_hr_bpm1 < 85
    assert mean_hr_bpm32 < 96


def test_generate_metrics_dict():
    global metrics1
    metrics1 = hrm.generate_metrics_dict(mean_hr_bpm1, voltage_extremes1,
                                         duration1, num_beats1, beats1)

    assert metrics1["mean_hr_bpm"] < 85
    assert metrics1["voltage_extremes"] == (-0.68, 1.05)
    assert metrics1["duration"] == 27.772
    assert metrics1["num_beats"] == 34
    assert len(metrics1["beats"]) == 34
    assert metrics1["beats"][0] < 0.5


def test_write_json_file():
    json_file = open("test_data1.json")
    new_metrics = json.loads(json_file.read())
    assert new_metrics["mean_hr_bpm"] == metrics1["mean_hr_bpm"]
    assert new_metrics["voltage_extremes"] == \
        list(metrics1["voltage_extremes"])
    assert new_metrics["duration"] == metrics1["duration"]
    assert new_metrics["num_beats"] == metrics1["num_beats"]
    assert new_metrics["beats"] == list(metrics1["beats"])
