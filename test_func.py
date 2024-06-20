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

import sys  # For testing system quits
import os  # For testing system quits
import psutil  # For testing system quits


current_system_pid = os.getpid()
ThisSystem = psutil.Process(current_system_pid)

# GPIO Assignments################################################################
pin_green_led = 20
pin_red_led = 21

pin_ult_echo = 4
pin_ult_trigger = 17

pin_start = 6
pin_Estop = 5

pin_transistor_magnet = 16

pin_plat_servo = 27

# Setup #############################################
green_led = LED(pin_green_led)  # Change number to assign GPIO number (BCM layout)
red_led = LED(pin_red_led)  # Change number to assign GPIO number (BCM layout)


plat_servo = Servo(pin_plat_servo) 

# Ultrasonic Sensor Assignment, threshold dist settings in meters
ult_sensor = DistanceSensor(echo=pin_ult_echo, trigger=pin_ult_trigger)

# Button Assignment
# In the prototype, the buttons are set to pull down
start_button = Button(pin_start, pull_up=True)
Estop_button = Button(pin_Estop, pull_up=True)

# Limit switch and IR sensor Assignment

# Electromagnet Assignment
magnet_cluster = DigitalOutputDevice(pin_transistor_magnet)


# Configure the serial connection
ser = serial.Serial(
    port='/dev/ttyAMA0',  # Replace with your serial port
    baudrate=115200,
    timeout=1
)
ser.flush()
ser.reset_input_buffer()
print("Serial with ESP32 OK\n")


def send_command(command):
    ser.write((command + '\n').encode('utf-8'))
    time.sleep(0.1)
    #ser.flush()
    response = ser.readline().decode('utf-8').strip()
    return response


def send_position(position):
    ser.write((str(position) + '\n').encode())
    time.sleep(0.1)
    #ser.flush()
    response = ser.readline().decode('utf-8').strip()
    #ser.reset_input_buffer()
    return response


# Call this function to test the ultrasonic sensor. If the 4 printed values
# are reasonable, the sensor is working. Else, check GPIO assignment,
# check the wiring, ensure 5V is supplied to Vcc pin

def esp_com(command):
    response = send_command(command)
    print("Response from ESP32:", response)

    if command in ["EMAGNET", "LED", "GLED", "RLED"]:
        # Wait for completion message
        print("Im in loop")
        while True:
            response = ser.readline().decode('utf-8').strip()
            if response == "Check Done":
                print("Test completed.")
                break
            elif response:
                print("ESP32:", response)

    elif command in ["LID", "GATE"]:
        print("Im in loop")
        while True:
            
            position = int(input("Input Position: ").strip())
            if 0 <= position <= 100:
                response = send_position(position)
                print("Response from ESP32:", response)
                if "info_servo variable string is:" in response:
                    break
                else:
                    print("Failed to set position. Try again.")
            else:
                print("Position out of range. Enter a value between 0 and 100.")
            

        while True:
            response = ser.readline().decode('utf-8').strip()
            if response == "Check Done":
                print("Test completed.")
                break
            elif response:
                print("ESP32:", response)


def UltraTest():
    for i in range(4):
        print('Distance: ', ult_sensor.distance * 100)
        sleep(1)


# # For debugging purposes
# # Show the distance measured by the ultrasonic sensor
# def PrintUltSenseDist():
#     print("Detected distance:", float(round(ult_sensor.distance, 3)), "System in Sensing Mode")
#     sleep(0.2)


# Button Test functions print a message when the button is pressed
# Physical button configuration may be pulled up or pulled down!
def ButtonTest():
    print("Press either button...\n")
    while True:
        if start_button.is_pressed:
            print("Start button is pressed")
            sleep(1)
            break
        elif Estop_button.is_pressed:
            print("Emergency Stop button is pressed")
            sleep(1)
            break

def plat_servoTest():
        print('Platform servo is initiated')
        angle = input("Enter minmidmax or angle degree (0-1): ").strip()

        if angle.upper() == "MINMIDMAX":
            plat_servo.min()
            print('Platform at min angle')
            sleep(2)
            plat_servo.mid()
            print('Platform at mid angle')
            sleep(2)
            plat_servo.max()
            print('Platform at max angle')
            sleep(2)
            print('Going back to min angle')
            plat_servo.min()
        else:
            print("Platform going to angle: " + angle)
            plat_servo.value = angle
            sleep(2)
    
def test_loop():
    command = "Test"
    response = send_command(command)
    print(response)
    while True:
        command = input("Enter test command or 'exit' to quit: ").strip()
        command = command.upper()
        if command.lower() == 'exit':
            print("Exiting...")
            break

        elif command in ["EMAGNET", "LED", "RLED", "GLED", "LID", "GATE"]:
            esp_com(command)
            
        elif command == "ULTRASONIC":
            UltraTest()

        elif command == "BUTTON":
            ButtonTest()

        elif command == "XYZAXIS":
            print("In progress")

        elif command == "GRIPPER":
            print("In progress")

        elif command == "PLATFORM":
            plat_servoTest()
            
            
        else:
            print("Unknown response. Please try again.")


if __name__ == "__main__":
    test_loop()
    
