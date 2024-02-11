import json

def save_fname(fname):
    """Save the provided filename to a JSON file."""
    try:
        with open('fname.json', 'w') as file:
            file_name = {"file_name": fname}
            json.dump(file_name, file)
    except Exception as e:
        print("Error occurred while saving filename:", e)

def load_fname():
    """Load the filename from the JSON file."""
    try:
        with open('fname.json', 'r') as file:
            data = json.load(file)
            return data.get("file_name")
    except FileNotFoundError:
        print("No saved filename found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON data from file.")
        return None
    except Exception as e:
        print("Error occurred while loading filename:", e)
        return None
