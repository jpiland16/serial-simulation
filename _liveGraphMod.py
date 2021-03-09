# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 12:37:41 2020

@author: jc16
"""

import serial
import time
import matplotlib.pyplot as plt
import numpy as np
import time
import serial.tools.list_ports as stlp
import threading
import _algorithm
import _simulation
import _simonSerial
import _videoCapture
import _dataRecording
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
except: # pylint: disable=bare-except
    pass

# -------------------------------------------
# Important parameters ----------------------
# -------------------------------------------

GRAPHING_ON = True
SIMULATION_ON = True
VIDEOCAPTURE_ON = False
DATARECORDINGS_ON = False

# Optionally hide some of the data from the graph to make it less cluttered 
# (True = that data does not appear on the graph)

ignore_index = [False, False, False, False, False, False, False, False]
#ignore_index = [True,  True,  True,  True,  True,  True,  False, False]
#ignore_index = [True,  True,  True,  False,  False,  False,  False, False]

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

text_x = 0
text_y = -20

#label to precede the list of values
#text_legend = "(blu X, org Y, grn Z, red M) = " 
text_legend = "" 

# NOTE: if graphing *n* things, then the list of values will take up 8*n characters. 
# The total line length should be less than or equal to 63 characters, i.e. len(text_legend) + 8 * n < 64.

win_ht = 5
win_wd = 7
# note: bigger window = more frames dropped :(

drop_frames = True # skip an update if we are falling behind
drop_threshold = 2 # size of waiting data before we start skipping frames

debug_wait = False # if True replaces the last graph with the number of messages waiting on the serial port

# -------------------------------------------
# -------------------------------------------
# -------------------------------------------

total_logs_received = 0
total_frames_dropped = 0

if SIMULATION_ON:
    _simonSerial.begin_sim()

if DATARECORDINGS_ON or VIDEOCAPTURE_ON:
    folder_name = _videoCapture.setup_folder()

if DATARECORDINGS_ON:
    _dataRecording.setup(num_of_graphs)

index = 0

x_points = []
y_points = []

lines = []

closePlot = False

def on_close(e):
    global closePlot
    closePlot = True

for i in range(0, num_of_graphs):
    y_points.append([])

if VIDEOCAPTURE_ON:
    _videoCapture.prepare(folder_name)

if GRAPHING_ON:
    fig = plt.figure(figsize=(win_wd, win_ht))
    ax2 = fig.add_subplot(1,1,1)
    ax2.xaxis.set_visible(False)
    
    for i in range(0, num_of_graphs):
        some_var, = ax2.plot([], lw=3)
        lines.append(some_var)
    
    text = ax2.text(text_x,text_y, text_legend, fontfamily="Consolas")
    ax2.set_ylim([plot_ymin,plot_ymax])
    ax2background = fig.canvas.copy_from_bbox(ax2.bbox)
    fig.canvas.draw()           
    
    fig.canvas.mpl_connect('close_event', on_close)
    
    plt.show(block=False)

start_time = time.time()

if not GRAPHING_ON and not SIMULATION_ON:
    print("Neither the simulation nor live graphing is active. Press CTRL-C to exit.")

def main():
    
    global index, x_points, y_points, total_logs_received, total_frames_dropped
    
    while True:
        if closePlot:
            break
        
        dataValues = []
        elapsed_time = round(time.time() - start_time, 2)
        x_points.append(elapsed_time)

        currentY = []
        
        if VIDEOCAPTURE_ON:
            _videoCapture.capture_frame()

        if not SIMULATION_ON or _simonSerial.simulation.is_alive():
            data = _simonSerial.update()
        else:
            break

        dataValues = data[0]
        angles = data[1]

        for i in range(0, num_of_graphs):
            dataPoint = 0
            
            if i < len(dataValues):
                dataPoint = float(dataValues[i])
                if i < len(ignore_index) and ignore_index[i]:
                    dataPoint = plot_ymax + 10
            
            y_points[i].append(dataPoint)
            currentY.append(dataPoint)
            
            if i == (num_of_graphs - 1) and debug_wait:
                y_points[i][-1] = serialPort.in_waiting
        
        if len(x_points) > max_list_length:
            x_points.pop(0)
            for i in range(0, num_of_graphs):
                y_points[i].pop(0)

        if DATARECORDINGS_ON:    
            _dataRecording.add_point(elapsed_time, currentY, angles)
        
        waiting_messages = _simonSerial.serialPort.in_waiting
        
        if drop_frames and waiting_messages > drop_threshold:
            total_frames_dropped += 1
            total_logs_received += 1
        else:
            total_logs_received += 1
            if GRAPHING_ON:
                live_update(True)
        
        index = index + 1
    exitFunction()

def live_update(blit = False):
    global ax2, fig, x, line, text, ax2background
    ax2.set_xlim(x_points[0], x_points[-1]+0.001)

    text.set_position((x_points[0] + text_x , text_y))
    label = text_legend + "("
    for i in range(0, num_of_graphs):
        label = label + "{:>6.2f}".format(y_points[i][-1])
        if (i != (num_of_graphs - 1)):
            label = label + ", "
    label = label + ")"        
    text.set_text(label)
    
    #img.set_data(np.sin(X/3.+k)*np.cos(Y/3.+k))
    for i in range(0, num_of_graphs):
        lines[i].set_data(x_points, y_points[i])
    
    # -----------------------------------------------------------------------------------------------------------------
    # NOTE: the below code is from https://stackoverflow.com/questions/40126176/fast-live-plotting-in-matplotlib-pyplot
    # -----------------------------------------------------------------------------------------------------------------
    
    if blit:
        # restore background
        fig.canvas.restore_region(ax2background)

        # redraw just the points
        for i in range(0, num_of_graphs):
            ax2.draw_artist(lines[i])
            
        ax2.draw_artist(text)
        fig.canvas.blit(ax2.bbox)

    else:
        fig.canvas.draw()

    fig.canvas.flush_events()
    
    # -----------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------

def exitFunction():
    _simonSerial.serialPort.close()
    print("Serial port closed.        ")
    if SIMULATION_ON and _simonSerial.simulation.is_alive:
        _simonSerial.render.reference.running = False
        if GRAPHING_ON:
            plt.close()
    if VIDEOCAPTURE_ON:
        _videoCapture.complete()
    if DATARECORDINGS_ON:
        _dataRecording.complete(folder_name)

try:
    main()
except KeyboardInterrupt:
    exitFunction()
except:
    exitFunction()
    raise