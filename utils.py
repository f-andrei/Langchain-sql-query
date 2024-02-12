import json

def save_fname(fname: str):
    """Save the provided filename to a JSON file."""
    try:
        with open('fname.json', 'w') as file:
            filename = {"filename": fname.lower()}
            json.dump(filename, file)
    except Exception as e:
        print("Error occurred while saving filename:", e)

def load_fname():
    """Load the filename from the JSON file."""
    try:
        with open('fname.json', 'r') as file:
            data = json.load(file)
            return data.get("filename")
    except FileNotFoundError:
        print("No saved filename found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON data from file.")
        return None
    except Exception as e:
        print("Error occurred while loading filename:", e)
        return None
