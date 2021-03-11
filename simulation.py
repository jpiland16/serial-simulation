from math import sin, cos, pi, radians, degrees, acos
from three.core import Base, FirstPersonController, Renderer, Scene, Mesh, Object3D
from three.cameras import PerspectiveCamera
from three.geometry import BoxGeometry, SphereGeometry
from three.material import SurfaceBasicMaterial, SurfaceLightMaterial
# from helpers import *
from three.lights import DirectionalLight
import time
import serial.tools.list_ports as stlp
import serial

# --------------------------------------------------------------------
# BEGIN MODIFIABLE PARAMETERS ----------------------------------------
# --------------------------------------------------------------------

red = [1.3,0,0]
orange = [2, 0.6, 0]
yellow = [2, 2, 0]
green = [0, 3, 0]
lblue = [1, 1.2, 3 ]
pink = [3, 1.3, 1.2]
mgray = [0.3,0.31,0.32]
dgray = [0.1, 0.1, 0.1]
black = [0,0,0]

CHEST_HEIGHT = 6
CHEST_WIDTH = 4
CHEST_THICKNESS = 1

UPPER_ARM_THICKNESS = 0.5
UPPER_ARM_LENGTH = 2.7

FOREARM_THICKNESS = 0.5
FOREARM_LENGTH = 2.3

PALM_THICKNESS = 0.2
PALM_LENGTH = 0.75
PALM_WIDTH = 0.5

FINGER_LENGTH = [0.7, 0.8, 0.7, 0.55]
FINGER_THICKNESS = 0.1
FINGER_SEPARATION = 0.02

# --------------------------------------------------------------------
#  END  MODIFIABLE PARAMETERS ----------------------------------------
# --------------------------------------------------------------------

class Joint(Object3D):

    def __init__(self, parent, translation, angle_verification, angle_conversion, rotation_axis):
        super(Joint, self).__init__()
        self.structures = []
        parent.add(self)
        self.verify_angle = angle_verification # Receives a function to check whether the angle is within the limits of the joint
        self.convert_angle = angle_conversion  # Receives a function to convert one angle to another (usually by reversing the direction of motion) if necessary
        self.transform.setPosition(translation[0], translation[1], translation[2])
        self.position = translation
        self.angle = 0
        self.rotation_axis = rotation_axis
        
    def add_structure(self, dimensions, translation, color, alpha=1):
        structure = Mesh( BoxGeometry(dimensions[0], dimensions[1], dimensions[2]), SurfaceLightMaterial(color=color, alpha=alpha))
        self.add(structure)
        structure.transform.setPosition(translation[0], translation[1], translation[2])

    def check_angle(self, deg):
        if(not self.verify_angle(deg)):
            raise ValueError("Angle " + str(deg) + " was out of bounds.")
        return self.convert_angle(deg)

    def set_angle(self, deg):
        angle = self.check_angle(deg)
        delta = angle - self.angle
        self.increment_angle(delta, False)

    def increment_angle(self, deg, needs_verification=True):
        
        self.angle += deg

        if needs_verification:
            self.verify_angle(self.angle)

        rad = pi * deg / 180

        if self.rotation_axis == "X":
            self.transform.rotateX(rad) 

        elif self.rotation_axis == "Y":
            self.transform.rotateY(rad)  

        elif self.rotation_axis == "Z":
            self.transform.rotateZ(rad)    

        self.transform.setPosition(self.position[0], self.position[1], self.position[2])

class Person(Base):
    
    def initialize(self):

        self.angles = [[10, 50, 60, 0, 15]]

        self.setWindowTitle('Simulation')
        self.setWindowSize(800,800)

        self.renderer = Renderer()
        self.renderer.setViewportSize(800,800)
        self.renderer.setClearColor(0.25,0.25,0.25)
        
        self.scene = Scene()

        self.camera = PerspectiveCamera()
        self.camera.transform.setPosition(0, 4, 11)
        self.camera.transform.lookAt(0, 0, 0)
        self.cameraControls = FirstPersonController(self.input, self.camera)

        background = Mesh(SphereGeometry(200, 64,64), SurfaceBasicMaterial(color=dgray))
        self.scene.add(background)

        self.directionalLight = DirectionalLight(position=[2,3,0], direction=[-1,-1, 0])
        self.scene.add(self.directionalLight)

        self.directionalLight2 = DirectionalLight(position=[2,3,0], direction=[1,1, 0], strength=0.3)
        self.scene.add(self.directionalLight2)

        # Create the parts of the simulation

        self.instances = []
        
        for index, i in enumerate(inst):
            self.instances.append(self.add_instance(index, i["color"], i["alpha"]))
        
        self.time = 0

    def add_instance(self, index, color=None, alpha=None):
        chestBase = Joint(self.scene, [2 + 4*index, 0, 2], lambda d: False, lambda d: 0, "N")
        chestBase.add_structure([CHEST_THICKNESS, CHEST_HEIGHT, CHEST_WIDTH], [0, 0, 0], red if color==None else color, 1 if alpha==None else alpha)
        chestBase.transform.rotateY( 3 * pi / 4 )
          
        shoulderFlexor = Joint(chestBase, [0, CHEST_HEIGHT / 2 - UPPER_ARM_THICKNESS / 2, - CHEST_WIDTH / 2 - UPPER_ARM_THICKNESS / 2], lambda d: True, lambda d: -d, "Z")
        shoulderAbductor = Joint(shoulderFlexor, [0, 0, 0], lambda d: (d <= 100) and (d >= 0), lambda d: d, "X")
        shoulderAbductor.add_structure([UPPER_ARM_THICKNESS, UPPER_ARM_LENGTH, UPPER_ARM_THICKNESS], [0, - UPPER_ARM_LENGTH / 2, 0], orange if color==None else color, 1 if alpha==None else alpha)
        
        elbow = Joint(shoulderAbductor, [0, -UPPER_ARM_LENGTH, 0], lambda d: (d >= 0) and (d <= 135), lambda d: -d, "Z")
        elbow.add_structure([FOREARM_THICKNESS, FOREARM_LENGTH, FOREARM_THICKNESS], [0, -FOREARM_LENGTH / 2, 0], yellow if color==None else color, 1 if alpha==None else alpha) 
        
        wrist = Joint(elbow, [0, -FOREARM_LENGTH, 0], lambda d: True, lambda d: d, "Y")
        wrist.add_structure([PALM_THICKNESS, PALM_LENGTH, PALM_WIDTH], [0, -PALM_LENGTH / 2, 0], green if color==None else color, 1 if alpha==None else alpha)

        thumbCMC = Joint(wrist, [0, PALM_LENGTH / 5, -PALM_WIDTH / 4], lambda d: True, lambda d: d, "X")
        thumbCMC.add_structure([FINGER_THICKNESS * 4/3, 2/3 * PALM_LENGTH, FINGER_THICKNESS * 4/3], [0, - 2/3 * PALM_LENGTH, 0], lblue if color==None else color, 1 if alpha==None else alpha)
        thumbCMC.set_angle(45)
        thumbCMC.transform.rotateY(pi / 12)

        fingerMCP = Joint(wrist, [-FINGER_THICKNESS, -PALM_LENGTH, 0], lambda d: d >= 0 and d <= 180, lambda d: -d, "Z")
        for i in range (0, 4):
            fingerMCP.add_structure([FINGER_THICKNESS, FINGER_LENGTH[i], FINGER_THICKNESS], [0, -FINGER_LENGTH[i] / 2, (i - 1.5) * (FINGER_THICKNESS + FINGER_SEPARATION)], pink if color==None else color, 1 if alpha==None else alpha)
        
        if len(self.instances) == len(self.angles): # true except in the initial case, where angles are added first
            self.angles.append([0,0,0,0,0])

        return {
            "shoulderAbductor": shoulderAbductor,
            "shoulderFlexor": shoulderFlexor,
            "elbow": elbow,
            "wrist": wrist,
            "fingerMCP": fingerMCP
        }
        

    def update(self):
        self.cameraControls.update()

        hundredths = (int) (self.time * 100)
        if hundredths % 10 < 2:
            labels = ['Shoulder abd.', "Shoulder flex.", "Elbow flex.", "Wrist pro.", "Finger flex."]
            printable_angles = [int(self.instances[0]["shoulderAbductor"].angle), int(self.instances[0]["shoulderFlexor"].angle), int(-self.instances[0]["elbow"].angle), int(self.instances[0]["wrist"].angle), int(-self.instances[0]["fingerMCP"].angle)]
            title = ""            
            for i in range(0, 5):
                title += labels[i] + ": " + str(printable_angles[i] % 360) + "\u00b0"
                if i is not 4:
                    title += ", "
            
            self.setWindowTitle(title)

        if self.input.resize():
            size = self.input.getWindowSize()
            self.camera.setAspectRatio( size["width"] / size["height"] )
            self.renderer.setViewportSize( size["width"] , size["height"] )
            
        
        self.time += self.deltaTime

        for i in range(0, len(self.instances)):
            self.instances[i]["shoulderAbductor"].set_angle(self.angles[i][0])
            self.instances[i]["shoulderFlexor"].set_angle(self.angles[i][1])
            self.instances[i]["elbow"].set_angle(self.angles[i][2])
            self.instances[i]["wrist"].set_angle(self.angles[i][3])
            self.instances[i]["fingerMCP"].set_angle(self.angles[i][4])  
            
        self.renderer.render(self.scene, self.camera)

class Render():
    def __init__(self, num_instances):
        self.reference = None
        global inst
        inst = num_instances

    def begin(self):
        p = Person()
        self.reference = p
        p.run()

if __name__ == "__main__":
    # demo code
    my_render = Render([{"color":None,"alpha":None}])
    my_render.begin()