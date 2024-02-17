# MinuteDB

MinuteDB is a simple local database written in Python that provides basic CRUD (Create, Read, Update, Delete) operations on a local file-based database. It is designed to be lightweight and easy to use.

## Installation

You can install MinuteDB using pip:

```bash
pip install minutedb
```

## Usage

### Importing MinuteDB
```python
from minutedb import MinuteDB
```

### Create an instance of MinuteDB
```python
# Format: 
db = MinuteDB(<table_name>, <primary_key>)
# Example:
db = MinuteDB("users", "name")
```
If the table already exist, then the primary key need not be specified.
```python
# Format: 
db = MinuteDB(<table_name>)
# Example:
db = MinuteDB("users")
```

### Create items
```python
# Format:
db.create_item({<primary_key>: <value>, <key1>: <value1>, <key2>: <value2>, ...})
# Example:
db.create_item({"name": "Alice", "age": 30, "height": 6.1})
db.create_item({"name": "Bob", "age": 20, "height": 5.7})
db.create_item({"name": "Eve", "age": 40, "height": 5.11})
```

### Read an item
The read operation needs only the primary key to be specified.
```python
# Format: 
db.get_item(<primary_key>)
# Example:
db.get_item("Alice")
```

### Update an item
The update operation needs the primary key as well as the updated key-value pair(s) in dictionaly format to be specified.
```python
# Format: 
db.update_item(<primary_key>, {<key>: <updated_value>})
# Example:
db.update_item("Alice", {"age": 31})
```
You can update multiple attributes also.
```python
# Format: 
db.update_item(<primary_key>, {<key1>: <updated_value1>, <key2>: <updated_value2>})
# Example:
db.update_item("Eve", {"age": 35, "height": 5.5})
```
You cannot update the value of the primary key itself.

### Scan to find an item
The scan operation searches the items using key-value pair in dictionaly format. The search key must not contain the the primary key attribute. The return type will be a list of dictionaries.
```python
# Format: 
db.update_item({<key>: <value>})
# Example:
db.scan_item({"age": 40})
```
You can scan using multiple key-value pairs also.
```python
# Format: 
db.update_item({<key1>: <value1>, <key2>: <value2>})
# Example:
db.scan_item({"age": 20, "height": 5.7})
```

### Delete an item
The delete operation deletes the item from the database using only the primary key.
```python
# Format: 
db.delete_item(<primary_key>)
# Example:
db.delete_item("Eve")
```