from ultralytics import YOLO
import numpy as np
import cv2
from time import sleep


def TakePicture():
    # Attach camera object
    webcamera = cv2.VideoCapture(0)

    brightness_value = 170  # Adjust this value as needed
    webcamera.set(cv2.CAP_PROP_BRIGHTNESS, brightness_value)
    webcamera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Set width
    webcamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Set height
    # sleep(2)


    for _ in range(10):  # Try up to 10 times to initialize the camera
        if webcamera.isOpened():
            success, _ = webcamera.read()
            if success:
                break  # Camera is ready
        sleep(0.5)  # Wait for a short time before retrying

    # Take a picture
    success, captured_img = webcamera.read()

    return captured_img


def GetMVData(frame):
    # Function takes image input and outputs type_posi array for segregation section
    # Create QR code detector
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred_frame = cv2.GaussianBlur(gray_frame, (3, 3), 0)

    # # Apply adaptive histogram equalization (CLAHE) for contrast improvement
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # enhanced_frame = clahe.apply(blurred_frame)
    #
    #
    # # Optionally, use adaptive thresholding to further improve visibility
    # adaptive_thresh = cv2.adaptiveThreshold(
    #     enhanced_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 10
    # )

    detector = cv2.QRCodeDetector()

    origin_detected = False  # Flag to track if origin is detected

    # Detect and decode QR code
    data, points, _ = detector.detectAndDecode(blurred_frame)

    if points is not None and data and not origin_detected:
        # QR code detected, proceed with processing

        # Convert points to integer format
        points = points[0].astype(int)  # Convert the float points to integers

        # Draw the polygon around the QR code
        for i in range(len(points)):
            cv2.line(blurred_frame, tuple(points[i]), tuple(points[(i + 1) % len(points)]), (0, 255, 0), 2)

        # Calculate the center of the QR code (origin)
        up_left_corner= points[0]
        origin_x = up_left_corner[0]
        origin_y = up_left_corner[1]


        # Mark the origin on the frame
        cv2.circle(blurred_frame, (origin_x, origin_y), 5, (255, 0, 0), -1)

        print(f"QR Code detected: {data}")
        print(f"Origin at: ({origin_x}, {origin_y})")

        origin_detected = True  # Set the flag to True once origin is detected

    # Show the frame with the marked origin, whether detected or not
    if origin_detected:
        # Display the frame with the detected QR code and marked origin
        cv2.putText(blurred_frame, f"Origin: ({origin_x}, {origin_y})", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("QR Code Detection", blurred_frame)

    model = YOLO('best.pt')
    print(model.names)
    # 0 for Battery
    # 1 for E_Devices
    # 2 for Alu_Can (Smart dustbin with Alu can segregation?)

    # Sample Frame

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
        waste_type.append(results[0].names[current_box.cls[0].item()])  # Translate ID into an English string

    print(waste_type)  # For verification

    # Create type_posi array
    waste_symbol = []

    for waste in waste_type:
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
            -(center_x - origin_x),
            center_y - origin_y
        )

        # Calculate the detected box area
        detected_area = int((x2 - x1) * (y2 - y1))

        # Store centre coordinates
        cen_x.append(object_new_coords[0])
        cen_y.append(object_new_coords[1])

        box_area.append(detected_area)

        i += 1

    print("cen_x = ", cen_x)
    print("cen_y = ", cen_y)

    type_posi = np.vstack((waste_symbol, cen_x, cen_y, box_area))

    print("The resulting type_posi array")
    print(origin_x,origin_y)
    print(type_posi)
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imshow("QR Code Detection", frame)
            break
    return type_posi


# Form of the returned type_posi
# [Waste Type]
# []
# [X box center]
# [Y box center]
# [Box Area]

# print(GetMVData(TakePicture()))

GetMVData(TakePicture())
