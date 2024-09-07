from ultralytics import YOLO
import numpy as np
import cv2
from time import sleep


def TakePicture():
    # Attach camera object
    webcamera = cv2.VideoCapture(0)
    sleep(2)
    brightness_value = 170  # Adjust this value as needed
    webcamera.set(cv2.CAP_PROP_BRIGHTNESS, brightness_value)
    # Take a picture
    success, captured_img = webcamera.read()

    return captured_img

def GetMVData(frame):
    #Function takes image input and outputs type_posi array for segregation section

    # Define the range for the color blue in HSV space
    lower_green = np.array([100, 125, 130])
    upper_green = np.array([120, 138, 150])

    # Convert the origin image to HSV color space
    hsv_origin = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only green colors
    mask_origin = cv2.inRange(hsv_origin, lower_green, upper_green)

    # Find contours in the binary mask
    contours, _ = cv2.findContours(mask_origin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    origin_image_coords=(0, 0)
    if contours:
        # Assume the largest contour is the green rectangle
        contour = max(contours, key=cv2.contourArea)

        # Get the bounding box of the largest contour
        x, y, w, h = cv2.boundingRect(contour)

        # Calculate the lower left corner of the rectangle
        origin_image_coords = (x, y)


        # Draw the rectangle and the origin point for visualization (optional)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, origin_image_coords, 5, (255, 0, 0), -1)  # Mark the origin


    model = YOLO('best.pt')
    print(model.names)
    #0 for Battery
    #1 for E_Devices
    #2 for Alu_Can (Smart dustbin with Alu can segregation?)


    #Sample Frame


    results = model.predict(frame, classes=[0, 1, 2], conf=0.8, imgsz=640)

    print(results)

    # print(len(results[0].boxes)) A way to get total detected items

    # Sample of printing out data of detected boxes, tensor conversion needed
    # ID, coordinates and confidence level
    # print("ID", results[0].boxes[0].cls[0].item())
    # print("Coordinates", results[0].boxes[0].xyxy[0].tolist()) #x1, y1, x2, y2 format
    # print("Confidence:", results[0].boxes[0].conf.item()) #Confidence may become a feature to improve accuracy

    waste_type = []  # Store the waste types
    for current_box in results[0].boxes:
        waste_type.append(results[0].names[current_box.cls[0].item()]) # Translate ID into an English string
        
    print(waste_type)  # For verification

    # Create type_posi array
    waste_symbol = []

    for waste in  waste_type:
        if waste == 'Battery':
            waste_symbol.append("B")
        elif waste == 'E_Devices':
            waste_symbol.append("E")
        elif waste == 'Alu_Can':
            waste_symbol.append("M")

    i = 0
    cen_x = []
    cen_y = []
    
    box_area = []
    
    for box in results[0].boxes:
        
        x_y = results[0].boxes[i].xyxy[0].tolist()
        
        # Retrieve corner points of bounding box
        x1 = x_y[0]
        y1 = x_y[1]
        x2 = x_y[2]
        y2 = x_y[3]
        
        print("\n")
        print(f"Individual box for {results[0].names[box.cls[0].item()]}")
        print("x1", x_y[0])
        print("y1", x_y[1])
        print("x2", x_y[2])
        print("y2", x_y[3])
        print("\n")

        

        
        
        # Calculate centre coordinates relative to image origin
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        
        # Draw the center point on the object bounding boxes
        cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)
        
        # Calculate new centre coordinates relative to platform origin
        object_new_coords = (
            -(center_x-origin_image_coords[0]),
            center_y - origin_image_coords[1]
        )

        # Calculate the detected box area
        detected_area = int((x2 - x1)*(y2 - y1))

        # Store centre coordinates
        cen_x.append(object_new_coords[0])
        cen_y.append(object_new_coords[1])
           
        box_area.append(detected_area)
        
        i += 1

    print("cen_x = ", cen_x)
    print("cen_y = ", cen_y)

    type_posi = np.vstack((waste_symbol, cen_x, cen_y, box_area))

    print("The resulting type_posi array")
    print(origin_image_coords)
    print(type_posi)

    return type_posi


#Form of the returned type_posi
#[Waste Type]
#[]
#[X box center]
#[Y box center]
#[Box Area]
    
#print(GetMVData(TakePicture()))

GetMVData(TakePicture())
