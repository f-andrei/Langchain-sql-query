import json
import re
import os


def save_fname(fname: str):
    """Saves the provided filename to a JSON file."""
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
    

def log_chat_history(chat_history, intermediate_steps):
    """
    Saves a comprehensive record of the model's thought process, covering the user's question, inputs,
    intermediate steps, and final answer.

    Args:
        chat_history (dict): A dictionary containing the chat history.
        intermediate_steps (list): A list of lists containing intermediate steps of the model.

    Raises:
        Exception: If an error occurs while saving the chat history.
    """
    # Extract user question and final answer
    user_question, final_answer = re.split(r'AI:|Final answer:', chat_history["chat_history"])
    user_question = user_question.replace("Human: ", "").strip()
    final_answer = final_answer.strip()

    # Prepare output data
    output_data = {
        "user_question": user_question,
        "final_answer": final_answer,
        "steps": []
    }

    # Populate steps
    for i, step in enumerate(intermediate_steps, start=1):
        for action in step:
            try:
                action_dict = action.dict()
                action_dict["step"] = i
                output_data["steps"].append(action_dict)
            except Exception as e:
                # Handle exceptions if necessary
                pass

    # Check if the output file exists
    output_file = 'output.json'
    if os.path.exists(output_file):
        # Load existing data from the file
        with open(output_file, 'r') as f:
            existing_data = json.load(f)
        
        # Append new record to existing data
        if "records" in existing_data:
            existing_data["records"].append(output_data)
        else:
            existing_data["records"] = [output_data]

        # Save updated data back to the file
        with open(output_file, 'w') as f:
            json.dump(existing_data, f, indent=4)
    else:
        # Save new data to the file
        with open(output_file, 'w') as f:
            json.dump({"records": [output_data]}, f, indent=4)