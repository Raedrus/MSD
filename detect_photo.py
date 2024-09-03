import cv2
from ultralytics import YOLO
import numpy as np
import time

model = YOLO('best.pt')
print(model.names)
webcamera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# webcamera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# webcamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Set the brightness value (brightness range is typically from 0.0 to 1.0)
brightness_value = 155  # Adjust this value as needed
webcamera.set(cv2.CAP_PROP_BRIGHTNESS, brightness_value)

# only if needed
time.sleep(2)  # Wait for 2 seconds to ensure the camera is ready

# Load the origin image to set the origin

# take a photo for origin definition
success, origin_image = webcamera.read()

# Define the range for the color green in HSV space
lower_green = np.array([40, 20, 40])
upper_green = np.array([80, 100, 255])



# take a photo for object detection
success, frame = webcamera.read()


# Convert the origin image to HSV color space
hsv_origin = cv2.cvtColor(origin_image, cv2.COLOR_BGR2HSV)


# Threshold the HSV image to get only green colors
mask_origin = cv2.inRange(hsv_origin, lower_green, upper_green)


# Find contours in the binary mask
contours, _ = cv2.findContours(mask_origin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


if contours:
    # Assume the largest contour is the green rectangle
    contour = max(contours, key=cv2.contourArea)

    # Get the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(contour)

    # Calculate the lower left corner of the platform rectangle
    origin_image_coords = (x, y + h)

    distperpix = round(300/w, 3)

    # Draw the rectangle and the origin point for visualization (optional)
    cv2.rectangle(origin_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.circle(origin_image, origin_image_coords, 5, (255, 0, 0), -1)  # Mark the origin

    # Display the origin image with the marked origin (optional)
    cv2.imshow("Origin Image", origin_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Initialize lists for storing details of items with IDs 1, 2, and 3
item_types = []
x_coordinates = []
y_coordinates = []



results = model.track(frame, classes=[0, 1, 2], conf=0.8, imgsz=640)
cv2.putText(frame, f"Total: {len(results[0].boxes)}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
            cv2.LINE_AA)
for box in results[0].boxes:
    # Get the bounding box coordinates
    x1, y1, x2, y2 = box.xyxy[0]

    # Calculate the center coordinates
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)

    # Adjust the coordinates based on the new origin
    object_new_coords = (
        center_x - origin_image_coords[0],
        origin_image_coords[1] - center_y
    )

    # Draw the center point on the object bounding boxes
    cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)
    cv2.putText(frame, f"({object_new_coords[0]}, {object_new_coords[1]})", (center_x, center_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 0, 0), 1, cv2.LINE_AA)

    obj_id = box.id
    label = model.names[int(box.cls)]

    # Append details of the item with ID 1 to the respective arrays
    if obj_id == 1:
        if label == 'Battery':
            label = 'B'

        elif label == 'E_Devices':
            label = 'E'

        else:
            label = 'A'

        item_types.append(label)
        x_coordinates.append(object_new_coords[0])
        y_coordinates.append(object_new_coords[1])

cv2.imshow("Live Camera", results[0].plot())

while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

webcamera.release()

# Create the NumPy array
TypePosi_Data = np.array([item_types, x_coordinates, y_coordinates], dtype=object)

# Print the NumPy array
print(TypePosi_Data)
