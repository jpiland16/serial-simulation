import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt
import os
import json

# if you want the most recent file, use 1; Second most recent --> 2, etc.
USE_RECENT = 2

directories = []
chosen_path = ""

prefix_path = "recorded-data/"

if not os.path.isdir(prefix_path):
    os.mkdir(prefix_path)

for item in os.listdir(prefix_path):
    if os.path.isdir(prefix_path + item):
        directories.append(prefix_path + item)

if USE_RECENT > len(directories) or not USE_RECENT > 0:
    raise SystemError("Index out of range.")
else:
    chosen_path = directories[-USE_RECENT] + "/"

if not os.path.exists(chosen_path + "video.avi") or not os.path.exists(chosen_path + "data.txt"):
    raise SystemError("Required file missing from directory.")    

with open(chosen_path + "data.txt","a+") as file:

    # Move pointer from end to beginning
    file.seek(0,0) # 0 bytes from beginning (0 = beginning, 1 = current pos, 2 = end)
    
    #Read file
    file_data = file.read()
    
    #Initialize dataObj to empty
    dataObj = []
    
    if len(file_data) > 0:
        dataObj = json.loads(file_data)



# --------------------------------------------------------------------------------------------------------------------------------------------------------
# NOTE: the below code is modified from https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
# --------------------------------------------------------------------------------------------------------------------------------------------------------

cap = cv2.VideoCapture(chosen_path + "video.avi")

num_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

while(cap.isOpened()):
    ret, frameBGR = cap.read()
    
    frameRGB = cv2.cvtColor(frameBGR, cv2.COLOR_BGR2RGB)
    
    if ret:
        cv2.imshow('frame', frameBGR)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------