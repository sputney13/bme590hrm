import csv
import os.path


def read_csv_data(filename):
    """ Reads in and stores float data from a valid .csv type file

    Args:
        filename: string containing .csv file name

    Returns:
        time: list containing ECG time data from file in s
        voltage: list containing ECG voltage data from file in mV

    """
    global save_file
    save_file = filename.strip('.csv')
    time = []
    voltage = []

    check = os.path.isfile(filename)
    if check is False:
        raise FileNotFoundError("File must exist on machine.")

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
                read_csv_data(filename)
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


if __name__ == "__main__":
    time, voltage = read_csv_data("test_data1.csv")
    voltage_extremes = find_voltage_extrema(voltage)
    print(voltage_extremes)
