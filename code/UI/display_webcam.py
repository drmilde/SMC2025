import pygame
import cv2
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 640  # Standard webcam resolution width
SCREEN_HEIGHT = 480 # Standard webcam resolution height

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Webcam Feed (Pygame + OpenCV)")

# Initialize OpenCV video capture
# 0 usually refers to the default webcam. If you have multiple, try 1, 2, etc.
cap = cv2.VideoCapture(0)

# Check if the webcam was opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
    print("Please ensure your webcam is connected and not in use by another application.")
    pygame.quit()
    sys.exit()

# Set webcam resolution (optional, might not be supported by all cameras)
# You can try to set a higher resolution if your camera supports it
cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)

# Clock for managing frame rate
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read a frame from the webcam
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to grab frame from webcam.")
        break

    # Convert the OpenCV BGR image to RGB (Pygame uses RGB)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Flip the image vertically (OpenCV captures often have the Y-axis flipped relative to Pygame)
    # Also, some webcams mirror the image. You might need to flip horizontally too, depending on your camera.
    # frame = cv2.flip(frame, 0) # Flip vertically (0 for vertical, 1 for horizontal, -1 for both)
    # frame = cv2.flip(frame, 1) # Flip horizontally (comment out if your webcam already provides unmirrored view)

    # Convert the NumPy array (OpenCV frame) to a Pygame Surface
    # The .swapaxes(0, 1) is crucial to convert the (height, width, channels)
    # numpy array to (width, height, channels) suitable for Pygame.
    pygame_frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

    # Scale the frame to fit the screen if necessary (only if the webcam resolution differs from SCREEN_WIDTH/HEIGHT)
    if pygame_frame.get_width() != SCREEN_WIDTH or pygame_frame.get_height() != SCREEN_HEIGHT:
        pygame_frame = pygame.transform.scale(pygame_frame, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Draw the frame onto the Pygame screen
    screen.blit(pygame_frame, (0, 0))

    # Update the display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(30) # Display at 30 frames per second

# Release the webcam and quit Pygame
cap.release()
pygame.quit()
sys.exit()