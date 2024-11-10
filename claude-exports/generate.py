import os
import json
from datetime import datetime

# Define the input and output directories
input_dir = os.path.join(os.getcwd(), "data")
output_dir = os.path.join(os.getcwd(), "output")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Get a list of all JSON files in the input directory
json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]

# Sort the files by date (assuming the date is part of the filename)
def extract_date(filename):
    try:
        return datetime.strptime(filename.split('-')[1], '%Y%m%d%H%M%S')
    except (IndexError, ValueError):
        return datetime.min

json_files.sort(key=extract_date)

# Process each JSON file
for json_file in json_files:
    input_file = os.path.join(input_dir, json_file)

    # Read the JSON file
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Process each chat
    for chat in data:
        chat_name = chat.get("name", "Unnamed Chat").replace(" ", "_").replace("\"", "")
        chat_messages = chat.get("chat_messages", [])

        # Skip empty conversations
        if not chat_messages:
            continue

        # Sort messages by created_at or updated_at timestamp
        chat_messages.sort(key=lambda x: x.get('created_at', x.get('updated_at', '')))

        # Define the output file path
        output_file = os.path.join(output_dir, f"{chat_name}.txt")

        # Write the markdown representation to the output file
        with open(output_file, "w", encoding="utf-8") as txt_file:
            txt_file.write(f"# {chat.get('name', 'Unnamed Chat')}\n\n")
            for message in chat_messages:
                sender = message.get("sender", "unknown")
                text = message.get("text", "")
                txt_file.write(f"**{sender}**: {text}\n\n")

print("Text files have been generated in the output directory.")