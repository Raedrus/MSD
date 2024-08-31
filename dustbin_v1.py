import ultralytics
import numpy as np
import cv2
import time
from gpiozero import LED
from gpiozero import DistanceSensor
from gpiozero import Button
from gpiozero import Servo
from gpiozero import DigitalOutputDevice
from Serial_Pi_ESP32 import esp32_comms

import time
from time import sleep
import serial

import sys  # For testing system quits
import os  # For testing system quits
import psutil  # For testing system quits

# Function file import
from WasteSorting import sortingcycle
from Serial_Pi_ESP32 import esp32_comms
import GripperSegregation as GS
current_system_pid = os.getpid()
ThisSystem = psutil.Process(current_system_pid)

################## GPIO Assignments################################################################
# Ultrasonic Sensor
pin_ult_echo = 6
pin_ult_trigger = 5

#Start Stop
pin_start = 17
pin_Estop = 13

#Limit Switches
pin_Xhome = 11
pin_Yhome = 9
pin_Zhome = 25
pin_bin1presence = 8
pin_bin2presence = 7
pin_bin3presence = 12

#Infrared Sensor
pin_Platorigin = 22
pin_bin = 10


#Stepper Motors
pin_Xen = 16
pin_Xstep = 20
pin_Xdir = 21

pin_Yen = 18
pin_Ystep = 23
pin_Ydir = 24

pin_Zen = 2
pin_Zstep = 3
pin_Zdir = 4

# Setup #############################################


# Ultrasonic Sensor Assignment, threshold dist settings in meters
ult_sensor = DistanceSensor(echo=pin_ult_echo, trigger=pin_ult_trigger)

# Button Assignment
# In the prototype, the buttons are set to pull down
start_button = Button(pin_start, pull_up=True)
Estop_button = Button(pin_Estop, pull_up=True)

# Limit switch and IR sensor Assignment



# initiate arrays

# initiate interrupt for E-stop

# initiate serial handshake with ESP32 (TX,RX)
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
ser.flush()
ser.reset_input_buffer()
print("Serial OK")

# initiate webcam
webcamera = cv2.VideoCapture(0, cv2.CAP_DSHOW)


def start_loop():
    # Ensure electromagnets are off
    esp32_comms(ser, "EMAGNET_OFF")

    esp32_comms(ser, "GLED_ON")
    esp32_comms(ser, "RLED_OFF")


    try:

        while True:
            humanPres(0.3, 5)  # Parameter specifies human detection range in meters,
            # second parameter specifies timeout value before it autosorts

    except KeyboardInterrupt:
        print("Keybard Interrupt!")
    except:
        pass
    finally:

        # Used to turn off the LEDs for the prototype while testing
        esp32_comms(ser, "GLED_OFF")
        esp32_comms(ser, "RLED_OFF")
        green_led.close()
        red_led.close()
        sys.exit()


def humanPres(detect_range, lid_timeout):
    PrintUltSenseDist()  # For debugging use

    ult_distance = float(ult_sensor.distance)

    if ult_distance < float(detect_range):
        t0 = time.time()

        # open the lid
        esp32_comms(ser, "LID_OPEN")
        
        while True:

            t1 = time.time()
            if start_button.is_pressed:
                # Begin the sorting cycle

                # PLACEHOLDER SORTING CYCLE
                print("ButtonTrig: The simulated sorting cycle begins")  # For Debugging
                SortingCycle()

                # Reset the timer
                break

            if t1 - t0 > lid_timeout:
                print("Timeout, attempt to start the process")
                # PLACEHOLDER SORTING CYCLE
                print("Timeout: The simulated sorting cycle begins")  # For Debugging
                SortingCycle()
                # Reset the timer
                break

    elif ult_distance > detect_range:
        # Close the lid
        esp32_comms(ser, "LID_CLOSE")
        sleep(0.4)


def SortingCycle():
    #Gate Sequence
    esp32_comms(ser, "LID_CLOSE")
    sleep(0.5)
    esp32_comms(ser, "EMAGNET_ON")
    sleep(1)
    esp32_comms(ser, "GATE_OPEN")
    sleep(5)
    esp32_comms(ser, "GATE_CLOSE")
    sleep(1)
    esp32_comms(ser, "EMAGNET_OFF")

    GS.main()

    sleep(1)
    #esp32_comms(ser, "EMAGNET_OFF") #REPLACE with string to tilt servo platform
    sleep(2)

    
    esp32_comms(ser, "GATE_OPEN")
    sleep(5)
    esp32_comms(ser, "GATE_CLOSE")
    
    GS.main()

    sleep(1)
    #esp32_comms(ser, "EMAGNET_OFF") #REPLACE with string to tilt servo platform
    sleep(2)
    
    return
