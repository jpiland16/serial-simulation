import numpy as np
import cv2 as cv2
import time
from datetime import datetime
import os

def setup_folder():
    time_text = "{:%Y.%m.%d %H-%M-%S}".format(datetime.now())

    if not os.path.exists("recorded-data\\" + time_text):
        os.makedirs("recorded-data\\" + time_text)

    return time_text

def prepare(folder_name):
    print("Video recording in progress...")
    global cap, out

    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('recorded-data\\' + folder_name + '\\video.avi',fourcc, 30.0, (640,480))


# --------------------------------------------------------------------------------------------------------------------------------------------------------
# NOTE: the below code is modified from https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
# --------------------------------------------------------------------------------------------------------------------------------------------------------

def capture_frame():
    # Capture frame-by-frame
    ret, frame = cap.read()

    if ret:
        # Our operations on the frame come here
        disp_frame = cv2.flip(frame, 1)

        # write the flipped frame
        out.write(frame)

        # Display the resulting frame
        cv2.imshow('frame', disp_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): # wait for 1 millisecond
            pass

def complete():
    # When everything done, release the capture
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------