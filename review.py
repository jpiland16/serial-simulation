import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import os
import json
import time

# -------------------------------------------
# Important parameters ----------------------
# -------------------------------------------

# x1 (blue) 
# y1 (orange) 
# z1 (green) 
# x2 (red) 
# y2 (purple) 
# z2 (brown)
# m1 (pink)
# m2 (gray)

max_list_length = 50 # how much data you can see at once
num_of_graphs = 8 # how many different things you are going to graph

plot_ymin = -21
plot_ymax = 21
plot_width_seconds = 5

text_x = 0
text_y = -20

#label to precede the list of values
#text_legend = "(blu X, org Y, grn Z, red M) = " 
text_legend = "" 

# NOTE: if graphing *n* things, then the list of values will take up 8*n characters. 
# The total line length should be less than or equal to 63 characters, i.e. len(text_legend) + 8 * n < 64.

win_ht = 4
win_wd = 10
# note: bigger window = more frames dropped :(

drop_frames = True # skip an update if we are falling behind
drop_threshold = 2 # size of waiting data before we start skipping frames

debug_wait = False # if True replaces the last graph with the number of messages waiting on the serial port

# if you want the most recent file, use 1; Second most recent --> 2, etc.
USE_RECENT = 2

directories = []
chosen_path = ""

# -------------------------------------------
# -------------------------------------------
# -------------------------------------------

prefix_path = "recorded-data/"

STATE = "PAUSED"
current_frame = 0;
fps = 30;

x_points = []
y_points = []

lines = []

closePlot = False

def on_close(e):
    global closePlot
    closePlot = True

for i in range(0, num_of_graphs):
    y_points.append([])

if not os.path.isdir(prefix_path):
    os.mkdir(prefix_path)

for item in os.listdir(prefix_path):
    if os.path.isdir(prefix_path + item):
        directories.append(prefix_path + item)

if USE_RECENT > len(directories) or not USE_RECENT > 0:
    raise SystemError("Index out of range. (Try decreasing the USE_RECENT variable, or recording new data.)")
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
    else:
        raise SystemError("The data.txt file was empty.")

x_points = dataObj[0]

def main():
    global cap, num_frames
    cap = cv2.VideoCapture(chosen_path + "video.avi")
    num_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    my_frame = get_frame(7)
    create_plot(len(dataObj[1]))


def create_plot(num_of_graphs):
    global lines, fig, im, ax1, ax1background, text, slider
    fig, (ax0, ax1) = plt.subplots(1,2,figsize=(win_wd, win_ht))
    
    ax0.axis("off")
        
    plt.subplots_adjust(bottom=0.2)
    
    ax1.xaxis.set_visible(False)
    
    for i in range(0, num_of_graphs):
        some_var, = ax1.plot([], lw=3)
        lines.append(some_var)
    
    text = ax1.text(text_x,text_y, text_legend, fontfamily="Consolas")
    ax1.set_ylim([plot_ymin,plot_ymax])
    ax1background = fig.canvas.copy_from_bbox(ax1.bbox)
    fig.canvas.draw()           
    
    fig.canvas.mpl_connect('close_event', on_close)
    
    legend_labels = ["x1", "y1", "z1", "x2", "y2", "z2", "m1", "m2"]
    for i, y_points in enumerate(dataObj[1]):
        l, = plt.plot(x_points, y_points, label = legend_labels[i])
        
    #plt.legend()
    
    axpos = plt.axes([0.2, 0.1, 0.65, 0.03])
    slider = Slider(axpos, 'Time (s)', 0, (num_frames - 1)/fps, valinit=0)
    slider.on_changed(slide)
    
    im = ax0.imshow(get_frame(1))
    
    plt.show(block=False)
    update_plot()

def slide(e):
    global current_frame
    """
    PSEUDOCODE:
        if playing:
            pause()
    """
    current_frame = round(slider.val * fps)
    update_plot()
    #print(str(current_frame) + "    \r", end="")

def update_plot():
    global text
    frame = min(current_frame, len(dataObj[0]) - 1)
    if (frame) > plot_width_seconds*fps:
        start = dataObj[0][frame - fps*plot_width_seconds]
        end = dataObj[0][frame]
    else:
        start = dataObj[0][0]
        end = dataObj[0][fps*plot_width_seconds]
        
    label = text_legend + "("
    for i in range(0, num_of_graphs):
        label = label + "{:>6.2f}".format(dataObj[1][i][frame])
        if (i != (num_of_graphs - 1)):
            label = label + ", "
        if i == 4:
            label += "\n"
    label = label + ")"        
    text.set_text(label)    
    text.set_position((text_x + start, text_y))
        
    ax1.axis([start, end, plot_ymin, plot_ymax])
    im.set_array(get_frame(frame + 1))


def get_frame(frame_index):
    if frame_index < num_frames and frame_index >= 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frameBGR = cap.read()
        frameRGB = cv2.cvtColor(frameBGR, cv2.COLOR_BGR2RGB)
        return frameRGB
    else:
        raise IndexError("Frame index out of range.")
        
        

if __name__ == "__main__":
    main()