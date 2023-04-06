import unittest
import os
import MyKeyring


class TestMyKeyring(unittest.TestCase):

    def setUp(self):
        # creates a temporary file for testing
        self.file_path = 'temp_keyring.json'
        self.keyring = MyKeyring.MyKeyring(file_path=self.file_path)

    def tearDown(self):
        # removes the temporary file after testing
        os.remove(self.file_path)

    def test_set_password(self):
        # sets a password and checks if it can be retrieved
        self.keyring.set_password('Gmail', 'user123', 'password123')
        self.assertEqual(self.keyring.get_password('Gmail', 'user123'), 'password123')

    def test_get_password(self):
        # retrieves a password that was previously set
        self.keyring.set_password('Facebook', 'johndoe', 'qwerty123')
        self.assertEqual(self.keyring.get_password('Facebook', 'johndoe'), 'qwerty123')

    def test_delete_password(self):
        # sets a password, deletes it, and checks if it was deleted
        self.keyring.set_password('Twitter', 'janedoe', 'abcdefg')
        self.keyring.delete_password('Twitter', 'janedoe')
        self.assertIsNone(self.keyring.get_password('Twitter', 'janedoe'))

    def test_delete_nonexistent_password(self):
        # tries to delete a password that was not set, and checks if a KeyError was raised
        with self.assertRaises(KeyError):
            self.keyring.delete_password('LinkedIn', 'markzuckerberg')

    def test_invalid_file_path(self):
        # tries to create a keyring with an invalid file path, and checks if an exception was raised
        with self.assertRaises(Exception):
            MyKeyring.MyKeyring(file_path='nonexistent_directory/temp_keyring.json')

    def test_invalid_json_file(self):
        # tries to load a keyring from an invalid JSON file, and checks if an exception was raised
        with open(self.file_path, 'w') as file:
            file.write('invalid json')
        with self.assertRaises(Exception):
            MyKeyring.MyKeyring(file_path=self.file_path)


if __name__ == '__main__':
    unittest.main()
