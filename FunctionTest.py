### Testing functions ###
# Used for troubleshooting, these were tested on a physical prototype
# thus it is reasonable to base troubleshooting off this
# also a maintenance feature incase the dustbin components break down


# LED Test
# Call this function to test circuit connection of Dustbin LEDs
# Troubleshoot: Check GPIO assignment, wire connections, fault in wires,
# fault in wires or fault in GPIO if LEDs do not light up
def LEDTest():
    print("Blinking LEDs")
    for i in range(4):
        green_led.on()
        red_led.on()
        sleep(0.5)
        green_led.off()
        red_led.off()
        sleep(0.5)
    green_led.off()
    red_led.off()


# Call this function to test the ultrasonic sensor. If the 4 printed values
# are reasonable, the sensor is working. Else, check GPIO assignment,
# check the wiring, ensure 5V is supplied to Vcc pin
def UltraTest():
    for i in range(4):
        print('Distance: ', ult_sensor.distance * 100)
        sleep(1)


# For debugging purposes
# Show the distance measured by the ultrasonic sensor
def PrintUltSenseDist():
    print("Detected distance:", float(round(ult_sensor.distance, 3)), "System in Sensing Mode")
    sleep(0.2)


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


def LidServoTest():
    print("0 deg")
    lid_servo.min()
    sleep(1.5)

    print("90 deg")
    lid_servo.mid()
    sleep(1.5)

    print("180 deg")
    lid_servo.max()
    sleep(1.5)

    # turning off lid_servo
    lid_servo.detach()


def GateServoTest():
    print( "0 deg" )
    gate_servo.min()
    sleep( 1.5 )

    print( "90 deg" )
    gate_servo.mid()
    sleep( 1.5 )

    print( "180 deg" )
    gate_servo.max()
    sleep( 1.5 )

    # turning off lid_servo
    gate_servo.detach()