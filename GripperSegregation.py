# Gripping cycle refers to:
# Object detection --> obtain number of objects and coordinates --> gripper sorting until no items remain

import CONST  # constant values only, coordinates and such

import ImgWasteData as imgD  # Image Data
import V33_XYMovementControls_XY as gan  # Gantry
import ZAxis as za

import serial
from Serial_Pi_ESP32 import esp32_comms

# Variables##########################################
gripper_posi = [0, 0]  # Current gripper coordinates in steps

# intentional

# Class declarations#################################
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)


####################################################

def home_XY():
    # Home the axis at the start and at the very end

    gan.drivedrv8825(ysteps_toDesti, dirY, "Full", "Y", 0.0004, homing=True)
    gan.drivedrv8825(ysteps_toDesti, dirY, "Full", "X", 0.0004, homing=True)
    esp32_comms(ser, "G_OPEN")


# The 4 bins (General waste, metal, electronics, batteries)
# One's with gripping requirements: Metals (Aluminum can), electronics, batteries


def ToCoordZero():
    # The gripper goes to 0 coordinate of the camera frame

    # ASSUMING THIS ENCODER IS THE HOME POSITION ENCODER
    drivedrv8825(ysteps_toDesti,
                 dirY,
                 "Full",
                 "Y",
                 0.0004,
                 tobin=1)  # Move the Y-axis towards one encoder

    gan.drivedrv8825(ysteps_toDesti, dirY, "Full", "X", 0.0004, homing=True)

    gripper_posi[0] = 0
    gripper_posi[1] = 0


def ToBinA(waste_sz):
    # With assumption that the item is already picked up
    # Take the item and drop them at Bin A

    # waste_sz in terms pixels detected from the camera, in type_posi array
    # For now, based on box area (Not foolproof for standing items)

    xDir = 0  # Placeholder values
    xloc = 30  # Placeholder value
    which_encoder = 1  # Placeholder value

    # The bins that drop gripping items have encoders on them, only a matter of which side
    # which_encoder is an int of 1 or 0 to control direction (which encoder to move to)
    # After moving to that location, xloc moves it above the right bin
    # xDir has to be determined from checking the right way to turn the motor

    # Move the gripper set towards to x limit switch,
    # this gives it accuracy later on when moviong to the bin
    gan.drivedrv8825(ysteps_toDesti, dirY, "Full", "X", 0.0004, homing=True)
    drivedrv8825(ysteps_toDesti,
                 dirY,
                 "Full",
                 "Y",
                 0.0004,
                 tobin=1)  # Move the Y-axis towards one encoder

    # Move X towards the needed bin
    drivedrv8825(0,
                 dirY,
                 "Full",
                 "XY",
                 0.001,
                 list_DirXY=[xDir, 1],
                 list_XYSteps=[xloc, 0],
                 invert_xDir=True,
                 invert_yDir=True)  # Direction inversion

    # Use a specific type of grip depending on size

    if waste_sz <= CONST.SMALL_SIZE:
        vacuum_release_drop()
    else:
        finger_release_drop()

    # Move x back to it's limit switch to recalibrate
    gan.drivedrv8825(ysteps_toDesti, dirY, "Full", "X", 0.0004, homing=True)

    print("Waste to Bin A was Attempted")

    # Return the current position of the gripper after completion of the operation
    # x = 0, because it was homed for calibration
    return [0, ENC1_POSI]


def ToBinB(waste_sz):
    # With assumption that the item is already picked up
    # Take the item and drop them at Bin A

    # waste_sz in terms pixels detected from the camera, in type_posi array
    # For now, based on box area (Not foolproof for standing items)

    xDir = 0  # Placeholder values
    xloc = 30  # Placeholder value
    which_encoder = 0  # Placeholder value

    # The bins that drop gripping items have encoders on them, only a matter of which side
    # which_encoder is an int of 1 or 0 to control direction (which encoder to move to)
    # After moving to that location, xloc moves it above the right bin
    # xDir has to be determined from checking the right way to turn the motor

    # Move the gripper set towards to x limit switch,
    # this gives it accuracy later on when moviong to the bin
    gan.drivedrv8825(ysteps_toDesti, dirY, "Full", "X", 0.0004, homing=True)
    gan.drivedrv8825(ysteps_toDesti, dirY, "Full", "Y", 0.0004,
                     homing=True)  # Assuming the bin rests in this limit switch

    # Move X towards the needed bin
    gan.drivedrv8825(0,
                 dirY,
                 "Full",
                 "XY",
                 0.001,
                 list_DirXY=[xDir, 1],
                 list_XYSteps=[xloc, 0],
                 invert_xDir=True,
                 invert_yDir=True)  # Direction inversion

    # Use a specific type of grip depending on size

    if waste_sz <= CONST.SMALL_SIZE:
        vacuum_release_drop()
    else:
        finger_release_drop()

    # Move x back to it's limit switch to recalibrate
    gan.drivedrv8825(ysteps_toDesti, dirY, "Full", "X", 0.0004, homing=True)

    print("Waste to Bin A was Attempted")

    # Return the current position of the gripper after completion of the operation
    # x = 0, because it was homed for calibration
    return [0, ENC2_POSI]


def ToBinC(waste_sz):
    # With assumption that the item is already picked up
    # Take the item and drop them at Bin A

    # waste_sz in terms pixels detected from the camera, in type_posi array
    # For now, based on box area (Not foolproof for standing items)

    xDir = 0  # Placeholder values
    xloc = 60  # Placeholder value
    which_encoder = 0  # Placeholder value

    # The bins that drop gripping items have encoders on them, only a matter of which side
    # which_encoder is an int of 1 or 0 to control direction (which encoder to move to)
    # After moving to that location, xloc moves it above the right bin
    # xDir has to be determined from checking the right way to turn the motor

    # Move the gripper set towards to x limit switch,
    # this gives it accuracy later on when moving to the bin
    gan.drivedrv8825(ysteps_toDesti, dirY, "Full", "X", 0.0004, homing=True)
    gan.drivedrv8825(ysteps_toDesti, dirY, "Full", "Y", 0.0004,
                     homing=True)  # Assuming the bin rests in this limit switch

    # Move X towards the needed bin
    drivedrv8825(0,
                 dirY,
                 "Full",
                 "XY",
                 0.001,
                 list_DirXY=[xDir, 1],
                 list_XYSteps=[xloc, 0],
                 invert_xDir=True,
                 invert_yDir=True)  # Direction inversion

    # Use a specific type of grip depending on size

    if waste_sz <= CONST.SMALL_SIZE:
        vacuum_release_drop()
    else:
        finger_release_drop()

    # Move x back to it's limit switch to recalibrate
    gan.drivedrv8825(ysteps_toDesti, dirY, "Full", "X", 0.0004, homing=True)

    print("Waste to Bin A was Attempted")

    # Return the current position of the gripper after completion of the operation
    # x = 0, because it was homed for calibration
    return [0, ENC2_POSI]


# DROPS
# There are two kinds of drops, the gripper drop or vacuum drop
def finger_release_drop():
    sleep(0.2)
    # lower the z axis
    full_lower_gripper()

    # open the gripper fingers
    esp32_comms(ser, "G_OPEN")

    sleep(0.2)
    # Elevate the gripper back upwards
    full_ele_gripper()


def vacuum_release_drop():
    pass


##########################################################################################


def main():
    full_ele_gripper()

    home_XY()

    # Detect the image, return the required position and item type data
    # and box area
    type_posi = imgD.GetMVData(imgD.TakePicture())

    ToCoordZero()

    while len(type_posi[0]) > 0:
        # The output below is the coordinates of the nearest waste
        # [x, y] in terms of steps
        xy_steps_toDesti = gan.getshortestdist(gripper_posi, type_posi, 20)
        # Obtaining turning directions
        dirX = int(xy_steps_toDesti[0]) >= 0
        dirY = int(xy_steps_toDesti[1]) >= 0
        dirXY = [dirX, dirY]

        # Move the gripper to the nearest waste
        gan.drivedrv8825(0, dirY, "Full",
                         "XY",
                         0.001,
                         list_DirXY=dirXY,
                         list_XYSteps=xy_steps_toDesti,
                         invert_xDir=True,
                         invert_yDir=True)

        if waste_sz <= CONST.SMALL_SIZE:
            pass  # Where the vacuum pump is supposed to turn off
            full_lower_gripper()
        # Turn vacuum pump on
        else:
            # Open the gripper fingers
            esp32_comms(ser, "G_OPEN")
            # Parameter specifies number of steps required for partial descent
            za.partial_lower_gripper(pd_steps)
            # close fingers
            esp32_comms(ser, "G_CLOSE")

            full_ele_gripper()
            match type_posi[0]:
                # Providing size of the waste as input parameter
                case "B":
                    ToBinA(type_posi[3])
                case "E":
                    ToBinB(type_posi[3])
                case "M":
                    ToBinC(type_posi[3])

        type_posi = imgD.GetMVData(imgD.TakePicture())
