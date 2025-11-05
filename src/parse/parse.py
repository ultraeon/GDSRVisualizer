import re
import csv
import cv2
import easyocr
from google.colab.patches import cv2_imshow
from time import perf_counter

unproc_frame_list = []

reader = easyocr.Reader(["en"], gpu=True)
capture = cv2.VideoCapture("TowerTAS.mp4")
configuration = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.'

if not capture.isOpened():
  print("didn't opem")

current_frame = 0
s_t = perf_counter()
while True:
  ret, frame = capture.read()
  current_frame += 1
  if (current_frame % 500) == 0:
    print(f"Current Frame: {current_frame}")
  
  if not ret:
    break

  frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

  time_crop = frame[10:60, 830:1030]
  x_crop = frame[70:100, 200:325]
  y_crop = frame[100:130, 200:325]

  #time_str = pytesseract.image_to_string(time_crop, lang="eng", config=configuration)
  #x_str = pytesseract.image_to_string(x_crop, lang="eng", config=configuration)
  #y_str = pytesseract.image_to_string(y_crop, lang="eng", config=configuration)

  time_str = reader.readtext(time_crop, allowlist="0123456789.")
  x_str = reader.readtext(x_crop, allowlist="0123456789.")
  y_str = reader.readtext(y_crop, allowlist="0123456789.")
  
  if not time_str:
    time_str = [[None, "0.0"]]
  if not x_str:
    x_str = [[None, "0.0"]]
  if not y_str:
    y_str = [[None, "0.0"]]
  
  time = ".".join(re.findall(r"\d+", time_str[0][1]))
  x = ".".join(re.findall(r"\d+", x_str[0][1]))
  y = ".".join(re.findall(r"\d+", y_str[0][1]))

  unproc_frame_list.append([time, x, y])

with open("unprocessed_frames.csv", "w", newline="") as file:
  writer = csv.writer(file)
  writer.writerows(unproc_frame_list)

capture.release()