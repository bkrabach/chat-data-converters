import json
import zipfile
from pathlib import Path
import re
from datetime import datetime

def extract_datetime_from_filename(filename):
    """Extract datetime from filename pattern: data-YYYY-MM-DD-HH-MM-SS.zip"""
    pattern = r'data-(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})\.zip'
    match = re.match(pattern, filename)
    if match:
        return match.group(1)
    return None

def process_zip_file(zip_path):
    """Extract and process JSON files from a zip file."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Read users.json
            with zip_ref.open('users.json') as f:
                users_data = json.load(f)
            
            # Read conversations.json
            with zip_ref.open('conversations.json') as f:
                conversations_data = json.load(f)
            
        return users_data, conversations_data
    except KeyError as e:
        raise Exception(f"Missing required file in zip: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON format: {e}")
    except Exception as e:
        raise Exception(f"Error processing zip file: {e}")

def create_user_conversation_files(users_data, conversations_data, timestamp, output_dir):
    """Create individual JSON files for each user containing their conversations."""
    
    # Create a mapping of user UUIDs to names
    uuid_to_name = {user['uuid']: user['full_name'] for user in users_data}
    
    # Create a dictionary to store conversations by user
    user_conversations = {}
    
    # Process each conversation
    for conversation in conversations_data:
        # Get the user UUID from the account field
        user_uuid = conversation['account']['uuid']
        
        # Skip if we don't have user info
        if user_uuid not in uuid_to_name:
            print(f"Warning: No user found for UUID {user_uuid}")
            continue
            
        # Get the user's name
        user_name = uuid_to_name[user_uuid]
        
        # Initialize user's conversation list if not exists
        if user_name not in user_conversations:
            user_conversations[user_name] = []
            
        # Add this conversation to the user's list
        user_conversations[user_name].append(conversation)
    
    # Write each user's conversations to a separate file
    for user_name, conversations in user_conversations.items():
        # Create sanitized user directory name
        user_dir = output_dir / user_name.replace(' ', '_')
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename with timestamp
        filename = user_dir / f"conversations_{timestamp}.json"
        
        # Write the conversations to a JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'user_name': user_name,
                'timestamp': timestamp,
                'conversations': conversations
            }, f, indent=2, ensure_ascii=False)
            
        print(f"Created file: {filename}")

def process_input_directory(input_dir, output_dir):
    """Process all zip files in the input directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Ensure directories exist
    input_path.mkdir(exist_ok=True)
    output_path.mkdir(exist_ok=True)
    
    # Find all zip files in input directory
    zip_files = list(input_path.glob('data-*.zip'))
    
    if not zip_files:
        print("No zip files found in input directory")
        return
    
    for zip_file in zip_files:
        try:
            # Extract timestamp from filename
            timestamp = extract_datetime_from_filename(zip_file.name)
            if not timestamp:
                print(f"Warning: Invalid filename format: {zip_file.name}")
                continue
            
            print(f"\nProcessing: {zip_file.name}")
            
            # Process the zip file
            users_data, conversations_data = process_zip_file(zip_file)
            
            # Create user conversation files
            create_user_conversation_files(users_data, conversations_data, timestamp, output_path)
            
            print(f"Successfully processed {zip_file.name}")
            
        except Exception as e:
            print(f"Error processing {zip_file.name}: {e}")

def main():
    try:
        # Configure directories
        input_dir = './data'
        output_dir = './output'
        
        # Process all files in input directory
        process_input_directory(input_dir, output_dir)
        
        print("\nProcessing completed!")
        
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")

if __name__ == '__main__':
    main()