import requests
import json
import os
import glob
import sys
import asyncio
import random 
from datetime import datetime
from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from .models import PromptRequest, ScriptRequest, VoiceResponse, PromptResponse, ScriptResponse, PodcastResponse, PodcastRequest
from urllib.parse import unquote  # Import unquote for URL decoding
import re

from pydantic import BaseModel
templates = Jinja2Templates(directory="src/templates")  # Set the template directory

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

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

anthropic_client = AsyncAnthropic()

def safe_filename(title: str) -> str:
    # Remove colons and question marks
    title = title.replace(':', '').replace('?', '')
    
    # Replace spaces with underscores
    title = title.replace(' ', '_')
    
    # Remove any characters that are not alphanumeric, underscores, or hyphens
    title = re.sub(r'[^a-zA-Z0-9_-]', '', title)
    
    # Optionally, you can also normalize the title to handle special characters
    # title = unidecode(title)  # Uncomment if you want to normalize accented characters

    return title
    
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
def text_to_speech(voice_id, text, filename=None):
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
    
    print(f"Sending request to TTS API at {tts_url} with voice_id: {voice_id}")
    
    response = requests.post(tts_url, headers=headers, json=data, stream=True)
    
    if response.ok:
        print("Received successful response from TTS API.")
        
        # Generate a timestamped filename with prompt filename if provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{filename}_{timestamp}.mp3"
        output_path = f"storage/audio/output/{output_filename}"
        
        print(f"Saving audio stream to {output_path}...")
        
        with open(output_path, "wb") as f:
            total_length = response.headers.get('content-length')
            if total_length is None:  # No content length header
                print("No content length header found, writing content directly.")
                f.write(response.content)
            else:
                total_length = int(total_length)
                print(f"Total content length: {total_length} bytes.")
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
                    done = int(50 * f.tell() / total_length)
                    sys.stdout.write(f"\r[{'█' * done}{' ' * (50 - done)}] {done * 2}%")
                    sys.stdout.flush()
        print("\nAudio stream saved successfully.")
        return output_filename
    else:
        print("Failed to convert text to speech. Response:", response.text)
        print(f"Status Code: {response.status_code}, Headers: {response.headers}")

# Function to generate a prompt using Anthropic's Sonnet 3.5
async def generate_prompt(topic):
    async with anthropic_client.messages.stream(
        model=MODEL_NAME,
        max_tokens=1024,
        system="""

You are an AI prompt engineer that generates prompts that will result in a professional script for solo podcast episodes.
The script should be written without any directives in a way that can be read aloud as-is.
Please use the <topic> tag to determine the podcast episode topic and add unique and specific additions to the prompt topic to the resulting prompt.
Return only the prompt and nothing else.

""",
        messages=[
            {"role": "user", "content": f"<topic>{topic}</topic>"}
        ]
    ) as stream:
        full_response = ""
        async for text in stream.text_stream:
            full_response += text
            yield text
    
    # Save the generated prompt to a file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    formatted_topic = safe_filename(topic.replace(" ", "_").lower())
    prompt_filename = f"{formatted_topic}_{timestamp}.md"
    with open(f"storage/prompts/{prompt_filename}", 'w') as file:
        file.write(full_response)
    
    print(f"Generated Prompt: {full_response}")
    print(f"Prompt saved as {prompt_filename}")

async def generate_script(prompt, topic):
    if not prompt:
        raise ValueError("Prompt cannot be empty.")
    if not topic:
        raise ValueError("Topic cannot be empty.")
    
    print("Starting script generation...")
    full_script = ""  # Initialize a variable to hold the full script
    async with anthropic_client.messages.stream(
        model=MODEL_NAME,
        max_tokens=2048,
        system="""
You are a professional podcast script writer.
You will be given a prompt and you will write a script for a podcast episode based on the prompt.
The script should be written without any directives in a way that can be read aloud as-is.
Keep the script fairly short and sweet. Reading time should be no longer than 4-5 minutes.
""",
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        async for text in stream.text_stream:
            print("Received chunk:", text)  # Log each chunk received
            full_script += text  # Accumulate the script text
            yield text  # Stream the text as it is received

    print("Script generation completed.")
    
    # Save the resulting script to a file after streaming is complete
    await save_script_to_file(full_script, topic)

async def create_script_prompt(topic):
    script_prompt = await generate_prompt(topic)
    
    # Generate a timestamped filename using the topic
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    formatted_topic = safe_filename(topic.replace(" ", "_")).lower()  # Format topic for filename
    prompt_filename = f"{formatted_topic}_{timestamp}.md"

    # Save the generated script prompt to a file
    await save_script_to_file(script_prompt, topic, prompt_filename)

    print(f"Script prompt generated and saved as {prompt_filename}.")
    return prompt_filename

async def save_script_to_file(script_content, topic, filename=None):
    if filename is None:
        # Generate a default filename if not provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        formatted_topic = safe_filename(topic.replace(" ", "_").lower())  # Format topic for filename
        filename = f"{formatted_topic}_{timestamp}.md"
    
    # Save the script content to the specified file
    with open(f"storage/scripts/{filename}", 'w') as file:
        file.write(script_content)
    print(f"Script saved as {filename}.")

def get_prompt_options():
    prompt_files = glob.glob('storage/prompts/*.md')
    prompt_options = []

    # Collect prompt options
    for file_path in prompt_files:
        filename = os.path.basename(file_path).replace('.md', '').replace('_', ' ').title()
        prompt_options.append((filename, file_path))  # Store both filename and path

    return prompt_options
    
# Function to generate a new script using an existing prompt
async def generate_script_from_prompt():
    # Call the new function to get prompt options
    prompt_options = get_prompt_options()
    
    # Display prompt options
    print("Available Prompts:")
    for index, (filename, _) in enumerate(prompt_options):
        print(f"{index + 1}: {filename}")
    
    choice = int(input("Select a prompt by number (or enter 0 to skip): ")) - 1
    
    if choice >= 0 and choice < len(prompt_options):
        with open(prompt_options[choice][1], 'r') as file:
            user_input = file.read()
        script_filename = os.path.basename(prompt_options[choice][1])  # Save the prompt filename
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
    else:
        print("No valid prompt selected. Exiting.")

def get_script_options():
    script_files = glob.glob('storage/scripts/*.md')
    script_options = []

    # Collect script options
    for file_path in script_files:
        filename = os.path.basename(file_path).replace('.md', '').replace('_', ' ').title()
        script_options.append((filename, file_path))  # Store both filename and path

    return script_options

# FastAPI endpoints
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    voices = fetch_voice_ids()
    prompt_files = glob.glob('storage/prompts/*.md')
    prompts = [os.path.basename(file).replace('.md', '') for file in prompt_files]
    script_files = glob.glob('storage/scripts/*.md')
    scripts = [os.path.basename(file).replace('.md', '') for file in script_files]
    audio_files = glob.glob('storage/audio/output/*.mp3')
    podcasts = [os.path.basename(file) for file in audio_files]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "voices": voices,
        "prompts": prompts,
        "scripts": scripts,
        "podcasts": podcasts
    })

@app.post("/create_prompt")
async def api_create_prompt(request: PromptRequest):
    return StreamingResponse(generate_prompt(request.topic), media_type="text/event-stream")

@app.post("/generate_script")
async def api_generate_script(request: ScriptRequest):
    return StreamingResponse(generate_script(request.prompt, request.topic), media_type="text/event-stream")

@app.get("/voices", response_model=VoiceResponse)
def api_fetch_voices():
    voices = fetch_voice_ids()
    return {"voices": voices}

@app.get("/prompts", response_model=PromptResponse)
def api_get_prompts():
    prompt_files = glob.glob('storage/prompts/*.md')
    prompts = [{"name": os.path.basename(file).replace('.md', ''), "id": os.path.basename(file).replace('.md', '')} for file in prompt_files]
    return {"prompts": prompts}

@app.get("/scripts", response_model=ScriptResponse)
def api_get_scripts():
    script_files = glob.glob('storage/scripts/*.md')
    scripts = [{"name": os.path.basename(file).replace('.md', ''), "id": os.path.basename(file).replace('.md', '')} for file in script_files]
    return {"scripts": scripts}

@app.get("/podcasts", response_model=PodcastResponse)
def api_get_audio_files():
    audio_files = glob.glob('storage/audio/output/*.mp3')
    podcasts = [{"name": os.path.basename(file), "id": os.path.basename(file)} for file in audio_files]
    return {"podcasts": podcasts}
    
# Function to generate the podcast from an existing script
async def generate_podcast_from_script():
    # Call the new function to get script options
    script_options = get_script_options()
    
    # Display script options
    print("Available Scripts:")
    for index, (filename, _) in enumerate(script_options):
        print(f"{index + 1}: {filename}")
    
    choice = int(input("Select a script by number (or enter 0 to skip): ")) - 1
    
    if choice >= 0 and choice < len(script_options):
        script_filename = script_options[choice][1]  # Get the file path
        with open(script_filename, 'r') as file:
            user_input = file.read()
        print(f"Using script from {script_options[choice][0]}.")
    else:
        print("No valid script selected. Exiting.")
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
    script_filename = os.path.basename(script_filename).replace('.md', '')  # Get the last segment without extension
    text_to_speech(selected_voice_id, user_input, script_filename)

@app.get("/prompts/{prompt_id}", response_class=PlainTextResponse)
async def get_prompt_content(prompt_id: str):
    prompt_path = f"storage/prompts/{prompt_id}.md"
    try:
        with open(prompt_path, "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Prompt not found")

@app.get("/scripts/{script_id}", response_class=PlainTextResponse)
async def get_script_content(script_id: str):
    script_path = f"storage/scripts/{script_id}.md"
    try:
        with open(script_path, "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Script not found")

# Function to cache random topics, appending new topics to the existing list
def cache_random_topics(new_topics):
    cache_file = 'storage/cache/random_topics.json'
    
    # Load existing topics if the cache file exists
    if os.path.exists(cache_file):
        cached_data = read_from_file(cache_file)
        existing_topics = cached_data["topics"]
    else:
        existing_topics = []

    # Append new topics to the existing list and remove duplicates
    combined_topics = list(set(existing_topics + new_topics))
    write_to_file(cache_file, {"topics": combined_topics})  # Cache the combined topics

# Update the api_get_random_topics function
@app.get("/random_topics")
async def api_get_random_topics(get_fresh_topics: bool = False):  # Add a query parameter
    cache_file = 'storage/cache/random_topics.json'
    
    # Load cached topics if available
    if os.path.exists(cache_file):
        cached_data = read_from_file(cache_file)
        cached_topics = cached_data["topics"]
    else:
        cached_topics = []

    if get_fresh_topics:  # Check if the query parameter is set to True
        async with anthropic_client.messages.stream(
            model=MODEL_NAME,
            max_tokens=2048,
            messages=[
                {"role": "user", "content": """
Generate a list of 15 concise and interesting topics for short 5 minute podcasts. The topics should be wide ranging diverse and fascinating.
Return only the list as a JSON array and nothing else.
"""}
            ]
        ) as stream:
            async for text in stream.text_stream:
                print(text, end="", flush=True)
            print()
        
        message = await stream.get_final_message()
        new_topics = json.loads(message.content[0].text)  # Parse JSON string into a list
        cache_random_topics(new_topics)  # Cache the new topics

        # Combine cached and new topics
        combined_topics = list(set(cached_topics + new_topics))
    else:
        combined_topics = cached_topics  # Use cached topics only

    # Select up to 15 random topics from the combined list
    random_topics = random.sample(combined_topics, min(15, len(combined_topics)))

    return {"topics": random_topics}

@app.post("/create_podcast")
async def api_create_podcast(request: PodcastRequest):
    
    # Extract the title, script, and voice_id from the request
    title = request.title  # New title parameter
    script = request.script
    voice_id = request.voice_id

    if not title:
        raise ValueError("title cannot be empty.")
    if not script:
        raise ValueError("script cannot be empty.")
    
    # Fetch voice IDs
    voices = fetch_voice_ids()
    if not voices:
        raise HTTPException(status_code=400, detail="No voices available for TTS.")

    # Use the provided voice_id or default to the first voice
    if voice_id is None:
        voices = fetch_voice_ids()

        if not voices:
            raise HTTPException(status_code=400, detail="No voices available for TTS.")

        selected_voice_id = voices[0]['voice_id']
    else:
        # Check if the provided voice_id is valid
        if not any(voice['voice_id'] == voice_id for voice in voices):
            raise HTTPException(status_code=400, detail="Invalid voice ID provided.")
        selected_voice_id = voice_id
    
    # Call the text_to_speech function and get the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    podcast_filename = safe_filename(f"{title.replace(' ', '_')}")
    podcast_filename = text_to_speech(selected_voice_id, script, podcast_filename)

    return {"message": "Podcast created successfully.", "podcast_filename": podcast_filename}

@app.get("/audio/{podcast_name}", response_class=StreamingResponse)
async def get_audio_file(podcast_name: str):
    # Decode the URL-encoded podcast name
    decoded_podcast_name = unquote(podcast_name)
    audio_path = f"storage/audio/output/{decoded_podcast_name}"
    
    print(f"Looking for audio file at: {audio_path}")  # Debugging line
    
    if os.path.exists(audio_path):
        return StreamingResponse(open(audio_path, "rb"), media_type="audio/mpeg")
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

async def main():
    print("Select an option:")
    print("1: Create a new script prompt")
    print("2: Generate a new script using an existing prompt")
    print("3: Generate the podcast from an existing script")
    action_choice = int(input("Enter your choice (1, 2, or 3): "))
    
    if action_choice == 1:
        topic = input("Enter a topic for the script prompt: ")
        await create_script_prompt(topic)
    elif action_choice == 2:
        await generate_script_from_prompt()
    elif action_choice == 3:
        await generate_podcast_from_script()
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "web"  # Default to web mode
    if mode == "cli":
        asyncio.run(main())