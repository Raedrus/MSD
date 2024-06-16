import ultralytics
import numpy as np
import cv2
import time
from gpiozero import LED
from gpiozero import DistanceSensor
from gpiozero import Button
from gpiozero import Servo
from gpiozero import DigitalOutputDevice
import time
from time import sleep
import serial

import sys      # For testing system quits
import os       # For testing system quits
import psutil   # For testing system quits

# Function file import
from WasteSorting import sortingcycle
from Serial_Pi_ESP32 import esp32_comms

current_system_pid = os.getpid()
ThisSystem = psutil.Process(current_system_pid)


# GPIO Assignments################################################################
pin_green_led = 20
pin_red_led = 21

pin_ult_echo = 4
pin_ult_trigger = 17

pin_start = 6
pin_Estop = 5

pin_lid_servo = 18
pin_gate_servo = 19

pin_transistor_magnet = 16


# Setup #############################################
green_led = LED(pin_green_led) # Change number to assign GPIO number (BCM layout)
red_led = LED(pin_red_led) # Change number to assign GPIO number (BCM layout)


# Ultrasonic Sensor Assignment, threshold dist settings in meters
ult_sensor = DistanceSensor(echo=pin_ult_echo, trigger=pin_ult_trigger)


# Button Assignment
# In the prototype, the buttons are set to pull down
start_button = Button(pin_start, pull_up=False)
Estop_button = Button(pin_Estop, pull_up=False)


# Servo Assignment#
lid_servo = Servo(pin_lid_servo)
gate_servo = Servo(pin_gate_servo)

# initiate arrays

# initiate interrupt for E-stop

# initiate serial handshake with ESP32 (TX,RX)
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1) #9600 is baud rate(must be same with that of NodeMCU)
ser.flush()
ser.reset_input_buffer()
print("Serial OK")

# initiate webcam
webcamera = cv2.VideoCapture(0, cv2.CAP_DSHOW)


def start_loop():
    lid_servo.min()  # Ensure the gate is closed on start
    magnet_cluster.off()    # Ensure electromagnets are off
    green_led.on()  # Turn on the LED to indicate the dustbin and raspi is powered
    red_led.off()

    try:

        while True:

            humanPres(0.3,
                      5)  # Parameter specifies human detection range in meters, second parameter specifies timeout value before it autosorts

    except KeyboardInterrupt:
        print("Keybard Interrupt!")
    except:
        pass
    finally:

        # Used to turn off the LEDs for the prototype while testing
        green_led.close()
        red_led.close()
        sys.exit()


def humanPres(detect_range,lid_timeout):
    PrintUltSenseDist() #For debugging use

    ult_distance = float(ult_sensor.distance)

    if ult_distance < float(detect_range):
        t0 = time.time()

        #open the lid
        lid_servo.value = 0.5 #Change value of pulsewidth to adjust position of servo

        while True:


            t1 = time.time()
            if start_button.is_pressed:
                #Begin the sorting cycle

            #PLACEHOLDER SORTING CYCLE
                print("ButtonTrig: The simulated sorting cycle begins") #For Debugging
                SortingCycle()

                #Reset the timer
                break

            if t1-t0 > lid_timeout:
                print("Timeout, attempt to start the process")
                #PLACEHOLDER SORTING CYCLE
                print("Timeout: The simulated sorting cycle begins") #For Debugging
                SortingCycle()
                #Reset the timer
                break

    elif ult_distance > detect_range:
        #Close the lid
        lid_servo.min() #Change value of pulsewidth to adjust position of servo
        sleep(0.4)


def SortingCycle():
    return