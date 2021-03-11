import json

MAX_SIZE = 1024000

x_points = []
y_points = []
angles = []

def setup(num_of_graphs, num_of_angles=5):
    for i in range(0, num_of_graphs):
        y_points.append([])
    for i in range(0, num_of_angles):
        angles.append([])

def add_point(x, y_array, angle_array):
    x_points.append(x)
    for i in range(0, len(y_array)):
        if i < len(y_points):
            y_points[i].append(y_array[i])
    for i in range(0, len(angle_array)):
        if i < len(angles):
            angles[i].append(angle_array[i])

def complete(folder_name):
    with open("recorded-data\\" + folder_name + "\\data.txt","w") as file:
        data = json.dumps([x_points,y_points,angles])
        file.write(data)