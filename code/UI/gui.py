import pygame
import pygame_gui
import sys
import cv2
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 700
WEBCAM_FEED_WIDTH = 1024
GUI_WIDTH = SCREEN_WIDTH - WEBCAM_FEED_WIDTH
GUI_HEIGHT = SCREEN_HEIGHT

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FreeMoscion")

hsLogoSurface = pygame.image.load(os.path.join('.', 'hs-fulda-logo.png')).convert_alpha()
fmLogoSurface = pygame.image.load(os.path.join('.', 'freemoscion-logo.png')).convert_alpha()


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
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_FEED_WIDTH)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)

# Pygame GUI Manager
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), 'freemoscion_theme.json')

# Placeholder for webcam feed (a simple colored rectangle)
# In a real application, you would load frames from your webcam here
webcam_feed_rect = pygame.Rect(0, 0, WEBCAM_FEED_WIDTH, SCREEN_HEIGHT)
header_rect = pygame.Rect(0, 0, WEBCAM_FEED_WIDTH, 200)
placeholder_image = pygame.Surface((WEBCAM_FEED_WIDTH, SCREEN_HEIGHT))
placeholder_image.fill((50, 50, 50)) # Dark gray color

font = pygame.font.Font(None, 40)
text_surface = font.render("Webcam Feed Placeholder", True, (255, 255, 255))
text_rect = text_surface.get_rect(center=placeholder_image.get_rect().center)
placeholder_image.blit(text_surface, text_rect)


# GUI elements (buttons)
gui_panel_rect = pygame.Rect(WEBCAM_FEED_WIDTH, 0, GUI_WIDTH, GUI_HEIGHT)

buttons = []
button_labels = ["add region", "remove region", "detect markers", "edit marker", "load controller", "save controller", "calibrate", "settings", "execute" ]
button_height = 50
button_spacing = 15
start_y = 50

for i, label in enumerate(button_labels):
    button_rect = pygame.Rect(WEBCAM_FEED_WIDTH + (GUI_WIDTH - 200) // 2,
                              start_y + i * (button_height + button_spacing),
                              200, button_height)
    button = pygame_gui.elements.UIButton(relative_rect=button_rect,
                                          text=label,
                                          manager=manager)
    buttons.append(button)

# Clock for managing frame rate
clock = pygame.time.Clock()

running = True
while running:
    time_delta = clock.tick(60) / 1000.0  # Limit to 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                for i, button in enumerate(buttons):
                    if event.ui_element == button:
                        print(f"'{button_labels[i]}' pressed!")
                        # Add your functionality for each button here
                        if i == 0:
                            print("Function for Button 1 executed.")
                        elif i == 1:
                            print("Function for Button 2 executed.")
                        # ... and so on for other buttons

        manager.process_events(event)

    # Update GUI manager
    manager.update(time_delta)

    # Drawing
    screen.fill((243, 241, 242))  # Fill background black
    

    # Draw webcam feed placeholder
    #screen.blit(placeholder_image, webcam_feed_rect)

    # Draw GUI panel background (optional, for visual separation)
    pygame.draw.rect(screen, (211,205,198), gui_panel_rect) # Dark gray for GUI background
    pygame.draw.rect(screen, (255,255,255), header_rect) # Dark gray for GUI background

    # Draw GUI elements
    manager.draw_ui(screen)

    ################ READ THE WEBCAM

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
        SCALED_HEIGHT = WEBCAM_FEED_WIDTH * (pygame_frame.get_height() / pygame_frame.get_width()) 
        pygame_frame = pygame.transform.scale(pygame_frame, (WEBCAM_FEED_WIDTH, SCALED_HEIGHT))

        # Draw the frame onto the Pygame screen
        offset_y = (SCREEN_HEIGHT - SCALED_HEIGHT) / 2
        screen.blit(pygame_frame, (0, offset_y))


    screen.blit(hsLogoSurface, (670, -10))
    screen.blit(fmLogoSurface, (10, 10))

    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit()