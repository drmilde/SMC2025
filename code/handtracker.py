import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def trackHands(self, image):
        """
        Tracks hands in an image and returns the annotated image.

        Args:
            image (numpy.ndarray): The input image (BGR format).

        Returns:
            numpy.ndarray: The image with hands annotated, or the original image
                           if no hands are detected.
        """
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(image_rgb)
        annotated_image = image.copy()

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(annotated_image, hand_landmarks,
                                            self.mp_hands.HAND_CONNECTIONS)
        return annotated_image

    def getThumbAngles(self):
        """
        Calculates and returns the angles of the thumbs if hands are detected.

        Returns:
            tuple: A tuple containing two float values representing the angles
                   of the left and right thumbs, respectively. Returns (None, None)
                   if hands are not detected or thumbs cannot be accurately determined.
        """
        left_thumb_angle = None
        right_thumb_angle = None

        if self.results and self.results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(self.results.multi_hand_landmarks):
                # Determine if it's a left or right hand (requires more sophisticated logic)
                # For simplicity, we'll assume the first detected hand is left and second is right
                # In a real application, you'd use hand_handedness from self.results.multi_handedness

                # Thumb tip (landmark 4), thumb IP joint (landmark 3), thumb CMC joint (landmark 2)
                thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                thumb_ip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP]
                thumb_cmc = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_CMC]

                # Convert to numpy arrays for vector operations
                p_tip = np.array([thumb_tip.x, thumb_tip.y])
                p_ip = np.array([thumb_ip.x, thumb_ip.y])
                p_cmc = np.array([thumb_cmc.x, thumb_cmc.y])

                # Vectors for angle calculation
                vec1 = p_ip - p_cmc
                vec2 = p_tip - p_ip

                # Calculate dot product and magnitudes
                dot_product = np.dot(vec1, vec2)
                magnitude1 = np.linalg.norm(vec1)
                magnitude2 = np.linalg.norm(vec2)

                # Avoid division by zero
                if magnitude1 > 0 and magnitude2 > 0:
                    angle_rad = np.arccos(dot_product / (magnitude1 * magnitude2))
                    angle_deg = np.degrees(angle_rad)

                    # Assign based on simple assumption of hand order
                    if len(self.results.multi_hand_landmarks) == 1:
                        # If only one hand, can't determine left/right without more info
                        # We'll just assign it to left_thumb_angle for this simplified example
                        left_thumb_angle = angle_deg
                    elif hand_idx == 0:  # Assuming first detected is left
                        left_thumb_angle = angle_deg
                    elif hand_idx == 1: # Assuming second detected is right
                        right_thumb_angle = angle_deg

        return (left_thumb_angle, right_thumb_angle)


    def getLeftHandValues(self):
        """
        Returns an array of 2D coordinates for the left hand landmarks.

        Returns:
            list: A list of [x, y] coordinates for each landmark of the left hand.
                  Returns an empty list if no left hand is detected.
        """
        left_hand_landmarks = []
        if self.results and self.results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(self.results.multi_hand_landmarks):
                # A more robust way to identify left/right hand is needed in production
                # For this example, we'll assume the first detected hand is potentially the left hand
                # based on some heuristic or external knowledge.
                # In a real application, you would check self.results.multi_handedness[hand_idx].classification[0].label
                # to determine if it's 'Left' or 'Right'.

                # Placeholder for actual left hand detection
                # Let's assume the first hand found is the left hand for simplicity
                if hand_idx == 0: # This is a very simplistic assumption
                    for landmark in hand_landmarks.landmark:
                        left_hand_landmarks.append([landmark.x, landmark.y])
                    break # Assuming only one left hand

        return left_hand_landmarks

    def getRightHandValues(self):
        """
        Returns an array of 2D coordinates for the right hand landmarks.

        Returns:
            list: A list of [x, y] coordinates for each landmark of the right hand.
                  Returns an empty list if no right hand is detected.
        """
        right_hand_landmarks = []
        if self.results and self.results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(self.results.multi_hand_landmarks):
                # A more robust way to identify left/right hand is needed in production
                # For this example, we'll assume the second detected hand is potentially the right hand
                # based on some heuristic or external knowledge.
                # In a real application, you would check self.results.multi_handedness[hand_idx].classification[0].label
                # to determine if it's 'Left' or 'Right'.

                # Placeholder for actual right hand detection
                # Let's assume the second hand found (if any) is the right hand for simplicity
                if hand_idx == 1: # This is a very simplistic assumption
                    for landmark in hand_landmarks.landmark:
                        right_hand_landmarks.append([landmark.x, landmark.y])
                    break # Assuming only one right hand

        return right_hand_landmarks

if __name__ == '__main__':
    # Example Usage:
    tracker = HandTracker()

    # Create a dummy image for testing
    dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
    # You would typically load an image like:
    # image = cv2.imread('your_image.jpg')
    # Or use a webcam:
    # cap = cv2.VideoCapture(0)
    # ret, frame = cap.read()
    # annotated_frame = tracker.trackHands(frame)
    # cv2.imshow("Hand Tracking", annotated_frame)


    print("--- Testing trackHands ---")
    annotated_img = tracker.trackHands(dummy_image)
    cv2.imshow("Annotated Dummy Image (should be black)", annotated_img)
    cv2.waitKey(1000) # Display for 1 second
    cv2.destroyAllWindows()


    # Note: To get meaningful results for getThumbAngles, getLeftHandValues,
    # and getRightHandValues, you need to call trackHands with an image
    # that actually contains hands. The dummy_image will not yield hand detections.

    print("\n--- Testing with a simulated detection (for demonstration) ---")
    # Simulate a single hand detection for testing purposes
    class MockLandmark:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    class MockHandLandmarks:
        def __init__(self, landmarks_data):
            self.landmark = []
            for x, y, z in landmarks_data:
                self.landmark.append(MockLandmark(x, y, z))

    class MockResults:
        def __init__(self, multi_hand_landmarks):
            self.multi_hand_landmarks = multi_hand_landmarks
            # In a real scenario, multi_handedness would also be populated
            self.multi_handedness = None # For simplicity in this mock

    # Simulate a left hand (e.g., simplified thumb for angle calculation)
    # These coordinates are arbitrary for demonstration
    simulated_left_hand_landmarks_data = [
        (0.1, 0.2, 0), # Wrist (0)
        (0.2, 0.3, 0), # Thumb_CMC (2)
        (0.25, 0.35, 0), # Thumb_IP (3)
        (0.3, 0.4, 0), # Thumb_TIP (4)
        (0.15, 0.25, 0), # Index_finger_MCP (5)
        (0.2, 0.3, 0), # Index_finger_PIP (6)
        (0.25, 0.35, 0), # Index_finger_DIP (7)
        (0.3, 0.4, 0), # Index_finger_TIP (8)
        # ... add more landmarks as needed for a full hand
    ]
    simulated_left_hand = MockHandLandmarks(simulated_left_hand_landmarks_data)

    # Simulate a right hand
    simulated_right_hand_landmarks_data = [
        (0.8, 0.2, 0), # Wrist (0)
        (0.7, 0.3, 0), # Thumb_CMC (2)
        (0.65, 0.35, 0), # Thumb_IP (3)
        (0.6, 0.4, 0), # Thumb_TIP (4)
        (0.75, 0.25, 0), # Index_finger_MCP (5)
        (0.7, 0.3, 0), # Index_finger_PIP (6)
        (0.65, 0.35, 0), # Index_finger_DIP (7)
        (0.6, 0.4, 0), # Index_finger_TIP (8)
        # ... add more landmarks as needed for a full hand
    ]
    simulated_right_hand = MockHandLandmarks(simulated_right_hand_landmarks_data)


    # Assign the mocked results to the tracker instance
    tracker.results = MockResults([simulated_left_hand, simulated_right_hand])

    # Test getThumbAngles
    left_angle, right_angle = tracker.getThumbAngles()
    print(f"Thumb Angles: Left={left_angle:.2f} degrees, Right={right_angle:.2f} degrees")

    # Test getLeftHandValues
    left_hand_coords = tracker.getLeftHandValues()
    print("\nLeft Hand Coordinates (first 5 landmarks):")
    for i, coord in enumerate(left_hand_coords[:5]):
        print(f"  Landmark {i}: [{coord[0]:.2f}, {coord[1]:.2f}]")

    # Test getRightHandValues
    right_hand_coords = tracker.getRightHandValues()
    print("\nRight Hand Coordinates (first 5 landmarks):")
    for i, coord in enumerate(right_hand_coords[:5]):
        print(f"  Landmark {i}: [{coord[0]:.2f}, {coord[1]:.2f}]")