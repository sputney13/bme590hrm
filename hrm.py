import csv
import os.path


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


if __name__ == "__main__":
    time, voltage = store_csv_data("test_data1.csv")
    duration = find_duration(time)
    print(duration)
