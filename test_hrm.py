import csv
import pytest
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

    global save_file
    save_file = hrm.verify_csv_file('test_data1.csv')
    assert save_file == 'test_data1'


def test_store_csv_data():
    global voltage1
    global time1
    time1, voltage1 = hrm.store_csv_data('test_data1.csv')
    time2, voltage2 = hrm.store_csv_data('test_data28.csv')
    assert (time1[0], voltage1[0]) == (0, -0.145)
    assert (time2[325], voltage2[325]) == (0.903, -0.285)


def test_find_voltage_extrema():
    global voltage_extremes
    voltage_extremes = hrm.find_voltage_extrema(voltage1)
    assert voltage_extremes == (-0.68, 1.05)


def test_find_duration():
    global duration
    duration = hrm.find_duration(time1)
    assert duration == 27.772


def test_set_perfect_beat():
    global perfect_voltage
    perfect_time, perfect_voltage = hrm.set_perfect_beat()
    time, voltage = hrm.store_csv_data("test_data21.csv")
    assert perfect_time[100] == time[100]
    assert perfect_voltage[100] == voltage[100]


def test_correlate_perfect_beat():
    global correlate_voltage
    correlate_voltage = hrm.correlate_perfect_beat(voltage1,
                                                   perfect_voltage)
    assert correlate_voltage.all() > -6


def test_detect_beats():
    global num_beats
    global beats
    num_beats, beats = hrm.detect_beats(time1, correlate_voltage)
    assert num_beats == 35
    assert len(beats) == 35
    assert beats[0] < 0.5


def test_user_truncated_time():
    global trunc_num_beats
    global trunc_time
    trunc_num_beats, trunc_beats, trunc_time = hrm.user_truncated_time(
        0, 5, time1, correlate_voltage)
    assert trunc_num_beats == 6
    assert len(trunc_beats) == 6
    assert trunc_beats[5] < 5


def test_calculate_mean_bpm():
    global mean_hr_bpm
    mean_hr_bpm = hrm.calculate_mean_bpm(trunc_time, trunc_num_beats)
    assert mean_hr_bpm < 73


def test_generate_metrics_dict():
    global metrics
    metrics = hrm.generate_metrics_dict(mean_hr_bpm, voltage_extremes,
                                        duration, num_beats, beats)
    assert metrics["mean_hr_bpm"] < 73
    assert metrics["voltage_extremes"] == (-0.68, 1.05)
    assert metrics["duration"] == 27.772
    assert metrics["num_beats"] == 35
    assert len(metrics["beats"]) == 35
    assert metrics["beats"][0] < 0.5


def test_write_json_file():
    json_file = open("test_data1.json")
    new_metrics = json.loads(json_file.read())
    assert new_metrics["mean_hr_bpm"] == metrics["mean_hr_bpm"]
    assert new_metrics["voltage_extremes"] == list(metrics["voltage_extremes"])
    assert new_metrics["duration"] == metrics["duration"]
    assert new_metrics["num_beats"] == metrics["num_beats"]
    assert new_metrics["beats"] == list(metrics["beats"])
