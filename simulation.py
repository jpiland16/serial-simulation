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
        
    def add_structure(self, dimensions, translation, color):
        structure = Mesh( BoxGeometry(dimensions[0], dimensions[1], dimensions[2]), SurfaceLightMaterial(color=color))
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

        self.angles = [10, 50, 60, 0, 15]

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

        self.chestBase = Joint(self.scene, [2, 0, 2], lambda d: False, lambda d: 0, "N")
        self.chestBase.add_structure([CHEST_THICKNESS, CHEST_HEIGHT, CHEST_WIDTH], [0, 0, 0], red)
        self.chestBase.transform.rotateY( 3 * pi / 4 )
          
        self.shoulderFlexor = Joint(self.chestBase, [0, CHEST_HEIGHT / 2 - UPPER_ARM_THICKNESS / 2, - CHEST_WIDTH / 2 - UPPER_ARM_THICKNESS / 2], lambda d: True, lambda d: -d, "Z")
        self.shoulderAbductor = Joint(self.shoulderFlexor, [0, 0, 0], lambda d: (d <= 100) and (d >= 0), lambda d: d, "X")
        self.shoulderAbductor.add_structure([UPPER_ARM_THICKNESS, UPPER_ARM_LENGTH, UPPER_ARM_THICKNESS], [0, - UPPER_ARM_LENGTH / 2, 0], orange)
        
        self.elbow = Joint(self.shoulderAbductor, [0, -UPPER_ARM_LENGTH, 0], lambda d: (d >= 0) and (d <= 135), lambda d: -d, "Z")
        self.elbow.add_structure([FOREARM_THICKNESS, FOREARM_LENGTH, FOREARM_THICKNESS], [0, -FOREARM_LENGTH / 2, 0], yellow) 
        
        self.wrist = Joint(self.elbow, [0, -FOREARM_LENGTH, 0], lambda d: True, lambda d: d, "Y")
        self.wrist.add_structure([PALM_THICKNESS, PALM_LENGTH, PALM_WIDTH], [0, -PALM_LENGTH / 2, 0], green)

        self.thumbCMC = Joint(self.wrist, [0, PALM_LENGTH / 5, -PALM_WIDTH / 4], lambda d: True, lambda d: d, "X")
        self.thumbCMC.add_structure([FINGER_THICKNESS * 4/3, 2/3 * PALM_LENGTH, FINGER_THICKNESS * 4/3], [0, - 2/3 * PALM_LENGTH, 0], lblue)
        self.thumbCMC.set_angle(45)
        self.thumbCMC.transform.rotateY(pi / 12)

        self.fingerMCP = Joint(self.wrist, [-FINGER_THICKNESS, -PALM_LENGTH, 0], lambda d: d >= 0 and d <= 180, lambda d: -d, "Z")
        for i in range (0, 4):
            self.fingerMCP.add_structure([FINGER_THICKNESS, FINGER_LENGTH[i], FINGER_THICKNESS], [0, -FINGER_LENGTH[i] / 2, (i - 1.5) * (FINGER_THICKNESS + FINGER_SEPARATION)], pink)
        
        self.time = 0

    def update(self):
        
        self.cameraControls.update()

        hundredths = (int) (self.time * 100)
        if hundredths % 10 < 2:
            labels = ['Shoulder abd.', "Shoulder flex.", "Elbow flex.", "Wrist pro.", "Finger flex."]
            printable_angles = [int(self.shoulderAbductor.angle), int(self.shoulderFlexor.angle), int(-self.elbow.angle), int(self.wrist.angle), int(-self.fingerMCP.angle)]
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

        self.shoulderAbductor.set_angle(self.angles[0])
        self.shoulderFlexor.set_angle(self.angles[1])
        self.elbow.set_angle(self.angles[2])
        self.wrist.set_angle(self.angles[3])
        self.fingerMCP.set_angle(self.angles[4])  
        
        self.renderer.render(self.scene, self.camera)

class Render():
    def __init__(self):
        self.reference = None

    def begin(self):
        p = Person()
        self.reference = p
        p.run()