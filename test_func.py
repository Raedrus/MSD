import ultralytics
import numpy as np
import cv2
import time
from gpiozero import LED
from gpiozero import DistanceSensor
from gpiozero import Button
from gpiozero import Servo
from gpiozero import DigitalOutputDevice
from gpiozero import DigitalInputDevice
import time
from time import sleep
import serial

import sys  # For testing system quits
import os  # For testing system quits
import psutil  # For testing system quits


current_system_pid = os.getpid()
ThisSystem = psutil.Process(current_system_pid)

# GPIO Assignments################################################################
#pin_green_led = 20
#pin_red_led = 21

pin_ult_echo = 4
pin_ult_trigger = 17

pin_start = 6
pin_Estop = 5

pin_transistor_magnet = 16

pin_plat_servo = 27

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


def drivedrv8825(steps, dir, microstep, selected_xy, time_delay, homing=False, tobin=None, list_XYSteps=None,
                 list_DirXY=None, invert_xDir=False, invert_yDir=False):
    # En_Motors = 1 to turn motor on
    # Dir = Boolean to control direction of motor spin (1 to spin anticlockwise (reference: shaft pointing at your face))
    # Steps = The number of steps for the stepper motor to takewhile
    # Microstep = Whether it it is full step, half step, 1/4, 1/8, 1/16 or 1/32
    # Selected_XY = Whether DRV8825 for X or Y is selected use "XY" TO ENABLE SIMULTANEOUS AXIS MOVEMENT,
    # SIMULTAENOUS MOVEMENT REQUIRES list_XYSteps and list_DirXY
    # time_delay = Delay between each step, influences motor speed
    # homing is a boolean, setting it to true causes the selected axis to home instead
    # ToBIn is useful for making the stepper motor move in y-axis direction towards one of the encoders
    # When: None = Disabled, 1 = Move to one of the encoders, 0 Move to another encoder
    # invert_xDir  when set to true, will invert inputted dir or list_DirXY X
    # invert_y_Dir when set to true, will invert inputted dir or list_DirXY X

    # NOTE: While homing or in simultaneous mode, the Steps parameter is not signifigant, can be any number
    # Dir is ignored in simultaenous mode

    # Direction inversion decisions
    if (invert_xDir == True) or (invert_yDir == True) and (list_DirXY == None):
        dir = not (dir)
    # In single axis mode, you can set whichever invert_xDir or invert_yDir to cause inversion
    elif (invert_xDir == True) or (invert_yDir == False) and (list_DirXY != None):
        list_DirXY[0] = not (list_DirXY[0])
    elif (invert_xDir == False) or (invert_yDir == True) and (list_DirXY != None):
        list_DirXY[1] = not (list_DirXY[1])

    # Refer to the dictionary below for what to place into this parameter
    # Note: For DRV8825, the EN pin, RST pin and SLP pin are active LOW
    # Thus to enable the DRV8825, its EN pin should be set to false

    # Microstep Guide for reference (DRV8825) - PHYSICAL PINS
    # MODE0    MODE1    MODE2    Microstep Resolution
    # Low    Low        Low     Full step
    # High    Low        Low        Half step
    # Low    High    Low        1/4 step
    # High    High    Low        1/8 step
    # Low    Low        High    1/16 step
    # High    Low        High    1/32 step
    # Low    High    High    1/32 step
    # High    High    High    1/32 step

    # Use these names to specify microstep
    microsteps = {'Full': 1,
                  'Half': 2,
                  '1/4': 4,
                  '1/8': 8,
                  '1/16': 16,
                  '1/32': 32}

    # If full steps uses 200 steps to complete with a delay of 0.005,
    # using half step would require 400 steps, and if we keep the delay 0.005
    # the process will become twice as long, thus the below is to adjust
    # the time delay between each step so that all types of steps complete
    # their journey with the same amount of time

    time_delay = time_delay / microsteps[microstep]

    # To compensate for the numbers of steps
    print("Check microstep value ", microsteps[microstep])
    steps = steps * microsteps[microstep]

    if selected_xy == "X":

        x_drv8825_en.off()  # Turn ON the chosen motor
        if dir:
            x_drv8825_dir.on()  # Direction of turn selected
        else:
            x_drv8825_dir.off()

    elif selected_xy == "Y":
        y_drv8825_en.off()  # Turn ON the chosen motor
        if dir:
            y_drv8825_dir.on()  # Direction of turn selected
        else:
            y_drv8825_dir.off()

    elif selected_xy == "XY":
        x_drv8825_en.off()  # Turn ON the chosen motor
        if list_DirXY[0]:
            x_drv8825_dir.on()  # Direction of turn selected
            print("Direction Check")
            print("x_drv8825_dir = 1")
        else:
            x_drv8825_dir.off()
            print("Direction Check")
            print("x_drv8825_dir = 0")

        y_drv8825_en.off()  # Turn ON the chosen motor
        if list_DirXY[1]:
            y_drv8825_dir.on()  # Direction of turn selected
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
            for i in range(steps):
                x_drv8825_step.on()
                sleep(time_delay)
                x_drv8825_step.off()
                sleep(time_delay)
                print(f"Stepping X-axis motor {i + 1}/{steps}")

            sleep(1)  # A brief pause before disabling the motor, so that inertia is accounted for
            x_drv8825_en.on()  # Disable the motor, may reduce holding torque but reduce power dissipation

        elif selected_xy == "Y":
            for i in range(steps):
                y_drv8825_step.on()
                sleep(time_delay)
                y_drv8825_step.off()
                sleep(time_delay)
                print(f"Stepping Y-axis motor {i + 1}/{steps}")
        elif selected_xy == "XY":
            print("list_XYSteps[0] + list_XYSteps[1]", abs(list_XYSteps[0] + list_XYSteps[1]))

            x_i = 0
            y_i = 0
            for i in range(abs(list_XYSteps[0]) + abs(list_XYSteps[1])):

                if i < abs(list_XYSteps[0]):  # Check if X has completed its steps
                    x_drv8825_step.on()
                    sleep(time_delay)
                    x_drv8825_step.off()
                    sleep(time_delay)
                    x_i += 1
                    print(f"Stepping X-axis motor {x_i}/{abs(list_XYSteps[0])}")

                if i < abs(list_XYSteps[1]):
                    y_drv8825_step.on()
                    sleep(time_delay)
                    y_drv8825_step.off()
                    sleep(time_delay)
                    y_i += 1
                    print(f"Stepping Y-axis motor {y_i}/{abs(list_XYSteps[1])}")

            sleep(1)  # A brief pause before disabling the motor, so that inertia is accounted for
            y_drv8825_en.on()  # Disable the motor, may reduce holding torque but reduce power dissipation

        print("Movement ", selected_xy, " complete")

    elif homing == True and tobin == None:
        # The core XY moves the gripper to home by turning the steppers until a limit switch is hit
        # MAY BE DEPRECATED FOR A SAFER OPTION, IN EVENT THAT THE LIMIT SWITCHES FAIL, THE
        # STEPPER MAY RAM AND STALL, CAUSING HIGHER CURRENT DRAW AND FORCE THE PROGRAM INTO INFINITE LOOP
        if selected_xy == "X":
            x_drv8825_en.off()  # Turn on motor
            x_drv8825_dir.off()  # ADJUST TO TURN IN DIRECTION WHICH HOME LIMIT SWITCH IS LOCATED

            while x_homingswitch.is_pressed == False:
                x_drv8825_step.on()
                sleep(time_delay)

                x_drv8825_step.off()
                sleep(time_delay)

                print("Stepping motor")

            sleep(1)  # A brief pause before disabling the motor, so that inertia is accounted for
            x_drv8825_en.on()  # Disable the motor, may reduce holding torque but reduce power dissipation

        elif selected_xy == "Y":
            y_drv8825_en.off()  # Turn on motor
            y_drv8825_dir.off()  # ADJUST TO TURN IN DIRECTION WHICH HOME LIMIT SWITCH IS LOCATED

            while y_homingswitch.is_pressed == False:
                y_drv8825_step.on()
                sleep(time_delay)

                y_drv8825_step.off()
                sleep(time_delay)

                print("Stepping motor")

            sleep(1)  # A brief pause before disabling the motor, so that inertia is accounted for

            y_drv8825_en.value = 1  # Disable the motor, may reduce holding torque but reduce power dissipation

        print("Homing for ", selected_xy, " complete")

    elif homing == False and tobin == 0:  # CHANGE ToBin == 1 Incase direction is wrong
        y_drv8825_en.off()  # Enable the motor
        y_drv8825_dir.value = tobin  # Set motor direction

        # SIMILAR TO LIMIT SWITCH, THERE IS AN OPPORTUNITY TO WRITE A SAFER ALGORITHM FOR THIS SECTION
        while ir_enc1.value == False:
            y_drv8825_step.on()
            sleep(time_delay)

            y_drv8825_step.off()
            sleep(time_delay)

            print("Stepping motor Indefinitely Enc1")

        y_drv8825_en.on()  # Turn the motor off
    elif homing == False and tobin == 1:  # CHANGE ToBin == 0 Incase direction is wrong
        y_drv8825_en.off()  # Enable the motor
        y_drv8825_dir.value = tobin  # Set motor direction

        # SIMILAR TO LIMIT SWITCH, THERE IS AN OPPORTUNITY TO WRITE A SAFER ALGORITHM FOR THIS SECTION
        while ir_enc2.value == False:
            y_drv8825_step.on()
            sleep(time_delay)

            y_drv8825_step.off()
            sleep(time_delay)

            print("Stepping motor Indefinitely to Enc2")

        y_drv8825_en.on()  # Turn the motor off

def YTest():

    drivedrv8825(200, 1, "Full", "Y", 0.001) #A full rotation with Y


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

        elif command == "YAXIS" :
            YTest()
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
    
