import cv2
import numpy as np

# Load the image
image = cv2.imread('/Users/dingy/OneDrive/Desktop/n7/1460460.png')

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Define the chessboard size
chessboard_size = (10, 7)  # Change this to the size of your chessboard

# Find the chessboard corners
ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

if ret:
    # Refine corner positions to subpixel accuracy
    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                               criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))

    # Draw and display the corners
    cv2.drawChessboardCorners(image, chessboard_size, corners, ret)

    # Calculate the pixel dimensions of a single square
    square_size_in_pixels = np.mean([np.linalg.norm(corners[i] - corners[i + 1])
                                     for i in range(len(corners) - 1) if (i + 1) % chessboard_size[0] != 0])

    # Known size of a square in real-world units (e.g., cm)
    square_size_in_cm = 2.425

    # Calculate the distance per pixel
    distance_per_pixel = square_size_in_cm / square_size_in_pixels


    # Add text to the image
    text = f'{distance_per_pixel:.4f} cm per pixel'
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (10, 50)  # Position of the text
    font_scale = 1
    color = (0, 255, 0)  # Green color in BGR
    thickness = 2

    # Add the text to the image
    cv2.putText(image, text, org, font, font_scale, color, thickness, cv2.LINE_AA)

    # Highlight one square for visual clarity
    top_left = tuple(corners[0].ravel().astype(int))
    bottom_right = tuple(corners[chessboard_size[0] + 1].ravel().astype(int))
    cv2.rectangle(image, top_left, bottom_right, color, thickness)

    # Display the image
    cv2.imshow('Chessboard with Distance', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Print the results for reference
    print(f'Pixel dimensions of one square: {square_size_in_pixels}')
    print(f'Distance per pixel: {distance_per_pixel} cm')

else:
    print('Chessboard corners not found.')