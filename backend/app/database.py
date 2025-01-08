import pymysql
import pickle
import numpy as np
from .config import db_config


class PalmPrintDatabase:
    def __init__(self):
        """
        Initialize the PalmPrintDatabase class with the database configuration.
        """
        self.db_config = db_config

    def _get_db_connection(self):
        """
        Establish and return a database connection.

        Returns:
            pymysql.connections.Connection: A connection to the database.
        """
        return pymysql.connect(**self.db_config)

    @staticmethod
    def _serialize_feature(feature: np.ndarray) -> bytes:
        """
        Serialize the feature array into BLOB data.

        Args:
            feature (np.ndarray): The feature array to serialize.

        Returns:
            bytes: The serialized feature in bytes format.
        """
        return pickle.dumps(feature)

    @staticmethod
    def _deserialize_feature(feature_blob: bytes) -> np.ndarray:
        """
        Deserialize the BLOB data into a feature array.

        Args:
            feature_blob (bytes): The BLOB data to deserialize.

        Returns:
            np.ndarray: The deserialized feature array.
        """
        return pickle.loads(feature_blob)

    def update_left_palm_print(self, name: str, left_feature: np.ndarray):
        """
        Update the left palm print feature in the database.

        Args:
            name (str): The name of the user.
            left_feature (np.ndarray): The left palm print feature array.

        Returns:
            None
        """
        feature_blob = self._serialize_feature(left_feature)
        connection = self._get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE palm_print_data SET left_feature = %s WHERE name = %s"
                cursor.execute(sql, (feature_blob, name))
                connection.commit()
                print(f"Updated left palm print for {name}")
        finally:
            connection.close()

    def update_right_palm_print(self, name: str, right_feature: np.ndarray):
        """
        Update the right palm print feature in the database.

        Args:
            name (str): The name of the user.
            right_feature (np.ndarray): The right palm print feature array.

        Returns:
            None
        """
        feature_blob = self._serialize_feature(right_feature)
        connection = self._get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE palm_print_data SET right_feature = %s WHERE name = %s"
                cursor.execute(sql, (feature_blob, name))
                connection.commit()
                print(f"Updated right palm print for {name}")
        finally:
            connection.close()

    def insert_palm_print(self, name: str, left_feature: np.ndarray, right_feature: np.ndarray):
        """
        Insert a new user and their palm print features into the database.

        Args:
            name (str): The name of the user.
            left_feature (np.ndarray): The left palm print feature array.
            right_feature (np.ndarray): The right palm print feature array.

        Returns:
            None
        """
        left_feature_blob = self._serialize_feature(left_feature)
        right_feature_blob = self._serialize_feature(right_feature)
        connection = self._get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """INSERT INTO palm_print_data (name, left_feature, right_feature)
                         VALUES (%s, %s, %s)"""
                cursor.execute(sql, (name, left_feature_blob, right_feature_blob))
                connection.commit()
                print(f"Inserted palm print data for {name}")
        finally:
            connection.close()

    def get_palm_print_by_name(self, name: str):
        """
        Retrieve the left and right palm print features by username.

        Args:
            name (str): The name of the user.

        Returns: Tuple[np.ndarray, np.ndarray]: A tuple containing the left and right palm print features, or (None,
        None) if no data is found.
        """
        connection = self._get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT left_feature, right_feature FROM palm_print_data WHERE name = %s"
                cursor.execute(sql, (name,))
                result = cursor.fetchone()
                if result:
                    left_feature_blob, right_feature_blob = result
                    left_feature = PalmPrintDatabase._deserialize_feature(left_feature_blob)
                    right_feature = PalmPrintDatabase._deserialize_feature(right_feature_blob)
                    return left_feature, right_feature
                else:
                    print(f"No palm print data found for {name}")
                    return None, None
        finally:
            connection.close()

    def get_all_info(self):
        """
        Retrieve all records from the palm print database.

        Returns: List[Dict[str, Any]]: A list of dictionaries containing all user data, including names and palm
        print features.
        """
        connection = self._get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT name, left_feature, right_feature FROM palm_print_data"
                cursor.execute(sql)
                result = cursor.fetchall()
                all_palm_prints = []
                for record in result:
                    name, left_feature_blob, right_feature_blob = record
                    left_feature = PalmPrintDatabase._deserialize_feature(left_feature_blob)
                    right_feature = PalmPrintDatabase._deserialize_feature(right_feature_blob)
                    all_palm_prints.append({
                        'name': name,
                        'left_feature': left_feature,
                        'right_feature': right_feature
                    })
                return all_palm_prints
        finally:
            connection.close()
