import csv
import os.path
import matplotlib.pyplot as plt
import numpy as np


def verify_csv_file(filename):
    """ Validates that user inputted file exists on drive

    Args:
        filename: string containing .csv file name

    Returns:
        savefile: existing inputted file, stripped of .csv

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
         beat_times: times at which a beat occurred

    """
    n = 0
    num_beats = 0
    beat_times = []
    while n < len(correlate_voltage):
        if abs(correlate_voltage[n]) > 4.75:
            num_beats += 1
            beat_times.append(time[n])
            n = n + 100
        else:
            n = n + 1
    return num_beats, beat_times


if __name__ == "__main__":
    time, voltage = store_csv_data("test_data1.csv")
    perfect_time, perfect_voltage = set_perfect_beat()
    correlate_voltage = correlate_perfect_beat(voltage, perfect_voltage)
    num_beats, beat_times = detect_beats(time, correlate_voltage)
    print(num_beats)
    print(beat_times)
    plt.plot(time, voltage)
    plt.plot(time, correlate_voltage)
    plt.show()
