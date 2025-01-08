import cv2
import mediapipe as mp
import math
from typing import Any
import numpy as np

# Initialize MediaPipe Hand Detection Model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)


def _get_middle_finger_angle(hand_landmarks: Any) -> float:
    """
    Calculate the rotation angle of the middle finger.

    Args:
        hand_landmarks (Any): The detected hand landmarks from MediaPipe.

    Returns:
        float: The angle (in degrees) between the base and tip of the middle finger.
    """
    # Get the base and tip positions of the middle finger
    base = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

    # Calculate the angle between the base and tip
    x1, y1 = base.x, base.y
    x2, y2 = tip.x, tip.y
    angle = math.atan2(y2 - y1, x2 - x1) * 180 / math.pi  # Convert radians to degrees
    return angle


def _rotate_image(image: Any, angle: float) -> Any:
    """
    Rotate the given image by the specified angle.

    Args:
        image (Any): The input image in OpenCV format (BGR).
        angle (float): The angle (in degrees) to rotate the image.

    Returns:
        Any: The rotated image.
    """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    # Compute the rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Apply the rotation
    rotated_image = cv2.warpAffine(image, rotation_matrix, (w, h))
    return rotated_image


def align_hand_image(image: cv2.Mat | np.ndarray[Any, np.dtype] | np.ndarray) -> Any:
    """
    Process a hand image to align it based on the middle finger orientation.

    Args:
        image (cv2.Mat | np.ndarray[Any, np.dtype] | np.ndarray): The image in opencv format (BGR).

    Returns: The rotated image as a NumPy ndarray in RGB format (OpenCV image),
             or None if no hand is detected.
    """

    # Convert the image to RGB (MediaPipe uses RGB format)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Detect hand landmarks
    results: Any = hands.process(image_rgb)
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            # Get the rotation angle of the middle finger
            angle = _get_middle_finger_angle(landmarks)
            print(f"Middle finger rotation angle: {angle} degrees")

            # Calculate the rotation angle to align the middle finger vertically
            rotation_angle = angle + 90
            print(f"Rotation angle to align middle finger: {rotation_angle} degrees")

            # Rotate the image
            rotated_image = _rotate_image(image, rotation_angle)

            return rotated_image

    return None
