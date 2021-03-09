import time
import serial.tools.list_ports as stlp
import serial
import threading
import _algorithm
import _simulation

# BEGIN PARAMETER SECTION -----------------

CHECK_PORTS = True
BAUD_RATE = 115200
DATA_HX_SIZE = 100

#  END  PARAMETER SECTION -----------------

all_data = []

found_port = False
using_sim = False

comport = "COM6"

if (CHECK_PORTS):
    print("Seraching COM ports...")
    ports = stlp.comports()
    for port in ports:
        if(port.description[0:9] == "P1 Serial"):
            comport = port.device
            found_port = True
            # print(port.description + " found!")

if not found_port and CHECK_PORTS:
    raise SystemError("Particle Photon not connected.")

serialPort = serial.Serial(comport, BAUD_RATE)
print("Serial port " + comport +  " opened at " + str(BAUD_RATE) + " baud.")

def begin_sim():
    global render, simulation, using_sim
    using_sim = True
    render = _simulation.Render()
    simulation = threading.Thread(target=render.begin)
    simulation.start()

def update():
    binaryData = serialPort.readline()
    if binaryData is not None:
        textData = binaryData.decode().rstrip()
        dataValues = textData.split(",")

        all_data.append(_algorithm.parse_data(dataValues))
        if(len(all_data) > DATA_HX_SIZE):
            all_data.pop(0)

    angles = _algorithm.execute(all_data)

    if using_sim and render.reference is not None:
        render.reference.angles = angles

    return [dataValues, angles]

def main():
    begin_sim()
    while True:
        update()
        if using_sim and not simulation.is_alive():
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except:
        raise
