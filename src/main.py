import requests
import json
import os
import glob
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

# Load environment variables from .env file
load_dotenv()

# Access the API key
XI_API_KEY = os.getenv("XI_API_KEY")

MODEL_NAME = "claude-3-5-sonnet-20240620"

# Create storage directories if they don't exist
os.makedirs('storage/prompts', exist_ok=True)
os.makedirs('storage/cache', exist_ok=True)
os.makedirs('storage/audio/output', exist_ok=True)
os.makedirs('storage/scripts', exist_ok=True)

anthropic_client = AsyncAnthropic()

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
        voices_data = read_from_file(cache_file)
        print(f"Type of voices_data: {type(voices_data)}")
        print(f"voices {voices_data}")
        if voices_data["voices"] != None:
            return voices_data["voices"]
    
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
        output_path = f"storage/audio/output/{prompt_suffix}_{timestamp}.mp3"
        
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


# Function to generate a prompt using Anthropic's Sonnet 3.5
async def generate_prompt(topic):
    async with anthropic_client.messages.stream(
        model=MODEL_NAME,
        max_tokens=1024,
        system="You are an AI prompt engineer that generates prompts that will result in a professional script for solo podcast episodes. The script should be written without any directives in a way that can be read aloud as-is. Please use the <topic> tag to determine the podcast episode topic and add unique and specific additions to the prompt topic to the resulting prompt.",
        messages=[
            {"role": "user", "content": f"<topic>{topic}</topic>"}
        ]
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)
        print()
    
    message = await stream.get_final_message()
    print(message.to_json())
    prompt_result = message.content[0].text
    print(f"Generated Prompt: {prompt_result}")
    return prompt_result

async def generate_script(prompt):
    async with anthropic_client.messages.stream(
        model=MODEL_NAME,
        max_tokens=2048,
        system="You are a professional podcast script writer. You will be given a prompt and you will write a script for a podcast episode based on the prompt. The script should be written without any directives in a way that can be read aloud as-is.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)
        print()
    
    message = await stream.get_final_message()
    print(message.to_json())
    prompt_result = message.content[0].text
    print(f"Generated Script: {prompt_result}")
    return prompt_result

# Main function
async def main():
    # Prompt user for action
    print("What would you like to do?")
    print("1: Create a new script prompt")
    print("2: Generate a new script using an existing prompt")
    print("3: Generate the podcast from an existing script")
    action_choice = int(input("Enter your choice (1, 2, or 3): "))
    
    if action_choice == 1:
        # Create a new script prompt
        topic = input("Enter the topic for the podcast episode: ")
        script_prompt = await generate_prompt(topic)
        
        # Generate a timestamped filename using the topic
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        formatted_topic = topic.replace(" ", "_").lower()  # Format topic for filename
        prompt_filename = f"{formatted_topic}_{timestamp}.md"

        # Save the generated script prompt to a file
        with open(f"storage/prompts/{prompt_filename}", 'w') as file:
            file.write(script_prompt)

        print(f"Script prompt generated and saved as {prompt_filename}.")
        return

    elif action_choice == 2:
        # Generate a new script using an existing prompt
        prompt_files = glob.glob('storage/prompts/*.md')
        
        # Display prompt options
        print("Available Prompts:")
        for index, file_path in enumerate(prompt_files):
            filename = os.path.basename(file_path).replace('.md', '').replace('_', ' ').title()
            print(f"{index + 1}: {filename}")
        
        choice = int(input("Select a prompt by number (or enter 0 to skip): ")) - 1
        
        if choice >= 0 and choice < len(prompt_files):
            with open(prompt_files[choice], 'r') as file:
                user_input = file.read()
            script_filename = os.path.basename(prompt_files[choice])  # Save the prompt filename
            print(f"Using prompt from {script_filename}.")
            
            # Generate the script using the selected prompt
            script = await generate_script(user_input)
            
            # Generate a good filename based on the prompt (without timestamp)
            formatted_script_name = script_filename.replace('.md', '').replace('_', ' ').title()
            script_filename = f"{formatted_script_name}_script.md"

            # Save the generated script to the storage/scripts directory
            with open(f"storage/scripts/{script_filename}", 'w') as file:
                file.write(script)

            print(f"Script generated and saved as {script_filename}.")
            return
        else:
            print("No valid prompt selected. Exiting.")
            return
        

    elif action_choice == 3:
        # Generate the podcast from an existing script
        script_files = glob.glob('storage/scripts/*.md')
        
        # Display script options
        print("Available Scripts:")
        for index, file_path in enumerate(script_files):
            filename = os.path.basename(file_path).replace('.md', '').replace('_', ' ').title()
            print(f"{index + 1}: {filename}")
        
        choice = int(input("Select a script by number (or enter 0 to skip): ")) - 1
        
        if choice >= 0 and choice < len(script_files):
            with open(script_files[choice], 'r') as file:
                user_input = file.read()
            script_filename = os.path.basename(script_files[choice])  # Save the script filename
            print(f"Using script from {script_filename}.")

        else:
            print("No valid script selected. Exiting.")
            return

    else:
        print("Invalid choice. Exiting.")
        return

    # Fetch voice IDs
    voices = fetch_voice_ids()
    
    if not voices:
        return
    
    # Display voice options
    print("Available Voices:")
    for index, voice in enumerate(voices):
        print(f"{index + 1}: {voice['name']} (ID: {voice['voice_id']})")
        for label_key, label_value in voice['labels'].items():  # Iterate through labels
            print(f"  {label_key}: {label_value}")  # Print each label key and value

    # Prompt user to select a voice
    choice = int(input("Select a voice by number: ")) - 1
    selected_voice_id = voices[choice]['voice_id']
    
    # Perform text-to-speech conversion
    text_to_speech(selected_voice_id, user_input, script_filename)

if __name__ == "__main__":
    asyncio.run(main())