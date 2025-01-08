from typing import Any

import torch
import torch.nn as nn
import torchvision.transforms as transforms
import cv2
from PIL import Image
from .hand_image_aligner import align_hand_image
from .roi_extractor import ImageROIExtractor
from .model import MobileFaceNet
import numpy as np
import os

# Load the model once, outside the function
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
net = MobileFaceNet().to(device)

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, '..', 'weights', 'mobile_face.pth')
net.load_state_dict(torch.load(model_path, map_location=device))
net.eval()

# Define the image transformation pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224), interpolation=transforms.InterpolationMode.NEAREST),
    transforms.ToTensor(),
    transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
])


def get_palm_print_feature(image: cv2.Mat | np.ndarray[Any, np.dtype] | np.ndarray) -> np.ndarray:
    """
    Get the palm print feature from the input image.

    Args:
        image (cv2.Mat | np.ndarray[Any, np.dtype] | np.ndarray): The image in opencv format (BGR).

    Returns:
        np.ndarray: The palm print feature extracted from the input image.
    """
    # Align the hand image
    aligned_image = align_hand_image(image)
    if aligned_image is None:
        print("No hand detected in the image.")

    # Extract ROI (Region of Interest)
    roi = ImageROIExtractor.get_roi(aligned_image)
    if roi is None:
        print("ROI extracted error in the image.")

    # Convert to RGB and apply transformations
    image = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    img_tensor = transform(image).unsqueeze(0).to(device)  # Directly move tensor to device

    # Extract feature vector
    with torch.no_grad():
        feature_vector = net(img_tensor)

    # Normalize the feature vector
    feature_vector = nn.functional.normalize(feature_vector).cpu().numpy()

    return feature_vector


def calculate_cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Calculate the cosine similarity between two vectors.

    Args:
        vector_a (np.ndarray): The first feature vector.
        vector_b (np.ndarray): The second feature vector.

    Returns:
        float: The cosine similarity between the two vectors.
    """
    # Compute the dot product of the vectors
    dot_product = np.dot(vector_a, vector_b.T)

    # Compute the norms (magnitudes) of the vectors
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    # Calculate cosine similarity
    cosine_similarity = dot_product / (norm_a * norm_b)

    return cosine_similarity
