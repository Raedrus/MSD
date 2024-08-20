#XY MOVEMENT CONTROLS
#Summary: Processes information from machine vision, to move stepper motor accordingly

from time import sleep
from gpiozero import DigitalOutputDevice
from gpiozero import DigitalInputDevice
from gpiozero import Button
import numpy as np
import math


#Pin Assignments###############################################
#IR Encoders for movement
pin_ir_enc1 = 10
pin_ir_enc2 = 22

#XY Gantry Motors Drivers
pin_y_drv8825_en = 18
pin_y_drv8825_step = 23
pin_y_drv8825_dir = 24

pin_x_drv8825_en = 16
pin_x_drv8825_step = 20
pin_x_drv8825_dir = 21

#Setup##########################################################
#Setup Encoders

ir_enc1 = DigitalInputDevice(pin_ir_enc1)
ir_enc2 = DigitalInputDevice(pin_ir_enc2)


#Arbitrary values defining encoder coordinate positions
ENC1_COOR = 54  
ENC2_COOR = -12

#Setup XY Motors Drivers

y_drv8825_en = DigitalOutputDevice(pin_y_drv8825_en)
y_drv8825_step = DigitalOutputDevice(pin_y_drv8825_step)
y_drv8825_dir = DigitalOutputDevice(pin_y_drv8825_dir)

x_drv8825_en = DigitalOutputDevice(pin_x_drv8825_en)
x_drv8825_step = DigitalOutputDevice(pin_x_drv8825_step)
x_drv8825_dir = DigitalOutputDevice(pin_x_drv8825_dir)


#Setup Limit Switches
y_homingswitch = Button(9, pull_up = False)
x_homingswitch = Button(11, pull_up = False)

#TESTING####################################################################################
#TEST DATA

#Sample Data: Used to simulate data extracted by machine vision#####
#"B" for battery, "E" for Electronics
typeposi_data = np.array([
    ["B", "E", "B", "E"], #Waste Type
    [1.5, 4, 1, 9], #X-Coordinates of waste (in cm, relative to origin)
    [5, 7, 2, 8]    #Y-Coordinates of waste (in cm, relative to origin)
])

#Assume the gripper position is updated each time it a) homes, each time it reaches the b) encoders and
#each time it c) goes towards a waste

gripper_posi = [4, 1] #Position of the gripper [X,Y] (in cm, relative to origin)
#Use comment to disable sample data when actual smart dustbin is used

coor_chosen_waste = [0, 0]

#TEST FUNCTIONS
def homingswitchestest():
    while True:
        if y_homingswitch.is_pressed:
            print("Y Limit Switch Triggered")
            sleep(0.25)
        elif x_homingswitch.is_pressed:
            print("X Limit Switch Triggered")
            sleep(0.25)

def irencstest():
    while True:
        print("IR Encoder 1 reads:", ir_enc1.value)
        print("IR Encoder 2 reads:", ir_enc2.value)
        print("Note 0 for absence, 1 for presence of object blocking the sensor")
        sleep(1)

#Dustbin Core Functions######################################################

#SHORTEST DISTANCE IN STEPS
def getshortestdist(gripper_posi, typeposi_data, distperpix):
    #DistPerPix assumed to be in cm
    
    arr_dimensions = typeposi_data.shape
    typeposi_rows, typeposi_cols = arr_dimensions


    current_shortest = float('inf') #Initialization to a very large value #Needed for choosing shortest distance

    for col_index in range(typeposi_cols):
        print("Waste ", col_index + 1) #Verify data extracted

        waste_xposi = float(typeposi_data[1][col_index])
        waste_yposi = float(typeposi_data[2][col_index])

        print(" waste_XPosi= ", waste_xposi, " waste_YPosi= ", waste_yposi) #Verify Data Extracted
        print("Gripper_Posi X= ", gripper_posi[0], " Gripper_Posi Y= ", gripper_posi[1])

        dif_x = waste_xposi - float(gripper_posi[0])
        dif_y = waste_yposi - float(gripper_posi[1])

        print("dif_X= ", dif_x) #For Verification
        print("dif_Y= ", dif_y) #For Verification

        shortest_dist_cm = round(math.sqrt(abs(dif_x)**2 + abs(dif_y)**2), 3)

        print("shortest_dist_cm=",shortest_dist_cm) #For Verification

        if shortest_dist_cm <= current_shortest:
            current_shortest = shortest_dist_cm #current_shortest refers to the shortest route found from gripper to waste
            x_short_dif_posi = dif_x * distperpix #Memorize the x-coordinate of the nearest waste (PIXEL MAPPED TO CM)
            y_short_dif_posi = dif_y * distperpix #Memorize the y-coordinate of the nearest waste (PIXEL MAPPED TO CM)

            #Memorize position of chosen waste, it is where the gripper will arrive later:
            coor_chosen_waste[0] = waste_xposi
            coor_chosen_waste[1] = waste_yposi

    #For Verification
    print("current_shortest= ", current_shortest) 
    print("X_short_dif_posi= ", x_short_dif_posi)
    print("Y_short_dif_posi= ", y_short_dif_posi) 
    print("coor_chosen_waste= ", coor_chosen_waste)

    return cmToMotorSteps(1.8, 22.41, x_short_dif_posi, y_short_dif_posi)



def cmToMotorSteps(step_angle, gt2_pulleydiameter, x_short_dif_posi, y_short_dif_posi):
    #Takes in stepper motor parameters, diameter of the pulley and difference
    #of distance between one position to a another in and x and y, translates
    #those into number of steps for the motor, returned in a tupple [X steps, Y steps]
    #NOTE DUE TO FIXED STEP ANGLES OF STEPPER MOTORS, THERE MAY BE SLIGHT DEVIATIONS

    steps_per_rev = 360 / step_angle #For example, step angle of 1.8 would require 200 steps to complete a revolution
    #If it is a half step, 1.8/2 can be specified here

    mm_distperstep = round(gt2_pulleydiameter, 3) / steps_per_rev #Approximate distance traveled by gantry each motor step

    x_short_dif_posi = x_short_dif_posi * 10 #UNIT CONVERSION: cm to mm
    y_short_dif_posi = y_short_dif_posi * 10 #UNIT CONVERSION: cm to mm

    x_stepstotravel = int(x_short_dif_posi / mm_distperstep)
    y_stepstotravel = int(y_short_dif_posi / mm_distperstep)

    print("X_StepsToTravel= ", x_stepstotravel)
    print("Y_StepsToTravel= ", y_stepstotravel)

    return [x_stepstotravel, y_stepstotravel]



#STEPPER MOTOR: COREXY
def drivedrv8825(steps, dir, microstep, selected_xy, time_delay, homing = False, tobin = None, list_XYSteps = None, list_DirXY = None, invert_xDir = False, invert_yDir = False, x_offset = 0, y_offset = 0):
    #En_Motors = 1 to turn motor on
    #Dir = Boolean to control direction of motor spin (1 to spin anticlockwise (reference: shaft pointing at your face))
    #Steps = The number of steps for the stepper motor to takewhile
    #Microstep = Whether it it is full step, half step, 1/4, 1/8, 1/16 or 1/32
    #Selected_XY = Whether DRV8825 for X or Y is selected use "XY" TO ENABLE SIMULTANEOUS AXIS MOVEMENT,
    #SIMULTAENOUS MOVEMENT REQUIRES list_XYSteps and list_DirXY
    #time_delay = Delay between each step, influences motor speed
    #homing is a boolean, setting it to true causes the selected axis to home instead
    #ToBIn is useful for making the stepper motor move in y-axis direction towards one of the encoders
    #When: None = Disabled, 1 = Move to one of the encoders, 0 Move to another encoder
    #invert_xDir  when set to true, will invert inputted dir or list_DirXY X
    #invert_y_Dir when set to true, will invert inputted dir or list_DirXY X
    #x_offset, y_offset refers to offset in terms of steps, useful for calibration

    #NOTE: While homing or in simultaneous mode, the Steps parameter is not signifigant, can be any number
    #Dir is ignored in simultaenous mode
    
    

    #Direction inversion decisions
    print("\n\n########################################################################")
    if ((invert_xDir == True) or (invert_yDir == True)) and (list_DirXY is None):
        dir = not(dir)
        print("Dir Inverted")
    #In multi axis mode, you can set whichever invert_xDir or invert_yDir to cause inversion
    elif (invert_xDir == True) and (invert_yDir == False) and (list_DirXY is not None):
        list_DirXY[0] = not(list_DirXY[0])
        print("xDir Inverted")
    elif (invert_xDir == False) and (invert_yDir == True) and (list_DirXY is not None):
        list_DirXY[1] = not(list_DirXY[1])
        print("yDir Inverted")
    elif (invert_xDir == True) and (invert_yDir == True) and (list_DirXY is not None):
        list_DirXY[0] = not(list_DirXY[0])
        list_DirXY[1] = not(list_DirXY[1])
        print("xDir and yDir Inverted")
        


    #Refer to the dictionary below for what to place into this parameter
    #Note: For DRV8825, the EN pin, RST pin and SLP pin are active LOW
    #Thus to enable the DRV8825, its EN pin should be set to false



    #Microstep Guide for reference (DRV8825) - PHYSICAL PINS
    # MODE0    MODE1    MODE2    Microstep Resolution
    # Low    Low        Low     Full step
    # High    Low        Low        Half step
    # Low    High    Low        1/4 step
    # High    High    Low        1/8 step
    # Low    Low        High    1/16 step
    # High    Low        High    1/32 step
    # Low    High    High    1/32 step
    # High    High    High    1/32 step

    #Use these names to specify microstep
    microsteps =  {'Full':1,
                    'Half':2,
                    '1/4':4,
                    '1/8':8,
                    '1/16':16,
                    '1/32':32}


    #If full steps uses 200 steps to complete with a delay of 0.005,
    #using half step would require 400 steps, and if we keep the delay 0.005
    #the process will become twice as long, thus the below is to adjust
    #the time delay between each step so that all types of steps complete
    #their journey with the same amount of time

    time_delay = time_delay / microsteps[microstep]
    
    #To compensate for the numbers of steps
    print("Check microstep value ", microsteps[microstep])
    steps = steps * microsteps[microstep]

    if selected_xy == "X":
        
        x_drv8825_en.off()   #Turn ON the chosen motor
        if dir:
            x_drv8825_dir.on()  #Direction of turn selected
        else:
            x_drv8825_dir.off()

    elif selected_xy == "Y":
        y_drv8825_en.off()   #Turn ON the chosen motor
        if dir:
            y_drv8825_dir.on()  #Direction of turn selected
        else:
            y_drv8825_dir.off()
            
    elif selected_xy == "XY" and list_DirXY != None:
        
        
        x_drv8825_en.off()   #Turn ON the chosen motor
        if list_DirXY[0] == True:
            x_drv8825_dir.on()  #Direction of turn selected
            print("Direction Check")
            print("x_drv8825_dir = 1")
        else:
            x_drv8825_dir.off()
            print("Direction Check")
            print("x_drv8825_dir = 0")
        
        if list_DirXY[1] == True:
            y_drv8825_dir.on()  #Direction of turn selected
            print("Direction Check")
            print("y_drv8825_dir = 1")
        else:
            y_drv8825_dir.off()
            print("Direction Check")
            print("y_drv8825_dir = 0")
        
        
        y_drv8825_en.off()   #Turn ON the chosen motor
        if list_DirXY[1]:
            y_drv8825_dir.on()  #Direction of turn selected
            print("Direction Check")
            print("y_drv8825_dir = 1")
        else:
            y_drv8825_dir.off()
            print("Direction Check")
            print("y_drv8825_dir = 0")
        
        
    else:
        
        print("WARNING: UNKNOWN CHOICE FOR GANTRY (X OR Y OR XY?)")


    if homing == False and tobin == None:
        if selected_xy == "X":
            for i in range(abs(steps - x_offset)):
                x_drv8825_step.on()
                sleep(time_delay)
                x_drv8825_step.off()
                sleep(time_delay)
                print(f"Stepping X-axis motor {i+1}/{steps}")
            
            sleep(1) #A brief pause before disabling the motor, so that inertia is accounted for
            x_drv8825_en.on() #Disable the motor, may reduce holding torque but reduce power dissipation
            
        elif selected_xy == "Y":
            for i in range(abs(steps - y_offset)):
                y_drv8825_step.on()
                sleep(time_delay)
                y_drv8825_step.off()
                sleep(time_delay)
                print(f"Stepping Y-axis motor {i+1}/{steps}")
        elif selected_xy == "XY":
            print("list_XYSteps[0] + list_XYSteps[1]", abs(list_XYSteps[0] + list_XYSteps[1]))
            
            x_i = 0
            y_i = 0
            
            #The number of iterations to check always sides the greater value
            if abs(list_XYSteps[0]) >= abs(list_XYSteps[1]):
                iteration = abs(list_XYSteps[0])
            elif abs(list_XYSteps[0]) < abs(list_XYSteps[1]):
                iteration = abs(list_XYSteps[1])
            
            for i in range(iteration):
                
                
                if i < abs(list_XYSteps[0] - x_offset): #Check if X has completed its steps
                    x_drv8825_step.on()
                    sleep(time_delay)
                    x_drv8825_step.off()
                    sleep(time_delay)
                    x_i += 1
                    print(f"Stepping X-axis motor {x_i}/{abs(list_XYSteps[0])}")
                
                if i < abs(list_XYSteps[1] - y_offset): #Check if Y has completed its steps
                    y_drv8825_step.on()
                    sleep(time_delay)
                    y_drv8825_step.off()
                    sleep(time_delay)
                    y_i += 1
                    print(f"Stepping Y-axis motor {y_i}/{abs(list_XYSteps[1])}")
                
                
                
            
            sleep(1) #A brief pause before disabling the motor, so that inertia is accounted for
            y_drv8825_en.on() #Disable the motor, may reduce holding torque but reduce power dissipation
            x_drv8825_en.on()
        print("Movement ", selected_xy, " complete")
        
        #Update gripper position
        
        if selected_xy == "X":
            gripper_posi[0] = coor_chosen_waste[0] #gripper x position
        elif selected_xy == "Y":
            gripper_posi[1] = coor_chosen_waste[1] #gripper y position
        elif selected_xy == "XY":
            gripper_posi[0] = coor_chosen_waste[0] #gripper x position
            gripper_posi[1] = coor_chosen_waste[1] #gripper y position
 
        print("\n")
        print("Gripper position updated [Arrival at waste coordinates]= ", gripper_posi)
    
    elif homing == True and tobin == None:
        #The core XY moves the gripper to home by turning the steppers until a limit switch is hit
        #MAY BE DEPRECATED FOR A SAFER OPTION, IN EVENT THAT THE LIMIT SWITCHES FAIL, THE
        #STEPPER MAY RAM AND STALL, CAUSING HIGHER CURRENT DRAW AND FORCE THE PROGRAM INTO INFINITE LOOP
        if selected_xy == "X":
            x_drv8825_en.off() #Turn on motor
            x_drv8825_dir.off() #ADJUST TO TURN IN DIRECTION WHICH HOME LIMIT SWITCH IS LOCATED


            while x_homingswitch.is_pressed == False:
                x_drv8825_step.on()
                sleep(time_delay)
                
                x_drv8825_step.off()
                sleep(time_delay)
                
                print("Stepping motor")
                
            sleep(1) #A brief pause before disabling the motor, so that inertia is accounted for
            x_drv8825_en.on() #Disable the motor, may reduce holding torque but reduce power dissipation

        elif selected_xy == "Y":
            y_drv8825_en.off() #Turn on motor
            y_drv8825_dir.off() #ADJUST TO TURN IN DIRECTION WHICH HOME LIMIT SWITCH IS LOCATED


            while y_homingswitch.is_pressed == False:
                y_drv8825_step.on()
                sleep(time_delay)
                
                y_drv8825_step.off()
                sleep(time_delay)
                
                print("Stepping motor")
                
            sleep(1) #A brief pause before disabling the motor, so that inertia is accounted for
            
            y_drv8825_en.value = 1 #Disable the motor, may reduce holding torque but reduce power dissipation


        
        print("Homing for ", selected_xy, " complete")
        
        if selected_xy == "X":
            gripper_posi[0] = 0 #gripper x position
        elif selected_xy == "Y":
            gripper_posi[1] = 0 #gripper y position
        
        print("\n")
        print("Gripper position updated [Homing]= ", gripper_posi)
    
    elif homing == False and tobin == 0: #CHANGE ToBin == 1 Incase direction is wrong
        y_drv8825_en.off() #Enable the motor
        y_drv8825_dir.value =  tobin #Set motor direction
        
        
        #SIMILAR TO LIMIT SWITCH, THERE IS AN OPPORTUNITY TO WRITE A SAFER ALGORITHM FOR THIS SECTION
        while ir_enc1.value == False:
                y_drv8825_step.on()
                sleep(time_delay)
                
                y_drv8825_step.off()
                sleep(time_delay)
                
                print("Stepping motor Indefinitely Enc1")
                
        #Update the Y position        
        gripper_posi[1] = ENC1_COOR #gripper y position
        
        print("\n")
        print("Gripper position updated [Homing]= ", gripper_posi)
        
        y_drv8825_en.on() #Turn the motor off
        
        
    elif homing == False and tobin == 1:   #CHANGE ToBin == 0 Incase direction is wrong
        y_drv8825_en.off() #Enable the motor
        y_drv8825_dir.value =  tobin #Set motor direction
        
        
        #SIMILAR TO LIMIT SWITCH, THERE IS AN OPPORTUNITY TO WRITE A SAFER ALGORITHM FOR THIS SECTION
        while ir_enc2.value == False:
                y_drv8825_step.on()
                sleep(time_delay)
                
                y_drv8825_step.off()
                sleep(time_delay)
                
                print("Stepping motor Indefinitely to Enc2")

        #Update the Y position        
        gripper_posi[1] = ENC2_COOR #gripper y position
        
        y_drv8825_en.on() #Turn the motor off


#IMPLEMENTATION##############################################################

#homingswitchestest()

# irencstest()



#Produce data to for the stepper motor to move
xsteps_toDesti, ysteps_toDesti = getshortestdist(gripper_posi ,typeposi_data, 20) #The steps needed in x direction to reach destination
xy_steps_toDesti = [xsteps_toDesti, ysteps_toDesti] #For use in simultaneous movement
print("\n\n")
print("Xsteps_toDesti= ", xsteps_toDesti) #For verification
dirX = int(xsteps_toDesti) >= 0 #get sign for direction to turn
print("dirX", dirX)
print("Direction dirX = Anticlockwise") if dirX == True else print("Direction dirX = Clockwise")
print("Ysteps_toDesti= ", ysteps_toDesti) #For verification
dirY = int(ysteps_toDesti) >= 0 #get sign for direction to turn
print("dirY", dirY)
print("Direction dirY = Anticlockwise") if dirY == True else print("Direction dirY = Clockwise")

dirXY = [dirX, dirY] #For use when direction is simultaneous
print("xy_steps_toDesti = ", xy_steps_toDesti)
print("dirXY = ", dirXY)

#NOTE: The direction can be inverted with not dirY for example
#drivedrv8825(xsteps_toDesti, dirX, "Full", "X", 0.0004)
#drivedrv8825(ysteps_toDesti, dirY, "Full", "Y", 0.0004) #(Number of steps, direction, physical microstep settings (wired), which motor, time delay between steps)
#drivedrv8825(2000, dirY, "Full", "X", 0.0004) #(Number of steps, direction, physical microstep settings (wired), which motor, time delay between steps)

#drivedrv8825(2000, dirY, "Full", "Y", 0.001) #Fixed steps but slower speed

#drivedrv8825(200, dirY, "Full", "Y", 0.001) #A full rotation with Y
#drivedrv8825(200, dirY, "Full", "X", 0.001) #A full rotation with X

#drivedrv8825(200, dirY, "Half", "Y", 0.001) #A full rotation under half step

#drivedrv8825(ysteps_toDesti, dirY, "Full", "Y", 0.0004, homing = True) #HOMING THE Y axis

#drivedrv8825(ysteps_toDesti, dirY, "Full", "Y", 0.0004, tobin = 0) #Move the Y-axis towards one encoder

#drivedrv8825(ysteps_toDesti, dirY, "Full", "Y", 0.0004, tobin = 1) #Move the Y-axis towards the other encoder

#drivedrv8825(0, dirY, "Full", "XY", 0.0004, list_DirXY = dirXY, list_XYSteps = xy_steps_toDesti) #Move the Y-axis towards the other encoder



drivedrv8825(0, dirY, "Full", "XY", 0.0004, list_DirXY = dirXY, list_XYSteps = [300, 300], invert_xDir = True, invert_yDir = True) #Direction inversion



sleep(5)
