import cv2
import mediapipe as mp
import numpy as np

# Assuming HandTracker.py is in the same directory or accessible via PYTHONPATH
from handtracker import HandTracker

def main():
    """
    A small test program for the HandTracker class that reads live video from a webcam,
    tracks hands, and displays the annotated image.
    """
    hand_tracker = HandTracker()
    cap = cv2.VideoCapture(0)  # 0 for the default webcam

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press 'q' to exit the webcam feed.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Flip the frame horizontally for a natural mirror-like view
        frame = cv2.flip(frame, 1)

        # Track hands and get the annotated image
        annotated_frame = hand_tracker.trackHands(frame)

        # Display the annotated frame
        cv2.imshow("Hand Tracking - Live Feed", annotated_frame)

        # Optional: Get and print hand data (for debugging/demonstration)
        # You can uncomment these lines to see the output in the console
        # left_thumb_angle, right_thumb_angle = hand_tracker.getThumbAngles()
        # if left_thumb_angle is not None or right_thumb_angle is not None:
        #     print(f"Thumb Angles: Left={left_thumb_angle:.2f} deg, Right={right_thumb_angle:.2f} deg")

        # left_hand_coords = hand_tracker.getLeftHandValues()
        # if left_hand_coords:
        #     print(f"Left Hand Landmarks (first 5): {left_hand_coords[:5]}")

        # right_hand_coords = hand_tracker.getRightHandValues()
        # if right_hand_coords:
        #     print(f"Right Hand Landmarks (first 5): {right_hand_coords[:5]}")


        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and destroy all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam feed stopped.")

if __name__ == "__main__":
    main()