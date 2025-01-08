from flask import Blueprint, request, jsonify
from .server import PalmPrintService  # Import the PalmPrintService class
import cv2
import numpy as np
import base64

# Initialize the PalmPrintService
palm_print_service = PalmPrintService()

# Create a Flask Blueprint for routes
palm_print_routes = Blueprint('palm_print_routes', __name__)


def decode_image(image_data):
    """
    Decode base64-encoded image to a NumPy array.

    Args:
        image_data (str): The base64-encoded image string.

    Returns:
        np.ndarray: Decoded image as a NumPy array.
    """
    # Remove the base64 header if present (i.e., 'data:image/jpeg;base64,')
    if image_data.startswith('data:image'):
        image_data = image_data.split(',')[1]
    else:
        raise ValueError("Invalid image data format. Must be a base64-encoded image.")

    # Decode the base64 string to bytes
    image_data = base64.b64decode(image_data)

    # Convert the bytes to a NumPy array
    np_arr = np.frombuffer(image_data, np.uint8)

    # Decode the image from the NumPy array
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


@palm_print_routes.route('/register', methods=['POST'])
def register_user():
    """
    Register a new user with left and right palm print images.

    Request JSON:
        {
            "username": "string",
            "left_palm_image": "base64_string",
            "right_palm_image": "base64_string"
        }

    Returns:
        JSON response with success status or error message.
    """
    data = request.get_json()
    username = data.get('username')

    try:
        left_palm_image = decode_image(data.get('left_palm_image'))
        right_palm_image = decode_image(data.get('right_palm_image'))
        palm_print_service.register_user(username, left_palm_image, right_palm_image)
        return jsonify({"message": f"User {username} registered successfully!"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@palm_print_routes.route('/login', methods=['POST'])
def login():
    """
    Login a user using username and a palm print image.

    Request JSON:
        {
            "username": "string",
            "palm_image": "base64_string"
        }

    Returns:
        JSON response with login status and hand type.
    """
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required for this endpoint."}), 400

    try:
        if not data.get('palm_image'):
            raise ValueError("Palm image is required for this endpoint.")
        palm_image = decode_image(data.get('palm_image'))
        success, hand = palm_print_service.login_by_username(username, palm_image)
        if success:
            return jsonify({"message": "Login successful", "hand": hand}), 200
        else:
            return jsonify({"message": "Login failed"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@palm_print_routes.route('/plain-login', methods=['POST'])
def plain_login():
    """
    Login a user using only a palm print image.

    Request JSON:
        {
            "palm_image": "base64_string"
        }

    Returns:
        JSON response with the username and hand type or error message.
    """
    data = request.get_json()

    try:
        palm_image = decode_image(data.get('palm_image'))
        result = palm_print_service.login_with_palm_image(palm_image)
        if result:
            username, hand = result
            return jsonify({"message": "Login successful", "username": username, "hand": hand}), 200
        else:
            return jsonify({"message": "Login failed"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@palm_print_routes.route('/update-user', methods=['PUT'])
def update_user_info():
    """
    Update user's palm print data.

    Request JSON:
        {
            "username": "string",
            "left_palm_image": "base64_string (optional)",
            "right_palm_image": "base64_string (optional)"
        }

    Returns:
        JSON response with update status or error message.
    """
    data = request.get_json()
    username = data.get('username')

    try:
        left_palm_image = decode_image(data.get('left_palm_image')) if data.get('left_palm_image') else None
        right_palm_image = decode_image(data.get('right_palm_image')) if data.get('right_palm_image') else None
        palm_print_service.update_user_palm_data(username, left_palm_image, right_palm_image)
        return jsonify({"message": f"User {username}'s palm print data updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
