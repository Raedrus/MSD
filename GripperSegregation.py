# Gripping cycle refers to:
# Object detection --> obtain number of objects and coordinates --> gripper sorting until no items remain

##TESTING PLAT STABILIZER


#################


import serial
from Serial_Pi_ESP32 import esp32_comms
from Serial_Pi_ESP32 import esp32_done

import CONST  # constant values only, coordinates and such

import ImgWasteData as imgD  # Image Data
import V33_XYMovementControls_XY as gan  # Gantry
import ZAxis as za

#import serial
#from Serial_Pi_ESP32 import esp32_comms

from gpiozero import Button

from time import sleep

print("Gripper Segregation")



# Variables##########################################
gripper_posi = [0, 0]  # Current gripper coordinates in steps

# intentional

# Class declarations#################################
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)

G_limit_pin = 13

G_limit_button = Button(G_limit_pin, pull_up=True)

####################################################





def home_XY():
    # Home the axis at the start and at the very end

    gan.drivedrv8825(0, 0, "Full", "X", 0.0004, homing=True)
    gan.drivedrv8825(0, 0, "Full", "Y", 0.0004, homing=True)
    
    #esp32_comms(ser, "G_OPEN")


# The 4 bins (General waste, metal, electronics, batteries)
# One's with gripping requirements: Metals (Aluminum can), electronics, batteries


def ToCoordZero():
    # The gripper goes to 0 coordinate of the camera frame

    # ASSUMING THIS ENCODER IS THE HOME POSITION ENCODER
    gan.drivedrv8825(0,
                 0,
                 "Full",
                 "Y",
                 0.0004,
                 tobin=0)  # Move the Y-axis towards encoder1

    gan.drivedrv8825(0, 0, "Full", "X", 0.0004, homing=True)

    gripper_posi[0] = 0
    gripper_posi[1] = 0



def Limited_G_Open():
	if  G_limit_button.is_pressed == True:
		sleep(0.3)
		esp32_comms(ser, "G_OPEN")
		
		
		while G_limit_button.is_pressed == True:
			pass
		
		sleep(0.3)
		esp32_comms(ser, "G_LIM")
		
		sleep(0.3)
		#esp32_done()

#Assumde bin positions:
#That Bin ABC are only bins gripper drops to, and are near the Y limit switch
#|  |  B |
#|A |----|
#|  |  C |
def ToBinA(waste_sz):
    
    
    ###
    #Process Description
    #1)Home X
    #2)To bin in Y
    #3)Y to Bin A
    #4)X to Position for Drop
    #5)Drop item based on size of item gripped
    #6)Home X
    
    ###
    
    # With assumption that
    #the item is already picked up
    # Take the item and drop them at Bin A

    # waste_sz in terms pixels detected from the camera, in type_posi array
    # For now, based on box area (Not foolproof for standing items)

    xDir = 0  # Placeholder values
    yDir = 0
    xloc = 800  # Placeholder value
    yloc = 1500 #Placeholder value
    
    # After moving to that location, xloc moves it above the correct bin
    # xDir has to be determined from checking the right way to turn the motor
    
    gan.drivedrv8825(0, 1, "Full", "X", 0.0004, homing=True)
    
    gan.drivedrv8825(0,0,"Full","Y",0.0004,tobin=1)  # Move the Y-axis towards encoder1
    


    #Move Y direction to the required bin
    gan.drivedrv8825(0,
                 1,
                 "Full",
                 "XY",
                 0.001,
                 list_DirXY=[0, yDir],
                 list_XYSteps=[0, yloc],
                 invert_xDir=True,
                 invert_yDir=True)  # Direction inversion
    

    # Move X towards the needed bin
    gan.drivedrv8825(0,
                 0,
                 "Full",
                 "XY",
                 0.001,
                 list_DirXY=[xDir, 1],
                 list_XYSteps=[xloc, 0],
                 invert_xDir=True,
                 invert_yDir=True)  # Direction inversion

    # Use a specific type of grip depending on size

    if waste_sz <= float(CONST.SMALL_SIZE):
        vacuum_release_drop()
        sleep(0.5)
        print("Vacuum Drop")
        
        
        sleep(1)
    else:
        finger_release_drop()
        sleep(0.5)
        print("Finger Drop")

    # Move x back to it's limit switch to recalibrate
    gan.drivedrv8825(0, 1, "Full", "X", 0.0004, homing=True)

    print("Waste to Bin A was Attempted")

    # Return the current position of the gripper after completion of the operation
    # x = 0, because it was homed for calibration
    return [0, 0]


def ToBinB(waste_sz):
    
    
    ###
    #Process Description
    #1)Home X
    #2)To bin in Y
    #3)Y to Bin A
    #4)X to Position for Drop
    #5)Drop item based on size of item gripped
    #6)Home X
    
    ###
    
    # With assumption that
    #the item is already picked up
    # Take the item and drop them at Bin A

    # waste_sz in terms pixels detected from the camera, in type_posi array
    # For now, based on box area (Not foolproof for standing items)

    xDir = 0  # Placeholder values
    yDir = 0
    xloc = 400  # Placeholder value
    yloc = 0 #Placeholder value
    
    # After moving to that location, xloc moves it above the correct bin
    # xDir has to be determined from checking the right way to turn the motor
    
    gan.drivedrv8825(0, 1, "Full", "X", 0.0004, homing=True)
    
    gan.drivedrv8825(0,0,"Full","Y",0.0004,tobin=1)  # Move the Y-axis towards encoder1
    


    #Move Y direction to the required bin
    gan.drivedrv8825(0,
                 1,
                 "Full",
                 "XY",
                 0.001,
                 list_DirXY=[xDir, yDir],
                 list_XYSteps=[0, yloc],
                 invert_xDir=True,
                 invert_yDir=True)  # Direction inversion



    # Move X towards the needed bin
    gan.drivedrv8825(0,
                 0,
                 "Full",
                 "XY",
                 0.001,
                 list_DirXY=[xDir, 1],
                 list_XYSteps=[xloc, 0],
                 invert_xDir=True,
                 invert_yDir=True)  # Direction inversion

    # Use a specific type of grip depending on size

    if waste_sz <= float(CONST.SMALL_SIZE):
        vacuum_release_drop()
        sleep(1)
    else:
        finger_release_drop()
        sleep(1)

    # Move x back to it's limit switch to recalibrate
    gan.drivedrv8825(0, 1, "Full", "X", 0.0004, homing=True)

    print("Waste to Bin A was Attempted")

    # Return the current position of the gripper after completion of the operation
    # x = 0, because it was homed for calibration
    return [0, 0]

def ToBinC(waste_sz):
        
    ###
    #Process Description
    #1)Home X
    #2)To bin in Y
    #3)Y to Bin A
    #4)X to Position for Drop
    #5)Drop item based on size of item gripped
    #6)Home X
    
    ###
    
    # With assumption that
    #the item is already picked up
    # Take the item and drop them at Bin A

    # waste_sz in terms pixels detected from the camera, in type_posi array
    # For now, based on box area (Not foolproof for standing items)

    xDir = 0  # Placeholder values
    yDir = 0
    xloc = 2200  # Placeholder value
    yloc = 0 #Placeholder value
    
    # After moving to that location, xloc moves it above the correct bin
    # xDir has to be determined from checking the right way to turn the motor
    
    gan.drivedrv8825(0, 1, "Full", "X", 0.0004, homing=True)
    
    gan.drivedrv8825(0,0,"Full","Y",0.0004,tobin=1)  # Move the Y-axis towards encoder1
    


    #Move Y direction to the required bin
    gan.drivedrv8825(0,
                 1,
                 "Full",
                 "XY",
                 0.001,
                 list_DirXY=[xDir, yDir],
                 list_XYSteps=[0, yloc],
                 invert_xDir=True,
                 invert_yDir=True)  # Direction inversion



    # Move X towards the needed bin
    gan.drivedrv8825(0,
                 0,
                 "Full",
                 "XY",
                 0.001,
                 list_DirXY=[xDir, 1],
                 list_XYSteps=[xloc, 0],
                 invert_xDir=True,
                 invert_yDir=True)  # Direction inversion

    # Use a specific type of grip depending on size

    if float(waste_sz) <= float(CONST.SMALL_SIZE):
        vacuum_release_drop()
        sleep(1)
    else:
        finger_release_drop()
        sleep(1)

    # Move x back to it's limit switch to recalibrate
    gan.drivedrv8825(0, 1, "Full", "X", 0.0004, homing=True)

    print("Waste to Bin A was Attempted")

    # Return the current position of the gripper after completion of the operation
    # x = 0, because it was homed for calibration
    return [0, 0]


# DROPS
# There are two kinds of drops, the gripper drop or vacuum drop
def finger_release_drop():
    #1) Lower the gripper
    #2) Open te fingers to drop the waste
    #3) Elevate the gripper back up
    
    sleep(0.2)
    # lower the z axis
    za.full_lower_gripper()

    sleep(0.5)
    
    # open the gripper fingers
    Limited_G_Open()

    sleep(2)
    # Elevate the gripper back upwards
    za.full_ele_gripper()


def vacuum_release_drop():
    #Lower the gripper
    #Turn on the vacuum pump
    #Elevate the gripper

    sleep(0.2)
    # lower the z axis
    za.full_lower_gripper()

    sleep(1)
    
    # OFF the vacuum pump
    esp32_comms(ser, "VAC_OFF")

    sleep(0.2)
    # Elevate the gripper back upwards
    za.full_ele_gripper()

def QRCapturePosition():
	gan.drivedrv8825(825,
                 1,
                 "Full",
                 "X",
                 0.0004,
                 )
	gan.drivedrv8825(2140,
                 0,
                 "Full",
                 "Y",
                 0.0004,
                 )
                 
def GripperToWaste(type_posi):
	print("GS_waste")
	home_XY()
	ToCoordZero()
	waste_sz = 0 #Setting default for value of no objects detected
	
	if len(type_posi[0]) > 0:
		print("Detected Items: ",  len(type_posi[0]))
		print(len(type_posi[0]))
		

		
		xy_steps_toDesti, waste_sz = gan.getshortestdist([0,0], type_posi, 30/400) #Last parameter is distance per pixel value
		
	
	else:
		print("No items detected")
		
	
	
	if xy_steps_toDesti[0] != 0 and xy_steps_toDesti[1] != 0:
		
	
		# Obtaining turning directions
		dirX = int(xy_steps_toDesti[0]) >= 0
		dirY = int(xy_steps_toDesti[1]) >= 0
		dirXY = [dirX, dirY]
			###
		
		print("dirX: ", dirXY[0])
		print("dirY: ", dirXY[1])
		
		
		print("xy_steps_toDesti [x]: ", xy_steps_toDesti[0])
		print("xy_steps_toDesti [y]: ", xy_steps_toDesti[1])
		
		
		sleep(2)
		#Check if coordinates are legal before moving
		#proceed if equal
		
		x_bound =  3000
		y_bound = 3000
		
		if (30 < abs(xy_steps_toDesti[0]) < x_bound) and (abs(xy_steps_toDesti[1]) < y_bound):
			if dirX == False:
				#For X gripping near the edge
				xy_steps_toDesti[0] = 0
				print("Bound X Adjusted")
			
			if dirY == False:
				xy_steps_toDesti[1] = 0
				print("Bound Y Adjusted")
			# Move the gripper to the nearest waste
			gan.drivedrv8825(0, dirXY, "Full","XY",0.001,list_DirXY=dirXY,list_XYSteps=xy_steps_toDesti,invert_xDir=False,invert_yDir=True)
			
		else:
			print("WARNING: Coordinates exceed bounds of the tray, ignoring movement command")
			
	
	

	return waste_sz

##########################################################################################


def main():
    
	print("main")
	sleep(5)
    #Initialize the gripper
	za.full_ele_gripper()
	Limited_G_Open()
	home_XY()

    # Detect the image, return the required position and item type data
    # and box area

	ToCoordZero()

	grip_attempt = 0
	
	ToCoordZero()
	QRCapturePosition()
	origin_xy=imgD.GetPlatOrigin()
	sleep(1)
	home_XY()
	type_posi = imgD.GetMVData(imgD.TakePicture(), origin_xy)
	
	
	print(len(type_posi))
	while len(type_posi[0]) > 0:
		
		prev_detected = len(type_posi[0])
		
		print("Gripper to waste")
		waste_sz = GripperToWaste(type_posi)
		
		
		#DECIDE ON A GRIPPING METHOD [LEFT WITH GRIPPER ONLY]
		#Use the vacuum pump on small items
		
		waste_sz = 10**23
		

			
		
		# Open the gripper fingers
		
		print("FINGER GRIPPING")
		
		
		Limited_G_Open()

		za.full_lower_gripper()
		
		# close fingers
		sleep(0.3)
		esp32_comms(ser, "G_CLOSE")
		esp32_done()
		
		sleep(0.3)
		za.full_ele_gripper()
		
		grip_attempt += 1
		
		match type_posi[0]:
			# Providing size of the waste as input parameter
			case "B":
				ToBinA(float(type_posi[3]))
			case "E":
				ToBinB(float(type_posi[3]))
			case "M":
				ToBinC(float(type_posi[3]))


		

		#Restart the process, the dustbin takes another look at what is left behind
		
		print("The number of attempted grip(s): ", grip_attempt)
		
		home_XY()
		sleep(0.3)
		type_posi = imgD.GetMVData(imgD.TakePicture(), origin_xy)
		
		next_detected = len(type_posi[0])
		
        #if next_detected < prev_detected:
			#print("Decrement detected")
        #IOT INSERTS HERE
		#CONDITION: If the number of detected waste has decremented, there has been a successful grip
		
#esp32_comms(ser, "EMAG_OFF")

#esp32_comms(ser, "LID_OPEN")
#sleep(3)
#esp32_comms(ser, "LID_CLOSE")

 
#home_XY()
#ToCoordZero()
#ToBinA(50)
#ToBinB(50)
#ToBinC(50)

#finger_release_drop()
#vacuum_release_drop()

main()
#ToBinC(50)

#ToBinB(50)

#home_XY()

#ToCoordZero()



#GripperToWaste(type_posi)
#za.full_ele_gripper()
#ToBinB(50)



#GripperToWaste(type_posi)

#za.partial_lower_gripper(5900)
#za.full_lower_gripper()

#esp32_comms(ser, "G_CLOSE")
#esp32_comms(ser, "G_CLOSE")
#Limited_G_Open()

print("Grip Segregation Program Ended")
