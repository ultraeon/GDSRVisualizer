import numpy as np
import csv

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

def fix_time(input_list, tolerance=0.2):
    outlier_list = [False for row in input_list]
    input_list[0] = [0.0, 42, 225]
    last_valid = 0
    for i in range(1, len(outlier_list)):
      delta_t = input_list[i][0] - input_list[last_valid][0]
      if((delta_t < ((i - last_valid)*tolerance)) and (delta_t > 0)):
        last_valid = i
      else:
        outlier_list[i] = True

    start_index = 0
    end_index = 0
    for i in range(1, len(outlier_list)):
      if outlier_list[i]:
        if start_index == 0:
          start_index = i
      else:
        if start_index != 0:
          end_index = i
          input_list = interpolate_time(input_list, start_index, end_index, min(i-1, 5))
          start_index = 0

    return input_list

def interpolate_time(input_list, start_index, end_index, amount=5):
  points_x = []
  points_y = []
  for i in range(start_index-amount, start_index):
    points_x.append(i)
    points_y.append(input_list[i][0])
  for i in range(end_index, end_index + amount):
    points_x.append(i)
    points_y.append(input_list[i][0])

    m, b = np.polyfit(points_x, points_y, 1)
    for i in range(start_index, end_index):
      input_list[i][0] = m * i + b
    return input_list

def regression_smooth(input_list, index, tolerance=700.0, amount=3):
  outlier_list = [False for row in input_list]
  last_valid = 0
  for i in range(1, len(outlier_list)):
    if (abs(input_list[last_valid][index]-input_list[i][index]) < (tolerance * (input_list[i][0]-input_list[last_valid][0]))):
      last_valid = i
    else:
      outlier_list[i] = True

  start_index = 0
  end_index = 0
  for i in range(0, len(outlier_list)):
    if outlier_list[i]:
      if start_index == 0:
        start_index = i
    else:
      if start_index != 0:
        end_index = i
        input_list = interpolate_regression(input_list, index, start_index, end_index, min(amount, i-1))
        start_index = 0

  return input_list

def interpolate_regression(input_list, index, start_index, end_index, amount):
  points_x = []
  points_y = []
  for i in range(start_index-amount, start_index):
    points_x.append(input_list[i][0])
    points_y.append(input_list[i][index])
  for i in range(end_index, end_index+amount):
    points_x.append(input_list[i][0])
    points_y.append(input_list[i][index])

  m, b = np.polyfit(points_x, points_y, 1)
  for i in range(start_index, end_index):
    input_list[i][index] = m * input_list[i][0] + b
  return input_list

def get_processed_list(input_list):
    processed_list = fix_time(input_list, tolerance=0.1)
    processed_list = regression_smooth(processed_list, tolerance=1000.0, index=1)
    processed_list = regression_smooth(processed_list, tolerance=1000.0, index=2)
    return processed_list

def get_frame_list(input_list, fps=60):
    input_list[0] = [0.0, 42, 225]
    frame_list = [[None, None] for i in range(0, fps*len(input_list))]
    last_index = 0
    for row in input_list:
        index = int(row[0] / (1/float(fps)))
        frame_list[index] = row[1:]
        if frame_list[index][0] > 11000 or frame_list[index][0] < 0:
          frame_list[index] = [None, None]
        elif frame_list[index][1] > 950 or frame_list[index][1] < 0:
          frame_list[index] = [None, None]
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

input_list = list_from_csv("unprocessed_frames.csv")
float_list = convert_input_to_float(input_list[:])
processed_list = get_processed_list(float_list)
frame_list = get_frame_list(processed_list)
pack_frame_list_to_csv("blank123_frames.csv", frame_list[:])
