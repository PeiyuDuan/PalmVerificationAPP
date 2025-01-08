from .database import PalmPrintDatabase
import core
import numpy as np


def _are_features_similar(feature1, feature2):
    """
    Compare two palm print features to determine if they are similar.

    Args:
        feature1 (np.ndarray): The first feature vector.
        feature2 (np.ndarray): The second feature vector.

    Returns:
        bool: True if features are similar based on the defined validation rate, False otherwise.
    """
    return core.calculate_cosine_similarity(feature1, feature2) > core.validate_rate


class PalmPrintService:
    def __init__(self):
        """
        Initialize the PalmPrintService and connect to the palm print database.
        """
        self.database = PalmPrintDatabase()

    def register_user(self, username: str, left_palm_image: np.ndarray, right_palm_image: np.ndarray):
        """
        Register a new user with their left and right palm print images.

        Args:
            username (str): The name of the user to register.
            left_palm_image (np.ndarray): Image of the user's left palm.
            right_palm_image (np.ndarray): Image of the user's right palm.

        Returns:
            bool: True if registration is successful.

        Raises:
            ValueError: If the username or palm prints already exist in the database.
        """
        # Extract features from the left and right palm images
        left_feature = core.get_palm_print_feature(left_palm_image)
        right_feature = core.get_palm_print_feature(right_palm_image)

        # Retrieve all existing user information from the database
        all_users = self.database.get_all_info()

        # Check if the username or palm prints already exist
        for user in all_users:
            if user['name'] == username:
                raise ValueError(f"User with name {username} already exists!")
            if _are_features_similar(user['left_feature'], left_feature):
                raise ValueError("Left palm print already registered!")
            if _are_features_similar(user['right_feature'], right_feature):
                raise ValueError("Right palm print already registered!")

        # Insert new user information into the database
        self.database.insert_palm_print(username, left_feature, right_feature)
        print(f"User {username} registered successfully with palm print features.")
        return True

    def login_by_username(self, username: str, palm_image: np.ndarray):
        """
        Authenticate a user by their username and a palm print image.

        Args:
            username (str): The name of the user.
            palm_image (np.ndarray): The palm print image provided for authentication.

        Returns:
            list: A list containing a boolean indicating success and the hand type ("left" or "right").
        """
        # Extract features from the provided palm image
        input_feature = core.get_palm_print_feature(palm_image)

        # Retrieve the user's palm print features from the database
        user_palm_data = self.database.get_palm_print_by_name(username)
        left_feature = user_palm_data[0]
        right_feature = user_palm_data[1]

        # Check if the input feature matches either the left or right palm feature
        if _are_features_similar(input_feature, left_feature):
            print(f"Login successful for {username}")
            return [True, "left"]
        elif _are_features_similar(input_feature, right_feature):
            print(f"Login successful for {username}")
            return [True, "right"]
        else:
            print("Login failed. No matching palm prints found.")
            return [False, None]

    def login_with_palm_image(self, palm_image: np.ndarray):
        """
        Authenticate a user with a palm print image without providing a username.

        Args:
            palm_image (np.ndarray): The palm print image provided for authentication.

        Returns:
            tuple: A tuple containing the username and hand type ("left" or "right"), or None if authentication fails.
        """
        # Extract features from the provided palm image
        input_feature = core.get_palm_print_feature(palm_image)

        # Retrieve all user information from the database
        all_users = self.database.get_all_info()

        # Compare the input feature against all stored palm features
        for user in all_users:
            stored_left_feature = user['left_feature']
            stored_right_feature = user['right_feature']

            if _are_features_similar(input_feature, stored_left_feature):
                print(f"Login successful for {user['name']}")
                return user['name'], "left"
            if _are_features_similar(input_feature, stored_right_feature):
                print(f"Login successful for {user['name']}")
                return user['name'], "right"

        # If no matching user is found
        print("Login failed. No matching palm prints found.")
        return None

    def update_user_palm_data(self, username: str, left_palm_image: np.ndarray = None,
                              right_palm_image: np.ndarray = None):
        """
        Update the palm print data for an existing user.

        Args:
            username (str): The name of the user to update.
            left_palm_image (np.ndarray, optional): New left palm image. Defaults to None.
            right_palm_image (np.ndarray, optional): New right palm image. Defaults to None.
        """
        if left_palm_image is not None:
            # Extract and update the left palm feature
            left_feature = core.get_palm_print_feature(left_palm_image)
            self.database.update_left_palm_print(username, left_feature)

        if right_palm_image is not None:
            # Extract and update the right palm feature
            right_feature = core.get_palm_print_feature(right_palm_image)
            self.database.update_right_palm_print(username, right_feature)

        print(f"User {username}'s palm print information updated.")
