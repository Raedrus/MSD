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
    ser.write((command + '\n').encode())
    time.sleep(0.1)
    response = ser.readline().decode('utf-8').strip()
    return response


def send_position(position):
    ser.write((str(position) + '\n').encode())
    time.sleep(0.1)
    response = ser.readline().decode('utf-8').strip()
    return response


# Call this function to test the ultrasonic sensor. If the 4 printed values
# are reasonable, the sensor is working. Else, check GPIO assignment,
# check the wiring, ensure 5V is supplied to Vcc pin

def esp_com(command):
    response = send_command(command)
    print("Response from ESP32:", response)

    if response == "Initiating MAGNET Test..." or \
            response == "Initiating LED Strip Test..." or \
            response == "Initiating Green LED Test..." or \
            response == "Initiating Red LED Test...":
        # Wait for completion message


    elif response == "Initiating LID servo Test..." or \
            response == "Initiating GATE servo Test...":

        while True:
            try:
                position = int(input(" ").strip())
                if 0 <= position <= 100:
                    response = send_position(position)
                    print("Response from ESP32:", response)
                    if "info_servo variable string is:" in response:
                        break
                    else:
                        print("Failed to set position. Try again.")
                else:
                    print("Position out of range. Enter a value between 0 and 100.")
            except ValueError:
                print("Invalid input. Enter an integer between 0 and 100.")

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
    while True:
        if start_button.is_pressed:
            print("Start button is pressed")
            sleep(1)
        elif Estop_button.is_pressed:
            print("Emergency Stop button is pressed")
            sleep(1)


def test_loop():
    while True:
        command = input("Enter test command or 'exit' to quit: ").strip()
        if command.lower() == 'exit':
            print("Exiting...")
            break

        elif command.upper() == "MAGNET" or "LED" or "RLED" or \
                "GLED" or "LID" or "GATE":
            esp_com(command)

        elif command.upper() == "ULTRASONIC":
            UltraTest()

        elif command.upper() == "BUTTON":
            ButtonTest()

        elif command.upper() == "XYZAXIS":
            print("In progress")

        elif command.upper() == "GRIPPER":
            print("In progress")

        elif command.upper() == "PLATFORM":


        else:
            print("Unknown response. Please try again.")


if __name__ == "__main__":
    test_loop()
