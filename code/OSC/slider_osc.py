import pygame
import pygame_gui
import sys
from pythonosc.udp_client import SimpleUDPClient

# --- OSC Configuration ---
# IP address and port of the OSC server you want to send data to
# For a local process, this will usually be '127.0.0.1' (localhost)
# The port must match the port your OSC server is listening on.
OSC_IP = "127.0.0.1"
OSC_PORT = 5005
OSC_ADDRESS = "/slider_value" # The OSC address for this data

# Initialize OSC client
try:
    osc_client = SimpleUDPClient(OSC_IP, OSC_PORT)
    print(f"OSC Client initialized: Sending to {OSC_IP}:{OSC_PORT} at address {OSC_ADDRESS}")
except Exception as e:
    print(f"Error initializing OSC client: {e}")
    print("OSC sending functionality might be limited or unavailable.")
    osc_client = None # Set to None if initialization fails

# --- Pygame Setup ---
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame OSC Slider")

# --- Pygame GUI Manager ---
# You can optionally provide a theme file path here if you have one.
# For simplicity, we'll use the default theme for now.
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Slider Configuration ---
slider_rect = pygame.Rect(50, 250, 700, 50) # x, y, width, height
slider_start_value = 127 # Middle of 0-255 range
slider_min_value = 0
slider_max_value = 255

# Create the HSlider (Horizontal Slider)
value_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=slider_rect,
    start_value=slider_start_value,
    value_range=(slider_min_value, slider_max_value),
    manager=manager
)

# Create a label to display the current slider value
value_display_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(350, 180, 100, 50), # Position above slider
    text=f"Value: {int(slider_start_value)}",
    manager=manager
)

# --- Game Loop ---
clock = pygame.time.Clock()
is_running = True
current_slider_value = slider_start_value # Keep track of the current value

while is_running:
    time_delta = clock.tick(60) / 1000.0  # Limit to 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        # --- Handle UI events ---
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == value_slider:
                    new_value = int(event.value) # Get the new integer value
                    if new_value != current_slider_value: # Only update if value changed
                        current_slider_value = new_value
                        value_display_label.set_text(f"Value: {current_slider_value}")

                        # --- OSC Sending Logic ---
                        if osc_client:
                            try:
                                print(new_value)
                                osc_client.send_message(OSC_ADDRESS, current_slider_value)
                                # print(f"Sent OSC: {OSC_ADDRESS} {current_slider_value}") # For debugging
                            except Exception as e:
                                print(f"Error sending OSC message: {e}")
                                # This might happen if the OSC server isn't running

        manager.process_events(event) # Let pygame_gui handle its events

    # Update the GUI manager
    manager.update(time_delta)

    # --- Drawing ---
    screen.fill((20, 20, 20)) # Dark background
    manager.draw_ui(screen) # Draw all GUI elements

    pygame.display.flip()

pygame.quit()
sys.exit()