from ultralytics import YOLO
import math
import numpy as np
import cv2
import gc
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, '..', 'weights', 'yolo.onnx')

model = YOLO(model_path, task='detect')
confidence = 0.5


class ImageROIExtractor:
    """
    A class for detecting and extracting the region of interest (ROI) in images using a YOLO model.
    """

    @staticmethod
    def _detect_objects(image) -> tuple:
        """
        Detect objects in the image using the YOLO model.

        Args:
            image (ndarray): Input image.

        Returns: tuple: Lists of detections for the primary category (primary_category) and secondary category (
        secondary_category).
        """
        predictions = model.predict(source=image, imgsz=512)
        results = predictions[0]

        preprocess_time = results.speed['preprocess']
        inference_time = results.speed['inference']
        postprocess_time = results.speed['postprocess']
        print(f"[INFO] YOLO took {preprocess_time + inference_time + postprocess_time} ms")

        boxes = []
        primary_category = []
        secondary_category = []

        for box in results.boxes:
            if box.conf > confidence:
                boxes.append(box)

        for box in boxes:
            x, y, w, h = box.xywh[0]
            conf = box.conf
            cls = box.cls

            if cls == 0:
                primary_category.append([x, y, w, h, conf])
            else:
                secondary_category.append([x, y, w, h, conf])

        return primary_category, secondary_category

    @staticmethod
    def _rotate_point(x: float, y: float, angle: float) -> list:
        """
        Rotate a point around the origin.

        Args:
            x (float): X-coordinate of the point.
            y (float): Y-coordinate of the point.
            angle (float): Rotation angle in radians.

        Returns:
            list: Rotated point as [X, Y].
        """
        rotated_x = x * math.cos(angle) + y * math.sin(angle)
        rotated_y = y * math.cos(angle) - x * math.sin(angle)
        return [int(rotated_x), int(rotated_y)]

    @staticmethod
    def _extract_roi(image, primary_category, secondary_category) -> np.ndarray:
        """
        Extract the region of interest (ROI) from the image.

        Args:
            image (ndarray): Input image.
            primary_category (list): List of primary category detections.
            secondary_category (list): List of secondary category detections.

        Returns:
            ndarray: The extracted ROI image.
        """
        # Get image dimensions
        height, width = image.shape[:2]

        # Create a square canvas (padding the smaller side with white background)
        if width > height:
            padded_image = np.zeros((width, width, 3), np.uint8)
            padded_image[...] = 255  # Set the background to white
            padded_image[1:height, 1:width, :] = image[1:height, 1:width, :]
            canvas_size = width
        else:
            padded_image = np.zeros((height, height, 3), np.uint8)
            padded_image[...] = 255  # Set the background to white
            padded_image[1:height, 1:width, :] = image[1:height, 1:width, :]
            canvas_size = height

        # Define center of the padded image
        center = (canvas_size / 2, canvas_size / 2)

        # Extract coordinates of points from categories
        primary_x1, primary_y1 = float(primary_category[0][0]), float(primary_category[0][1])
        primary_x2, primary_y2 = float(primary_category[1][0]), float(primary_category[1][1])
        secondary_x, secondary_y = float(secondary_category[0][0]), float(secondary_category[0][1])

        # Compute the midpoint of the primary category
        center_x = (primary_x1 + primary_x2) / 2
        center_y = (primary_y1 + primary_y2) / 2

        # Calculate the length of the unit (distance between primary category points)
        unit_length = math.sqrt(np.square(primary_x2 - primary_x1) + np.square(primary_y2 - primary_y1))

        # Calculate the line equation for the primary category (Line AB)
        slope1 = (primary_y1 - primary_y2) / (primary_x1 - primary_x2)  # slope of AB
        intercept1 = primary_y1 - slope1 * primary_x1  # y-intercept of AB

        # Perpendicular line equation through the secondary category point (Line CD)
        slope2 = -1 / slope1  # slope of perpendicular line
        intercept2 = secondary_y - slope2 * secondary_x  # y-intercept of perpendicular line

        # Find intersection of Line AB and Line CD
        intersection_x = (intercept2 - intercept1) / (slope1 - slope2)
        intersection_y = slope1 * intersection_x + intercept1

        # Vector from intersection to secondary category point
        vector_x = secondary_x - intersection_x
        vector_y = secondary_y - intersection_y

        # Calculate the distance (length) of the vector
        vector_length = math.sqrt(np.square(vector_x) + np.square(vector_y))

        # Normalize the vector (to get unit direction)
        normalized_vector = [vector_x / vector_length, vector_y / vector_length]

        # Calculate the rotation angle based on the normalized vector direction
        if normalized_vector[1] < 0 < normalized_vector[0]:
            rotation_angle = math.pi / 2 - math.acos(normalized_vector[0])
        elif normalized_vector[1] < 0 and normalized_vector[0] < 0:
            rotation_angle = math.acos(-normalized_vector[0]) - math.pi / 2
        elif normalized_vector[1] >= 0 and normalized_vector[0] > 0:
            rotation_angle = math.acos(normalized_vector[0]) - math.pi / 2
        else:
            rotation_angle = math.pi / 2 - math.acos(-normalized_vector[0])

        # Rotate the midpoint of the primary category
        rotated_x, rotated_y = ImageROIExtractor._rotate_point(center_x - canvas_size / 2, center_y - canvas_size / 2,
                                                               rotation_angle)

        # Adjust coordinates back to the padded image center
        rotated_x += canvas_size / 2
        rotated_y += canvas_size / 2

        # Perform image rotation using OpenCV
        rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle / math.pi * 180, 1.0)
        rotated_image = cv2.warpAffine(padded_image, rotation_matrix, (canvas_size, canvas_size))

        # Extract the region of interest (ROI) based on the calculated coordinates and unit length
        roi = rotated_image[
              int(rotated_y + unit_length / 2):int(rotated_y + unit_length * 3),
              int(rotated_x - unit_length * 5 / 4):int(rotated_x + unit_length * 5 / 4),
              :
        ]

        if roi.shape[0] == 0 or roi.shape[1] == 0:
            raise ValueError("ROI extraction failed. Please provide a different image.")

        # Resize the extracted ROI to a fixed size (224x224)
        roi_resized = cv2.resize(roi, (224, 224), interpolation=cv2.INTER_CUBIC)

        return roi_resized

    @staticmethod
    def get_roi(image) -> np.ndarray:
        """
        Process the image to extract the ROI.

        Args:
            image (ndarray): Input image which is aligned.

        Returns:
            ndarray: The extracted ROI image.
        """
        primary_category, secondary_category = ImageROIExtractor._detect_objects(image)
        gc.collect()

        if len(primary_category) < 2:
            raise ValueError("Detection failed. Please provide a different image.")

        # Select the two most distant points if there are multiple detections
        if len(primary_category) > 2:
            primary_category = sorted(
                primary_category,
                key=lambda p: -math.sqrt((p[0] - primary_category[0][0]) ** 2 + (p[1] - primary_category[0][1]) ** 2)
            )[:2]

        secondary_category.sort(key=lambda x: x[-1], reverse=True)

        return ImageROIExtractor._extract_roi(image, primary_category, secondary_category)
