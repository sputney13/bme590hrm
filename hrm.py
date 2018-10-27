import csv
import os.path
import matplotlib.pyplot as plt
import numpy as np
import json


def main(filename, min_time=0, max_time=60):
    """ Main function for heart rate monitor: takes .csv data containing
        time and voltage, outputs JSON data about the heart rate data

    Args:
        filename: string containing name of .csv file with hr data
        min_time: min time to calculate mean hr from (default is 0 s)
        max_time: max time to calculate mean hr from (default is 60 s)

    Returns:
        outfile: JSON file containing hr metrics dictionary

    """
    save_file = verify_csv_file(filename)
    time, voltage = store_csv_data(filename)
    voltage_extremes = find_voltage_extrema(voltage)
    duration = find_duration(time)
    perfect_time, perfect_voltage = set_perfect_beat()
    correlate_voltage = correlate_perfect_beat(voltage, perfect_voltage)
    num_beats, beats = detect_beats(time, correlate_voltage)
    trunc_num_beats, trunc_beats, trunc_time = \
        user_truncated_time(min_time, max_time, time, correlate_voltage)
    mean_hr_bpm = calculate_mean_bpm(trunc_time, trunc_num_beats)
    metrics = generate_metrics_dict(mean_hr_bpm, voltage_extremes,
                                    duration, num_beats, beats)
    outfile = write_json_file(save_file, metrics)
    plt.plot(time, voltage)
    plt.plot(time, correlate_voltage)
    plt.show()
    return outfile


def verify_csv_file(filename):
    """ Validates that user inputted file exists on drive

    Args:
        filename: string containing .csv file name

    Returns:
        save_file: existing inputted file, stripped of .csv

    """
    check = os.path.isfile(filename)
    if check is False:
        raise FileNotFoundError("File must exist on machine.")
    else:
        save_file = filename.strip('.csv')
    return save_file


def store_csv_data(filename):
    """ Reads in and stores float data from a valid .csv type file

    Args:
        filename: string containing .csv file name

    Returns:
        time: list containing ECG time data from file in s
        voltage: list containing ECG voltage data from file in mV

    """
    time = []
    voltage = []
    while True:
        with open(filename, newline='') as csvfile:
            try:
                csvreader = csv.reader(csvfile, delimiter=',',
                                       quoting=csv.QUOTE_NONNUMERIC)
                for row in csvreader:
                    if isinstance(row[0], float) and\
                            isinstance(row[1], float) is True:
                        time.append(row[0])
                        voltage.append(row[1])
                    else:
                        continue
                break
            except csv.Error:
                filename = input("Input a valid .csv file as a string:")
                store_csv_data(filename)
    return time, voltage


def find_voltage_extrema(voltage):
    """ Determines minimum and maximum values of list, saves into tuple

    Args:
        voltage: list of voltage values saved from csv data

    Returns:
        voltage_extremes: tuple containing min and max voltage values

    """
    maxvoltage = max(voltage)
    minvoltage = min(voltage)
    voltage_extremes = (minvoltage, maxvoltage)
    return voltage_extremes


def find_duration(time):
    """ Subtracts beginning time from end time to find time duration

    Args:
        time: list of time values saved from csv data

    Returns:
        duration: time duration of the ECG strip

    """
    duration = time[-1] - time[1]
    return duration


def set_perfect_beat():
    """ Cuts test_data21.csv to give one "perfect" beat for correlation

    Returns:
        perfect_time: array of time values for "perfect" beat
        perfect_voltage: array of voltage values for "perfect" beat

    """
    time, voltage = store_csv_data("test_data21.csv")
    perfect_time = np.asarray(time[0:119])
    perfect_voltage = np.asarray(voltage[0:119])
    return perfect_time, perfect_voltage


def correlate_perfect_beat(voltage, perfect_voltage):
    """ Cross-correlates voltage data with "perfect" beat

    Args:
        voltage: list of voltage values saved from .csv data
        perfect_voltage: array of voltage values for "perfect" beat

    Returns:
        correlate_voltage: correlation of voltage array

    """
    voltage = np.asarray(voltage)
    correlate_voltage = np.correlate(voltage, perfect_voltage, 'same')
    return correlate_voltage


def detect_beats(time, correlate_voltage):
    """ Uses a threshold of |4.75| mV on the correlation to detect beats

    Args:
        correlate_voltage: correlation of voltage array and "perfect" beat

    Returns:
         num_beats: number of beats detected over all time
         beats: times at which a beat occurred

    """
    n = 0
    num_beats = 0
    beats = []
    while n < len(correlate_voltage):
        if abs(correlate_voltage[n]) > 4.75:
            num_beats += 1
            beats.append(time[n])
            n += 100
        else:
            n += 1
    beats = np.asarray(beats)
    return num_beats, beats


def user_truncated_time(min_time, max_time, time, correlate_voltage):
    """ Detects beats and beat times for a user specified time interval
        If no specifications, time interval defaults to the first minute

    Args:
        min_time: minimum time for the time interval (s)
        max_time: maximum time for the time interval (s)
        time: list of ECG time data from .csv file
        correlate_voltage: correlation of voltage data and "perfect" beat

    Returns:
         trunc_num_beats: number of beats in user specified interval
         trunc_beats: times at which beats in interval occur

    """
    trunc_time = []
    trunc_voltage = []
    for index in range(len(time)):
        if min_time < time[index] < max_time:
            trunc_time.append(time[index])
            trunc_voltage.append(correlate_voltage[index])
    trunc_num_beats, trunc_beats = detect_beats(trunc_time, trunc_voltage)
    return trunc_num_beats, trunc_beats, trunc_time


def calculate_mean_bpm(trunc_time, trunc_num_beats):
    """ Calculate mean hr bpm for user specified time interval

    Args:
        trunc_time: time truncated by the user/default max and min times
        trunc_num_beats: number of beats in the time interval

    Returns:
         mean_hr_bpm: average heart rate in bpm for the time interval
    """
    trunc_duration = find_duration(trunc_time)
    mean_hr_bpm = 60*(trunc_num_beats/trunc_duration)
    return mean_hr_bpm


def generate_metrics_dict(mean_hr_bpm, voltage_extremes,
                          duration, num_beats, beats):
    """ Creates metrics dictionary containing required values

    Args:
        mean_hr_bpm: average heart rate over user specified interval (bpm)
        voltage_extremes: tuple containing min and max of voltage data
        duration: time duration of time data (s)
        num_beats: number of beats in voltage data
        beats: array of times at which beats occurred

    Returns:
         metrics: dictionary containing keys for the input values

    """
    metrics = {
        "mean_hr_bpm": mean_hr_bpm,
        "voltage_extremes": voltage_extremes,
        "duration": duration,
        "num_beats": num_beats,
        "beats": beats
    }
    return metrics


def write_json_file(save_file, metrics):
    """ Writes values in metrics dictionary into a json file

    Args:
        metrics: dictionary containing assignment-specified hr data

    Returns:

    """
    metrics["beats"] = list(metrics["beats"])
    namefile = save_file + ".json"
    with open(namefile, 'w') as outfile:
        json.dump(metrics, outfile, indent=4)
    return outfile


if __name__ == "__main__":
    main("test_data18.csv")
