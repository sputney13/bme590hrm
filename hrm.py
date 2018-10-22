import csv
import os.path


def read_csv_data(filename):
    """ Reads in data from a valid, existing .csv type file

    Args:
        filename: string containing .csv file name

    Returns:
        csvreader: .csv data in float format

    """
    global save_file
    save_file = filename.strip('.csv')
    check = os.path.isfile(filename)
    if check is False:
        raise FileNotFoundError("File must exist on machine.")
    while True:
        with open(filename, newline='') as csvfile:
            try:
                csvreader = csv.reader(csvfile, delimiter=',',
                                       quoting=csv.QUOTE_NONNUMERIC)
                break
            except csv.Error:
                filename = input("Input a valid .csv file as a string:")
    return csvreader


def store_csv_data(csvreader):
    """ Stores .csv data into separate time and voltage lists

    Args:
        csvreader: float values of .csv file input

    Returns:
        time: time values from .csv file saved as list
        voltage: voltage values from .csv file saved as list

    """
    time = []
    voltage = []
    for row in csvreader:
        if isinstance(row[0], float) and isinstance(row[1], float) is True:
                time.append(row[0])
                voltage.append(row[1])
        else:
            continue
    return time, voltage
