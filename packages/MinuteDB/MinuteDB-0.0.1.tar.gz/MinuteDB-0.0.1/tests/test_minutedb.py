import os
import unittest
from src.minutedb.minutedb import MinuteDB

class TestMinuteDB(unittest.TestCase):

    def setUp(self):
        # Create a test instance of MinuteDB
        self.db = MinuteDB("test_table", "id")

    def tearDown(self):
        # Clean up test data
        if os.path.exists(os.path.join("db", "test_table", "data.json")):
            os.remove(os.path.join("db", "test_table", "data.json"))
        if os.path.exists(os.path.join("db", "test_table", "data.json.lock")):
            os.remove(os.path.join("db", "test_table", "data.json.lock"))
        if os.path.exists(os.path.join("db", "test_table")):
            os.rmdir(os.path.join("db", "test_table"))

    def test_create_item(self):
        data = {"id": "1", "name": "Alice", "age": 30, "height": 6.1}
        self.db.create_item(data)
        result = self.db.get_item("1")
        self.assertEqual(result, data)

    def test_get_item(self):
        data = {"id": "1", "name": "Alice", "age": 30, "height": 6.1}
        self.db.create_item(data)
        result = self.db.get_item("1")
        self.assertEqual(result, data)

    def test_update_item(self):
        data = {"id": "1", "name": "Alice", "age": 30, "height": 6.1}
        self.db.create_item(data)
        self.db.update_item("1", {"age": 31})
        updated_data = self.db.get_item("1")
        self.assertEqual(updated_data["age"], 31)

    def test_scan_item(self):
        data1 = {"id": "1", "name": "Alice", "age": 30, "height": 6.1}
        data2 = {"id": "2", "name": "Bob", "age": 25, "height": 5.9}
        self.db.create_item(data1)
        self.db.create_item(data2)
        result = self.db.scan_item({"age": 30})
        self.assertEqual(result, [data1])

    def test_delete_item(self):
        data = {"id": "1", "name": "Alice", "age": 30, "height": 6.1}
        self.db.create_item(data)
        self.db.delete_item("1")
        with self.assertRaises(KeyError):
            self.db.get_item("1")

if __name__ == "__main__":
    unittest.main()
