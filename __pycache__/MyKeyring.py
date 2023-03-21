import hashlib
import json
import os


class MyKeyring:

    def __init__(self, file_path: str = None):
        """
        :param file_path: <String> the path of the keyring file.
               If the file does not exists there will create a new keyring file in that path.
               If not specified,  by default a new file 'My_Keyring.json' will be created in the path where the file is.
        """
        if file_path is None:
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'My_Keyring.json')

        self.__file_path = file_path
        self.__keys = {}
        self.__load_keys()

    def __load_keys(self):
        """
        Tries to open the file and load the keys.
        handles specific cases...
        """
        try:
            # tries to read from the file
            with open(self.__file_path, 'r') as file:
                try:
                    # try to load from the file to __keys
                    self.__keys = json.load(file)
                except json.JSONDecodeError as e:
                    # if the file is not a valid JSON. raising an exception
                    raise Exception(f"Error: Invalid JSON file '{self.__file_path}'.") from e
        except FileNotFoundError:
            # if the file specified by file_path not found. tries to create a new file with empty dict
            with open(self.__file_path, 'w') as file:
                json.dump({}, file)
        except IOError as e:
            # if the path is invalid. raising an exception
            raise Exception(f"Error: Invalid file path '{self.__file_path}'.") from e

    def __save_keys(self):
        """
        Saves the loaded keys (__keys) to the file as JSON.
        """
        with open(self.__file_path, 'w') as file:
            json.dump(self.__keys, file)

    def set_password(self, service_name: str, username: str, password: str):
        """
        Generate a key by hashing the service name and username with SHA-256.
        The password is then stored in the keys dictionary with the key as the SHA-256 digest.
        At the end, the keys dictionary is being saved to the file as JSON.
        :param service_name: <String> The service name for the password.
        :param username: <String> The username for the password.
        :param password: <String> The password to store with the following identifiers (service name and username).
        """
        key = hashlib.sha256(service_name.encode('utf-8') + username.encode('utf-8')).hexdigest()
        self.__keys[key] = password
        self.__save_keys()

    def get_password(self, service_name: str, username: str):
        """
        Generate a key by hashing the service name and username with SHA-256.
        The key is then used to look up the corresponding password in the keys dictionary.
        :param service_name: <String> The service name for the password.
        :param username: <String> The username for the password.
        :return: <String> The password matches the identifiers entered, or None if not found.
        """
        key = hashlib.sha256(service_name.encode('utf-8') + username.encode('utf-8')).hexdigest()
        if key in self.__keys:
            return self.__keys[key]
        else:
            return None

    def delete_password(self, service_name, username):
        """
        Generate a key by hashing the service name and username with SHA-256.
        The key is then used to delete the corresponding entry from the keys dict.  (if not exists -> exception raised)
         At the end, the keys dictionary is being saved to the file.
        :param service_name: <String> The service name for the password.
        :param username: <String> The username for the password.
        """
        key = hashlib.sha256(service_name.encode('utf-8') + username.encode('utf-8')).hexdigest()
        if key in self.__keys:
            del self.__keys[key]
            self.__save_keys()
        else:
            raise KeyError(f"No password found for {service_name} and {username}")
