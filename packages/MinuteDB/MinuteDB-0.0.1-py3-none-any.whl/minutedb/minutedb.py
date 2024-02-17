import os
import json
from .utils import *
from filelock import FileLock
DB_DIR, DATA_FILE = "db", "data.json"


class MinuteDB:

    def __init__(self, table_name, primary_key=None):
        self.table_name = table_name
        self.primary_key = primary_key
        self.data_file_path = os.path.join(DB_DIR, table_name, DATA_FILE)
        self.lock = FileLock(f"{self.data_file_path}.lock")
        if primary_key:
            if not os.path.exists(self.data_file_path):
                self._create_table()
            else:
                self._load_data()
                if primary_key != self.data.get("__primary_key__"):
                    raise KeyError(f"The primary key attribute '{primary_key}' is not matching.")
        else:
            if not os.path.exists(self.data_file_path):
                raise KeyError(f"The table '{table_name}' does not exist.")
            else:
                self._load_data()
                self.primary_key = self.data.get("__primary_key__")

    def _create_table(self):
        data_table_path = os.path.join(DB_DIR, self.table_name)
        if not os.path.exists(data_table_path):
            os.makedirs(data_table_path)
        os.mknod(self.data_file_path)
        self.data = {
            "__primary_key__": self.primary_key
        }
        self._save_data()

    def _load_data(self):
        if os.path.exists(self.data_file_path):
            with self.lock:
                with open(self.data_file_path, "r") as f:
                    self.data = json.load(f)
        else:
            self.data = {}

    def _save_data(self):
        with self.lock:
            with open(self.data_file_path, "w") as f:
                json.dump(self.data, f)

    def create_item(self, data):
        if self.primary_key not in data:
            raise KeyError(f"The primary key '{self.primary_key}' is not found in the data.")
        value_for_primary_key = data[self.primary_key]
        if self.data.get(value_for_primary_key) is None:
            self.data[value_for_primary_key] = data
            self._save_data()
            print(f"Record with {self.primary_key} '{value_for_primary_key}' created successfully.")
        else:
            raise KeyError(f"Record with {self.primary_key} '{value_for_primary_key}' already exist.")

    def get_item(self, key):
        if key not in self.data:
            raise KeyError(f"Record with {self.primary_key} '{key}' not found.")
        return self.data[key]

    def update_item(self, key, updated_dict):
        if key not in self.data:
            raise KeyError(f"Record with {self.primary_key} '{key}' not found.")
        if self.primary_key in updated_dict.keys():
            raise KeyError(f"The primary key '{self.primary_key}' cannot be updated.")
        self.data[key] = {**self.data[key], **updated_dict}
        self._save_data()
        print(f"Record with {self.primary_key} '{key}' updated successfully.")

    def scan_item(self, search_dict):
        data_list = list(self.data.values())
        data_list.remove(self.primary_key)
        print("Scanning ...")
        return search_in_list(search_dict, data_list)

    def delete_item(self, key):
        if key not in self.data:
            raise KeyError(f"Record with {self.primary_key} '{key}' not found.")
        del self.data[key]
        self._save_data()
        print(f"Record with {self.primary_key} '{key}' deleted successfully.")


if __name__ == "__main__":
    db = MinuteDB("users", "name")

    # Create
    db.create_item({"name": "Alice", "age": 30, "height": 6.1})
    db.create_item({"name": "Bob", "age": 20, "height": 5.7})
    db.create_item({"name": "Eve", "age": 40, "height": 5.11})

    # Read
    print(db.get_item("Alice"))

    # Update
    db.update_item("Alice", {"age": 31})

    # Scan
    print(db.scan_item({"age": 40}))

    # Delete
    db.delete_item("Eve")

