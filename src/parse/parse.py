import re
import csv
import cv2
import easyocr
from google.colab.patches import cv2_imshow
from time import perf_counter

unproc_frame_list = []

reader = easyocr.Reader(["en"], gpu=True)
capture = cv2.VideoCapture("/kaggle/input/batch2/Blank123.mp4")
configuration = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.'

if not capture.isOpened():
  print("didn't opem")

current_frame = 0
s_t = perf_counter()
while True:
  ret, frame = capture.read()
  current_frame += 1
  if (current_frame % 100) == 0:
    print(f"Current Frame: {current_frame}")

  if not ret:
    break


  frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

  time_crop = frame[0:60, 800:1020]
  x_crop = frame[220:257, 40:130]
  y_crop = frame[253:287, 40:130]

  #time_crop = cv2.GaussianBlur(frame, (3, 3), 0)
  #x_crop = cv2.GaussianBlur(frame, (3, 3), 0)
  #y_crop = cv2.GaussianBlur(frame, (3, 3), 0)

  #time_str = pytesseract.image_to_string(time_crop, lang="eng", config=configuration)
  #x_str = pytesseract.image_to_string(x_crop, lang="eng", config=configuration)
  #y_str = pytesseract.image_to_string(y_crop, lang="eng", config=configuration)

  time_str = reader.readtext(time_crop, allowlist="0123456789.")
  x_str = reader.readtext(x_crop, allowlist="0123456789.")
  y_str = reader.readtext(y_crop, allowlist="0123456789.")

  if not time_str:
    time_str = [[None, "-1000.0"]]
  if not x_str:
    x_str = [[None, "-10000.0"]]
  if not y_str:
    y_str = [[None, "-10000.0"]]

  time = ".".join(re.findall(r"\d+", time_str[0][1]))
  x = ".".join(re.findall(r"\d+", x_str[0][1]))
  y = ".".join(re.findall(r"\d+", y_str[0][1]))
  try:
    if x[0] == "1" and (unproc_frame_list[-1][1][0] == "7" or unproc_frame_list[-1][1][0] == "6"):
      x = "7" + x[1:]
  except Exception:
    x = "-10000"
  try:
    if y[0] == "1" and (unproc_frame_list[-1][2][0] == "7" or unproc_frame_list[-1][2][0] == "6"):
      y = "7" + y[1:]
  except Exception:
    y = "-10000"

  unproc_frame_list.append([time, x, y])

with open("unprocessed_frames.csv", "w", newline="") as file:
  writer = csv.writer(file)
  writer.writerows(unproc_frame_list)

capture.release()
