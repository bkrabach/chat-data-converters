import os
import xml.etree.ElementTree as ET
from datetime import datetime

# Define the input and output directories
input_dir = os.path.join(os.getcwd(), "data")
output_dir = os.path.join(os.getcwd(), "output")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Get a list of all XML files in the input directory
xml_files = [f for f in os.listdir(input_dir) if f.endswith('.xml')]

# Helper function to convert timestamp to the specified readable format
def convert_readable_date(timestamp):
    return datetime.utcfromtimestamp(int(timestamp) / 1000).strftime('%b %d, %Y %I:%M:%S %p')

# Process each XML file
for xml_file in xml_files:
    input_file = os.path.join(input_dir, xml_file)

    # Parse the XML file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Initialize the data structure
    data = {}

    # Process each SMS message in the XML
    for message in root.findall('sms'):
        address = message.get("address")
        contact_name = message.get("contact_name", "")
        if address not in data:
            data[address] = {
                "name": contact_name,
                "chat_messages": []
            }
        chat_message = {
            "text": message.get("body"),
            "sender": contact_name if message.get("type") == "1" else "user",
            "timestamp": int(message.get("date")),
            "readable_date": convert_readable_date(message.get("date")),
            "attachments": [],
            "files": []
        }
        data[address]["chat_messages"].append(chat_message)

    # Process each MMS message in the XML
    for message in root.findall('mms'):
        address = message.get("address")
        contact_name = message.get("contact_name", "")
        if address not in data:
            data[address] = {
                "name": contact_name,
                "chat_messages": []
            }
        parts_text = []
        for part in message.find('parts').findall('part'):
            if part.get("ct") == "text/plain":
                parts_text.append(part.get("text"))

        chat_message = {
            "text": "\n".join(parts_text),
            "sender": contact_name if message.get("msg_box") == "1" else "user",
            "timestamp": int(message.get("date")),
            "readable_date": convert_readable_date(message.get("date")),
            "attachments": [],
            "files": []
        }
        data[address]["chat_messages"].append(chat_message)

    # Process each chat in the data
    for address, chat in data.items():
        chat_name = chat["name"].replace(" ", "_").replace("\"", "")
        chat_messages = chat["chat_messages"]

        # Sort messages by timestamp
        chat_messages.sort(key=lambda x: x["timestamp"])

        # Skip empty conversations
        if not chat_messages:
            continue

        # Define the output file path
        output_file = os.path.join(output_dir, f"{chat_name}.txt")

        # Write the markdown representation to the output file
        with open(output_file, "w", encoding="utf-8") as txt_file:
            txt_file.write(f"# {chat['name']}\n\n")
            for message in chat_messages:
                sender = message.get("sender", "unknown")
                text = message.get("text", "")
                readable_date = message.get("readable_date", "")
                txt_file.write(f"**{sender}** ({readable_date}): {text}\n\n")

print("Text files have been generated in the output directory.")