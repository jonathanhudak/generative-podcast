import requests
import json
import os
import glob
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
XI_API_KEY = os.getenv("XI_API_KEY")

# Create storage directories if they don't exist
os.makedirs('storage/prompts', exist_ok=True)
os.makedirs('storage/cache', exist_ok=True)
os.makedirs('storage/audio/output', exist_ok=True)

# Function to write data to a file
def write_to_file(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data written to {filename}")

# Function to read data from a file
def read_from_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Function to fetch voice IDs from Eleven Labs API
def fetch_voice_ids():
    cache_file = 'storage/cache/get_voices.json'
    
    # Check if the cache file exists
    if os.path.exists(cache_file):
        print("Reading voice IDs from cache.")
        voices = read_from_file(cache_file)  # Read from cache if it exists
        print("Cached Voices Data:", voices)  # Inspect the cached data
        return voices
    
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        write_to_file(cache_file, data)  # Cache voice IDs
        
        # Check if 'voices' is a list
        if isinstance(data.get('voices'), list):
            return data['voices']
        else:
            print("Unexpected response structure:", data)
            return []
    else:
        print("Failed to fetch voice IDs. Status code:", response.status_code)
        print("Response:", response.text)
        return []

# Function to perform text-to-speech conversion
def text_to_speech(voice_id, text, prompt_filename=None):
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    response = requests.post(tts_url, headers=headers, json=data, stream=True)
    
    if response.ok:
        # Generate a timestamped filename with prompt filename if provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_suffix = f"_{prompt_filename.replace('.md', '')}" if prompt_filename else ""
        output_path = f"storage/audio/output/output{prompt_suffix}_{timestamp}.mp3"
        
        with open(output_path, "wb") as f:
            total_length = response.headers.get('content-length')
            if total_length is None:  # No content length header
                f.write(response.content)
            else:
                total_length = int(total_length)
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
                    done = int(50 * f.tell() / total_length)
                    sys.stdout.write(f"\r[{'█' * done}{' ' * (50 - done)}] {done * 2}%")
                    sys.stdout.flush()
        print("\nAudio stream saved successfully.")
    else:
        print("Failed to convert text to speech. Response:", response.text)

# Main function
def main():
    # List all .md files in the storage/prompts directory
    prompt_files = glob.glob('storage/prompts/*.md')
    
    # Display prompt options
    print("Available Prompts:")
    for index, file_path in enumerate(prompt_files):
        # Extract the filename without the directory and extension
        filename = os.path.basename(file_path).replace('.md', '').replace('_', ' ').title()
        print(f"{index + 1}: {filename}")
    
    # Prompt user to select a prompt
    choice = int(input("Select a prompt by number (or enter 0 to skip): ")) - 1
    
    if choice >= 0 and choice < len(prompt_files):
        with open(prompt_files[choice], 'r') as file:
            user_input = file.read()
        prompt_filename = os.path.basename(prompt_files[choice])  # Save the prompt filename
    else:
        user_input = input("Enter the text you want to convert to speech: ")
        prompt_filename = None
    
    voices = fetch_voice_ids()
    
    if not voices:
        return
    
    # Display voice options
    print("Available Voices:")
    for index, voice in enumerate(voices):
        # Access the voice dictionary correctly
        print(f"{index + 1}: {voice['name']} (ID: {voice['voice_id']})")
    
    # Prompt user to select a voice
    choice = int(input("Select a voice by number: ")) - 1
    selected_voice_id = voices[choice]['voice_id']
    
    # Perform text-to-speech conversion
    text_to_speech(selected_voice_id, user_input, prompt_filename)

if __name__ == "__main__":
    main()