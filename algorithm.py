from math import sin, cos, pi, radians, degrees, acos
import time
from types import SimpleNamespace
import statistics

MUSCLE_MAX = 18.74
STATE = "REST"
last_event = 0
alsAngles = [10, 50, 60, 0, 15]

def execute(data, should_print=False):
    # Data is an array
    return alshammary1(data, should_print)

def parse_data(raw_data):
    d = {
        "x1": float(raw_data[0]),
        "y1": float(raw_data[1]),
        "z1": float(raw_data[2]),
        "x2": float(raw_data[3]),
        "y2": float(raw_data[4]),
        "z2": float(raw_data[5]),
        "m1": float(raw_data[6]),
        "m2": float(raw_data[7]),
        "raw": raw_data
        }
    return d

def wrist_only(data, should_print):
    #global elbow_angle, up_count

    angles = [10, 50, 60, 0, 15]
    status = str(data["raw"])
    
    x = data["x1"]
    y = data["y1"]
    z = data["z1"]

    vec_mag = (x ** 2 + y ** 2 + z ** 2) ** 0.5
    phi = acos(z / vec_mag) * 180 / pi
    
    angles[3] = - 90 - phi * 3


    status += " phi = " + str(int(phi))
    
    if should_print and (time.time() * 100) % 10 < 2:
        print(status + "          \r", end="")

    for i in range(0,5):
        angles[i] %= 360

    return angles


def alshammary1(data, should_print):

    global STATE, alsAngles, last_event

    RECENCY = 10
    BICEP_ACTIVATION_THRESHOLD = 0.70 * MUSCLE_MAX
    TRICEP_ACTIVATION_THRESHOLD = 0.30 * MUSCLE_MAX
    EVENT_DELAY = 0.100 # seconds

    actual_data = data[-RECENCY:]

    bicep_data = arrayify(actual_data, "m1")
    tricep_data = arrayify(actual_data, "m2")

    if average(bicep_data) > BICEP_ACTIVATION_THRESHOLD and STATE != "TRICEP":
        last_event = time.time()
        STATE = "BICEP"
        alsAngles[2] = min(alsAngles[2] + 5, 135)

    elif average(tricep_data) > TRICEP_ACTIVATION_THRESHOLD and STATE != "BICEP":
        last_event = time.time()
        STATE = "TRICEP"
        alsAngles[2] = max(alsAngles[2] - 5, 0)

    elif (time.time() - last_event) > EVENT_DELAY:
        STATE = "REST"

    status = "Current state: " + STATE
    if should_print and (time.time() * 100) % 10 < 2:
        print(status + "          \r", end="")

    return alsAngles

def arrayify(data, attr):
    array = []
    for point in data:
        array.append(point[attr])
    return array

def average(data):
    if not data:
        return 0
    return sum(data)/len(data)

def is_outlier(value, data):
    OUTLIER_THRESHOLD = 3
    stdev = statistics.stdev(data)
    return (value - average(data)) - 0.001 > OUTLIER_THRESHOLD * stdev

def get_clean(data):
    cleaned_data = []
    for i in range(0, len(data)):
        if len(data) < 2 or not is_outlier(data[i], data):
            cleaned_data.append(data[i])
    print(cleaned_data)
    return cleaned_data