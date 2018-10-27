# bme590hrm [![Build Status](https://travis-ci.org/sputney13/bme590hrm.svg?branch=master)](https://travis-ci.org/sputney13/bme590hrm)
Heart Rate Monitor project for BME590: Medical Device and Software Design.

The completed heart rate monitor accepts inputs of time and voltage data in the .csv format and outputs a JSON file containing the `metrics` dictionary. `metrics` has keys for the mean heart rate in beats per minute over a user-specified or default time interval, the minimum and maximum voltage values in the data, the duration of the time input, the number of detected beats in the voltage data, and the times at which those detected beats occurred.

To use: import the hrm package, save the test_data21.csv file included in this repository to your code filepath, and call on the main function. Documentation for the main function is included below.

```python
hrm.main(filename, min_time=0, max_time=60)
    """ Main function for heart rate monitor: takes .csv data containing
        time and voltage, outputs JSON data about the heart rate data

    Args:
        filename: string containing name of .csv file with hr data
        min_time: min time to calculate mean hr from (default is 0 s)
        max_time: max time to calculate mean hr from (default is 60 s)

    Returns:
        outfile: JSON file containing hr metrics dictionary
        Pyplot graph of time versus voltage from the .csv input
        Pyplot graph of time versus the correlated voltage values

    """
```

This package utitilizes a beat detector algorithm based on correlation. The `set_perfect_beat` function cuts a "perfect" heart beat from test_data21.csv, and following functions correlate this data with the voltage data from the inputted .csv file then threshold the correlation to determine where beats occur. When a correlated voltage value above the threshold is detected, the number of beats is incremented and the index iterates forward 100 values to prevent repeat detections. 
