import numpy as np
import pandas as pd
import csv
import warnings

def list_from_csv(filepath):
    input_list = []
    with open(filepath, "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            input_list.append(row)
            
    return input_list

def convert_input_to_float(input_list):
    float_list = []
    for row in input_list:
        try:
            time = float(row[0])
            x = float(row[1])
            y = float(row[2])
            float_list.append([time, x, y])
        except Exception:
            continue
    return float_list

def fix_time(input_list, tolerance=0.5):
    delta = input_list[-1][0] / len(input_list)
    fixed_list = [[0.0, 42, 225]]
    for i in range(1, len(input_list)):
        if ((input_list[i][0] - fixed_list[i-1][0]) < tolerance) and ((input_list[i][0] - fixed_list[i-1][0]) > 0.0):
            fixed_list.append(input_list[i])
        else:
            fixed_list.append([fixed_list[i-1][0] + delta, input_list[i][1], input_list[i][2]])

    return fixed_list

import numpy as np
from scipy.interpolate import CubicSpline
import pandas as pd

def clean_with_spline(data, window=7, threshold=2.0):
    """
    Clean position data by removing outliers using rolling median deviation
    and filling them with cubic spline interpolation.

    Parameters:
        data (array-like): raw 1D position data
        window (int): rolling median window size (odd number recommended)
        threshold (float): multiple of MAD to classify an outlier

    Returns:
        cleaned: numpy array of same length with outliers replaced
        outliers: boolean mask of which elements were replaced
    """

    data = np.asarray(data)
    n = len(data)

    # --- 1. Compute rolling median ---
    roll_med = (
        pd.Series(data)
        .rolling(window=window, center=True, min_periods=1)
        .median()
        .to_numpy()
    )

    # --- 2. Compute absolute deviation from rolling median ---
    deviation = np.abs(data - roll_med)
    mad = np.median(deviation)  # Median Absolute Deviation

    # Avoid divide-by-zero in perfectly flat data
    if mad == 0:
        mad = 1e-9

    # --- 3. Detect outliers ---
    outliers = deviation > threshold * mad

    # --- 4. Cubic spline interpolation to fill outliers ---
    x = np.arange(n)
    good_x = x[~outliers]
    good_y = data[~outliers]

    # If too few points remain, just return original
    if len(good_x) < 4:
        return data.copy(), outliers

    spline = CubicSpline(good_x, good_y)

    cleaned = data.copy()
    cleaned[outliers] = spline(x[outliers])

    return cleaned

def fix_x(input_list, window_size=3):
    for i in range(0, len(input_list)):
        if (input_list[i][1] < 0.0) or (input_list[i][1] > 11000.0):
            input_list[i][1] = input_list[i-1][1]

    for i in range(0, len(input_list) - window_size):
        times = []
        actual_x = []
        for j in range(0, window_size):
            times.append(input_list[i+j][0])
            actual_x.append(input_list[i+j][1])

        slope = float(polyfit(times, actual_x, 1)[0])
        intercept = float(polyfit(times, actual_x, 1)[1])

        predicted_x = []
        for val in times:
            predicted_x.append(slope * val + intercept)

        residuals = []
        for j, actual in enumerate(actual_x):
            residuals.append(abs(actual - predicted_x[j]))

            index = argmax(residuals)
    return 0

def get_processed_list(input_list):
    processed_list = fix_time(input_list)
    time_list = [row[0] for row in processed_list]
    x_list = [row[1] for row in processed_list]
    y_list = [row[2] for row in processed_list]
    x_list = clean_with_spline(x_list)
    y_list = clean_with_spline(y_list)

    for i in range(0, len(processed_list)):
        processed_list[i] = [time_list[i], x_list[i], y_list[i]]

    return processed_list

def get_frame_list(input_list, fps=60):
    frame_list = [[None, None] for i in range(0, fps*len(input_list))]
    last_index = 0
    for row in input_list:
        index = int(row[0] / (1/float(fps)))
        frame_list[index] = row[1:]
        last_index = index
    
    i = 0
    while i < len(frame_list):
        if frame_list[i] == [None, None]:
            if i < last_index:
                frame_list[i] = frame_list[i-1] # i think a reference is fine prob
            else:
                del frame_list[i]
                i -= 1
        i += 1
    
    return frame_list

def pack_frame_list_to_csv(filepath, frame_list):
    with open(filepath, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(frame_list)

warnings.filterwarnings("error", category=RuntimeWarning)
input_list = list_from_csv("unprocessed_frames.csv")
float_list = convert_input_to_float(input_list[:3900])
processed_list = get_processed_list(float_list)
frame_list = get_frame_list(processed_list)
pack_frame_list_to_csv("frames/frames.csv", frame_list)
