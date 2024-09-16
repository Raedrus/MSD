import ultralytics
import numpy as np
import cv2
import time
from time import sleep
from gpiozero import LED
from gpiozero import DistanceSensor
from gpiozero import Button
from gpiozero import Servo
from gpiozero import DigitalOutputDevice


import serial

import sys  # For testing system quits
import os  # For testing system quits
import psutil  # For testing system quits

# for testing wifi
import platform
def is_wifi_connected():
    if platform.system() == "Windows":
        response = os.system("ping -n 1 google.com")
    else:
        response = os.system("ping -c 1 google.com")
    return response == 0

if is_wifi_connected():
    print("Wi-Fi is connected.")
else:
    print("Wi-Fi is not connected.")
    
# Function file import
#For IoT purpose and local storage
import blynk as IoTB
import api_google as google
import local_save 
from local_save import waste_counts


#from WasteSorting import sortingcycle
from Serial_Pi_ESP32 import esp32_comms
from Serial_Pi_ESP32 import esp32_done
import Gripper_Segregation as GS

current_system_pid = os.getpid()
ThisSystem = psutil.Process(current_system_pid)

#Platform Servo
##TESTING PLAT STABILIZER
from gpiozero import AngularServo
pin_plat_servo = 27
plat_servo=AngularServo(pin_plat_servo, min_pulse_width=0.0005, max_pulse_width=0.0025)

#Initialize at home position
plat_servo.angle = 0
plat_servo.angle= None
plat_servo.angle = 10
print("10")
time.sleep(4)
plat_servo.angle = 20
print("20")
time.sleep(4)
#plat_servo.angle = None
while True:    
    print("Hi")



################## GPIO Assignments################################################################
# Ultrasonic Sensor
pin_ult_echo = 26
pin_ult_trigger = 4

# Start Stop
pin_start = 17
pin_Estop = 13

# Limit Switches
pin_Xhome = 11
pin_Yhome = 9
pin_Zhome = 25
pin_binpresence = 19



# Infrared Sensor
pin_Platorigin = 22
pin_bin = 10

# Stepper Motors
pin_Zen = 2
pin_Zstep = 3
pin_Zdir = 4

pin_Xen = 16
pin_Xstep = 20
pin_Xdir = 21

pin_Yen = 18
pin_Ystep = 23
pin_Ydir = 24

# Setup #############################################


# Ultrasonic Sensor Assignment, threshold dist settings in meters
ult_sensor = DistanceSensor(echo=pin_ult_echo, trigger=pin_ult_trigger)

# Button Assignment
# In the prototype, the buttons are set to pull up
start_button = Button(pin_start, pull_up=True)
# Estop_button = Button(pin_Estop, pull_up=True)

binpresence = Button(pin_binpresence, pull_up = False)

# Limit switch and IR sensor Assignment


# initiate arrays


    


# initiate serial handshake with ESP32 (TX,RX)
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
ser.flush()
ser.reset_input_buffer()
print("Serial OK")

# initiate webcam
#webcamera = cv2.VideoCapture(0)

###############################
def shut_system():
    print("Emergency stop has been triggered, attempting system shutdown...")
    
    #Change LED indications
    LED_indicators(1, 1)
    
    
    sys.exit()

# initiate interrupt for E-stop

#Estop_button.when_pressed = shut_system
################################################

def LED_indicators(GLED, RLED, GBlink = False, RBlink = False):
    #Green LED controls = GLED, int 1 or 0
    #Red LED controls = RLED, int 1 or 0
    
    if GLED == 1:
        esp32_comms(ser, "GLED_ON")
    elif GLED == 0:
        esp32_comms(ser, "GLED_OFF")
    if RLED  == 1:
        esp32_comms(ser, "RLED_ON")
    elif RLED == 0:
        esp32_comms(ser, "RLED_OFF")
    
    
    if GBlink == True:
        #Blink the LED
        
        for _ in range(3):
            esp32_comms(ser, "GLED_ON")
            sleep(0.2)
            esp32_comms(ser, "GLED_OFF")
        
        #Restore the LED to ON
        esp32_comms(ser, "GLED_ON")
    
    elif RBlink == True:
        for _ in range(3):
            esp32_comms(ser, "RLED_ON")
            sleep(0.2)
            esp32_comms(ser, "RLED_OFF")
        
        #Restore the LED to ON
        esp32_comms(ser, "RLED_ON")
    

def start_loop():
    
    esp32_comms(ser, "LID_OPEN")
    esp32_done()
    # Ensure electromagnets are off
    
    esp32_comms(ser, "EMAG_OFF")
    esp32_done()
    
    esp32_comms(ser, "LID_CLOSE")
    esp32_done()
    
    esp32_comms(ser, "GATE_CLOSE")
    esp32_done()
    
    print("INITIALIZED")
    if is_wifi_connected():
        wifi_flag=1
        
    while True:
        if binpresence.is_pressed == False:
            print("Bin Absence Warning")
            event = "Bin_Unavailable"
            IoTB.writeIoT_Event(event)
            #LED_indicators(0, 1)
        
        if wifi_flag:
            print("Checking Blynk Reset...")
            #######################################################################################################################################
            ############# comment here when not necessary #############################################################################################
            ##############################################################################################################################################
            if IoTB.readIoT("V0") == 1:
                print("Clearing rubbish quantity")
                local_save.reset()
                event = "Reset"
                IoTB.writeIoT_Event(event)
                google.API_update(waste_counts['e_device'], waste_counts['general_waste'], waste_counts['battery'], waste_counts['metal'], event)
                
                
            
            
        else:
            #LED_indicators(1, 0)
                        
            print("Checking for humans")
            
            humanPres(0.3, 16)  # Parameter specifies human detection range in meters,
                # second parameter specifies timeout value before it closes
                






def humanPres(detect_range, lid_timeout):

    

    ult_distance = float(ult_sensor.distance)

    print("Utrasonic Dist: ", ult_distance)

    if ult_distance < float(detect_range):
        t0 = time.time()

        # open the lid
        sleep(0.3)
        esp32_comms(ser, "LID_OPEN")
        esp32_done()
        sleep(0.3)
        esp32_comms(ser, "EMAG_ON")
        esp32_done()
        #LED_indicators(1, 0, GBlink = True)

        while True:

            t1 = time.time()
            if start_button.is_pressed:
                # Begin the sorting cycle

                print("ButtonTrig: The  sorting cycle begins")  # For Debugging
                SortingCycle()
                
                
                # Reset the timer
                break

            if t1 - t0 > lid_timeout:
                #print("Timeout, attempt to start the process")
                #print("Timeout: The sorting cycle begins")  # For Debugging
                #SortingCycle()
                # Reset the timer
                print("Timeout")
                sleep(0.3)
                esp32_comms(ser, "LID_CLOSE")
                esp32_done()
                break

    elif ult_distance > detect_range:
        pass
        
        # Close the lid
        #esp32_comms(ser, "LID_CLOSE")
        #sleep(0.4)


def MetalBinTilt():

    plat_servo.angle = 16
    sleep(0.7)
    plat_servo.angle = 20
    sleep(1)
    plat_servo.angle = 0
    plat_servo.angle= None
    waste_counts['metal'] += 1
    IoTB.writeIoT("v3",str(waste_counts['metal']))
    local_save.update_values(waste_counts)
    
def GenBinTilt():
    plat_servo.angle = -16
    sleep(0.7)
    plat_servo.angle = -20
    sleep(1)
    plat_servo.angle = 0
    plat_servo.angle= None
    waste_counts['general_waste'] += 1
    IoTB.writeIoT("v4",str(waste_counts['general_waste']))
    local_save.update_values(waste_counts)

def SortingCycle():
    # Gate Sequence
    esp32_comms(ser, "LID_CLOSE")
    esp32_done()
    sleep(0.3)
    esp32_comms(ser, "GATE_OPEN")
    sleep(2)
    esp32_done()
    
    esp32_comms(ser, "GATE_CLOSE")
    sleep(0.3)
    esp32_done()
    esp32_comms(ser, "EMAG_OFF")
    esp32_done()



    #1st Sortation Cycle
    LED_indicators(1, 0, RBlink = True)
    GS.main()
    sleep(0.5)
    
    #First sortation cycle ends with GEN waste being tilted to the other platform
    GenBinTilt()
    
    
    

    #Platoform servo is connected to Pi Side
    #First sortation cycle ends with GENERAL waste bring tilted to one platform
    
    
    #2nd Sortation Cycle
    sleep(2.5)
    esp32_comms(ser, "GATE_OPEN")
    esp32_done()
    sleep(1)
    esp32_comms(ser, "GATE_CLOSE")
    esp32_done()
    
    GS.main()
    
    sleep(0.5)
    #Second
    MetalBinTilt()
    google.API_update(waste_counts['e_device'], waste_counts['general_waste'], waste_counts['battery'], waste_counts['metal'], "-")
    
    return




#Remove lines below?
#if __name__ == "__main__":
       # start_loop()
        #return




#The main program


#GS.GripperToWaste()



#start_loop()
