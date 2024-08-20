#The Z-axis system codes

####################
    #WARNING: The gripper fingers should open before descending to prevent collision
####################


#Note, there should be 2 distinctions of levels, z axis at its lowest level allows for vacuum gripping,
#The other value of partial descent allows it to enter finger gripping range

from gpiozero import DigitalOutputDevice
from gpiozero import PWMOutputDevice
from gpiozero import Button
from time import sleep


#Predefined Values############################################
desired_displacement_partial = 5 #The displacement from lowest position for the gripper finger grip objects in cm
travel_length = 20 #Value in cm from top limit switch to lower limit switch

pl_desc =200 #Partial descent, The gripper stepper takes this amount of steps to displace itself down into gripping range


#Pin Assignments###############################################
#Limit switches of upper and lower limit
z_up_lim_pin = 25
z_lowlim_pin = 26 #A chosen pin 26 that seems unoccupied on whatsapp schematic (15 Aug, SCH_Raspberry Pi_1-Version 2_2024-08-15

#XY Gantry Motors Drivers
pin_z_drv8825_en = 2 
pin_z_drv8825_step = 3
pin_z_drv8825_dir = 4 #1 for clockwise, 0 for counter-clockwise


#Declaration of classes#########################################
#Setup z axis stepper
z_drv8825_relax = DigitalOutputDevice(pin_z_drv8825_en) 
z_drv8825_step = PWMOutputDevice(pin_z_drv8825_step, frequency = 6000)
z_drv8825_dir = DigitalOutputDevice(pin_z_drv8825_dir)


#Setup Limit Switches
ZUP_lim = Button(z_up_lim_pin, pull_up = True)
ZLOW_lim = Button(z_lowlim_pin, pull_up = True)


######################################################################
#Temporal Data
cur_ele = 0 #The current position of the gripper's z position
steps_axis_length = 0 #Represents the number of steps to move from top of gripper to the bottom
######################################################################

def full_ele_gripper():
    #Restore gripper to upmost position for coordinate Accuracy and safety
    
    z_drv8825_relax.off()
    
    #Set Directions
    z_drv8825_dir.off() 
    
    while ZUP_lim.is_pressed != True:
        z_drv8825_step.blink(background = False,  n= 20, on_time =0.001, off_time = 0.0004)
        print("Elevating Gripper to Z Home")
        
    cur_ele = 0 #Home position is tuned as position 0
    print("Z axis homed")

    z_drv8825_relax.on()


def count_steps_of_axis(desired_displacement_partial):
    #Optional [For use of finding the total number of steps that makes up the z axis]
    #Allows an automated way count length of z-axis in terms of number of steps
    
    step_ct = 0 #step_count
    #full_ele_gripper() #Get to top most position before counting

    
    sleep(1)
    
    z_drv8825_relax.off()
    z_drv8825_dir.on()

    #Start descending the gripper
    while ZLOW_lim.is_pressed != True:
        z_drv8825_step.blink(background = False,  n= 20, on_time =0.001, off_time = 0.0004)
        print("Descending Gripper All the way down [MEASURING]")
        step_ct += 1*20
        
    print(f"It takes {steps_axis_length} to reach the bottom of the gripper")
    #This info MAY turn out helpful for an estimate number of turns needed for a partial descent,
    #simply: z-axis_length/no_steps --> distance per step
    dist_per_step_cm = travel_length/step_ct
    req_steps_displacement = desired_displacement_partial/dist_per_step_cm #for partial descent
    
    print("No steps to fully descend: ", step_ct)
    
    step_req = int((step_ct - req_steps_displacement))
    print("Step requirement for partial descent: ", step_req)
    
    sleep(0.8)
    
    print("Measurement complete, returning to the top")
    full_ele_gripper()
    
    z_drv8825_relax.on()
    
    return  step_req#Return the value for partial descent in steps
    
    

def partial_lower_gripper(pl_desc):
    
    z_drv8825_relax.off()
    
    #Adjust direction
    z_drv8825_dir.on() 
    
    #Partially descend the gripper
    z_drv8825_step.blink(background = False,  n= pl_desc, on_time =0.001, off_time = 0.0004)
    
    print("Partial lower completed")
    z_drv8825_relax.on()


def full_lower_gripper():
    #Set the directions
    z_drv8825_relax.off() 
    
    #Gripper goes all the way down to perform a vacuum grip
    while ZLOW_lim.is_pressed != True:
        z_drv8825_step.blink(background = False,  n= 20, on_time =0.001, off_time = 0.0004)
        print("Descending Gripper All the way down [BALLOON GRIPPING]")
        
    z_drv8825_relax.on()


# full_lower_gripper()
# 
# print("z operation complete")
# sleep(3)
