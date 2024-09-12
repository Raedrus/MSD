import cv2

# Initialize camera
cap = cv2.VideoCapture(0)  # Replace with your camera index

# Create QR code detector
detector = cv2.QRCodeDetector()

origin_detected = False  # Flag to track if origin is detected

while True:
    ret, frame = cap.read()  # Capture frame-by-frame
    if not ret:
        print("Failed to capture image")
        continue  # If no frame is captured, skip and try again

    # Detect and decode QR code
    data, points, _ = detector.detectAndDecode(frame)

    if points is not None and data and not origin_detected:
        # QR code detected, proceed with processing

        # Convert points to integer format
        points = points[0].astype(int)  # Convert the float points to integers

        # Draw the polygon around the QR code
        for i in range(len(points)):
            cv2.line(frame, tuple(points[i]), tuple(points[(i + 1) % len(points)]), (0, 255, 0), 2)

        # Calculate the center of the QR code (origin)
        origin_x = int(sum(point[0] for point in points) / 4)
        origin_y = int(sum(point[1] for point in points) / 4)

        # Mark the origin on the frame
        cv2.circle(frame, (origin_x, origin_y), 5, (255, 0, 0), -1)

        print(f"QR Code detected: {data}")
        print(f"Origin at: ({origin_x}, {origin_y})")

        origin_detected = True  # Set the flag to True once origin is detected

    # Show the frame with the marked origin, whether detected or not
    if origin_detected:
        # Display the frame with the detected QR code and marked origin
        cv2.putText(frame, f"Origin: ({origin_x}, {origin_y})", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("QR Code Detection", frame)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the windows
cap.release()
cv2.destroyAllWindows()