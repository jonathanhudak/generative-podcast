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
from urllib.parse import unquote
import re
from typing import List, Optional
import uuid
from unidecode import unidecode
import subprocess

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
os.makedirs('storage/audio/uploads', exist_ok=True)

# Initialize FastAPI only in web mode
app = None
if len(sys.argv) > 1 and sys.argv[1] != "cli":
    from fastapi import FastAPI, HTTPException, Request, UploadFile, File
    from fastapi.responses import HTMLResponse, StreamingResponse, PlainTextResponse, FileResponse
    from fastapi.templating import Jinja2Templates
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    
    app = FastAPI()
    templates = Jinja2Templates(directory="src/templates")
    
    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Define Pydantic models for API
    class PromptRequest(BaseModel):
        topic: str

    class ScriptRequest(BaseModel):
        prompt: str
        topic: str

    class VoiceResponse(BaseModel):
        voices: List[dict]

    class PromptResponse(BaseModel):
        prompts: List[dict]

    class ScriptResponse(BaseModel):
        scripts: List[dict]

    class PodcastResponse(BaseModel):
        podcast: dict

    class PodcastRequest(BaseModel):
        topic: str
        voice_id: str
else:
    from pydantic import BaseModel
    
    # Define minimal models needed for CLI
    class Audio(BaseModel):
        duration: int
        file: str
        startTime: int
        endTime: int

    class AudioTimeline(BaseModel):
        id: str
        audio: List[Audio]

    class Podcast(BaseModel):
        id: str
        name: str
        audioTimeline: AudioTimeline

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

def slugify(text):
    # Convert to ASCII
    text = unidecode(text)
    # Convert to lowercase
    text = text.lower()
    # Remove non-word characters (everything except numbers and letters)
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace all spaces and underscores with hyphens
    text = re.sub(r'[-\s]+', '-', text)
    # Trim hyphens from start and end
    return text.strip('-')

# Available ElevenLabs models and their pricing
ELEVENLABS_MODELS = {
    'eleven_monolingual_v1': {
        'name': 'Eleven English v1',
        'description': 'Legacy model, English only',
        'cost_per_char': 0.00003
    },
    'eleven_multilingual_v1': {
        'name': 'Eleven Multilingual v1',
        'description': 'Legacy multilingual model',
        'cost_per_char': 0.00003
    },
    'eleven_turbo_v2': {
        'name': 'Eleven English v2',
        'description': 'Improved English model',
        'cost_per_char': 0.00004
    },
    'eleven_multilingual_v2': {
        'name': 'Eleven Multilingual v2',
        'description': 'Latest multilingual model',
        'cost_per_char': 0.00004
    }
}

def text_to_speech(voice_id, text, output_name, model_id=None):
    """Convert text to speech using ElevenLabs API."""
    
    # Define available models and their costs
    MODELS = {
        1: {"id": "eleven_monolingual_v1", "name": "Eleven English v1", "description": "Legacy model, English only", "cost": 0.00003},
        2: {"id": "eleven_multilingual_v1", "name": "Eleven Multilingual v1", "description": "Legacy multilingual model", "cost": 0.00003},
        3: {"id": "eleven_turbo_v2", "name": "Eleven English v2", "description": "Improved English model", "cost": 0.00004},
        4: {"id": "eleven_multilingual_v2", "name": "Eleven Multilingual v2", "description": "Latest multilingual model", "cost": 0.00004}
    }
    
    # If no model_id provided, use a default
    if model_id is None:
        model_id = "eleven_turbo_v2"
    else:
        # Convert numeric choice to model ID
        try:
            model_choice = int(model_id)
            if model_choice in MODELS:
                model_id = MODELS[model_choice]["id"]
            else:
                print(f"Invalid model choice {model_choice}, using default model")
                model_id = "eleven_turbo_v2"
        except ValueError:
            # If model_id is already a string, use it as is
            pass
    
    # Prepare the API endpoint and headers
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": XI_API_KEY
    }
    
    # Prepare the request data
    data = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    print(f"Sending request to TTS API at {url} with voice_id: {voice_id}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            output_dir = "storage/audio/output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{output_name}_{timestamp}.mp3"
            output_path = os.path.join(output_dir, output_filename)
            
            # Save the audio file
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            # Calculate and display the cost
            char_count = len(text)
            model_info = next((m for m in MODELS.values() if m["id"] == model_id), None)
            if model_info:
                cost = char_count * model_info["cost"]
                print(f"\nGeneration Stats:")
                print(f"Characters: {char_count:,}")
                print(f"Model: {model_info['name']}")
                print(f"Estimated cost: ${cost:.4f}")
            
            print(f"\nSuccessfully saved audio to: {output_path}")
            
            # Try to get audio duration using ffprobe
            try:
                result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', output_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.stdout.strip():
                    duration = float(result.stdout)
                    minutes = int(duration // 60)
                    seconds = int(duration % 60)
                    print(f"Audio duration: {minutes}m {seconds}s")
            except Exception as e:
                print("Could not determine audio duration")
            
            return output_filename
        else:
            print(f"Failed to convert text to speech. Response: {response.text}")
            print(f"Status Code: {response.status_code}, Headers: {dict(response.headers)}")
            return None
            
    except Exception as e:
        print(f"Error during text-to-speech conversion: {str(e)}")
        return None

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
    """Get available script options."""
    script_dir = "storage/scripts"
    script_files = glob.glob(f"{script_dir}/*.md")
    scripts = []
    
    for script_file in script_files:
        # Get just the filename without extension and convert to title case
        script_name = os.path.splitext(os.path.basename(script_file))[0]
        # Convert underscores to spaces and remove timestamps
        display_name = script_name.replace('_', ' ').replace('-', ' ')
        # Remove any timestamps (e.g., 20240911 211616)
        display_name = re.sub(r'\s+\d{8}\s+\d{6}$', '', display_name)
        # Convert to title case
        display_name = display_name.title()
        scripts.append((display_name, script_name))
    
    return sorted(scripts)

# New models
class Audio(BaseModel):
    duration: int
    file: str  # We'll store the file path as a string
    startTime: int
    endTime: int

class AudioTimeline(BaseModel):
    id: str
    audio: List[Audio]

class Podcast(BaseModel):
    id: str
    name: str
    audioTimeline: AudioTimeline

# In-memory storage (replace with database in production)
podcasts = {}
audio_timelines = {}

# CRUD operations for Podcast
if app:
    @app.post("/podcasts", response_model=Podcast)
    async def create_podcast(podcast: Podcast):
        if podcast.id in podcasts:
            raise HTTPException(status_code=400, detail="Podcast with this ID already exists")
        podcasts[podcast.id] = podcast
        return podcast

    @app.get("/podcasts/{podcast_id}", response_model=Podcast)
    async def read_podcast(podcast_id: str):
        if podcast_id not in podcasts:
            raise HTTPException(status_code=404, detail="Podcast not found")
        return podcasts[podcast_id]

    @app.get("/podcasts", response_model=List[Podcast])
    async def list_podcasts():
        return list(podcasts.values())

    @app.put("/podcasts/{podcast_id}", response_model=Podcast)
    async def update_podcast(podcast_id: str, podcast: Podcast):
        if podcast_id not in podcasts:
            raise HTTPException(status_code=404, detail="Podcast not found")
        podcasts[podcast_id] = podcast
        return podcast

    @app.delete("/podcasts/{podcast_id}")
    async def delete_podcast(podcast_id: str):
        if podcast_id not in podcasts:
            raise HTTPException(status_code=404, detail="Podcast not found")
        del podcasts[podcast_id]
        return {"message": "Podcast deleted successfully"}

# CRUD operations for AudioTimeline
if app:
    @app.post("/audio-timelines", response_model=AudioTimeline)
    async def create_audio_timeline(audio_timeline: AudioTimeline):
        if audio_timeline.id in audio_timelines:
            raise HTTPException(status_code=400, detail="AudioTimeline with this ID already exists")
        audio_timelines[audio_timeline.id] = audio_timeline
        return audio_timeline

    @app.get("/audio-timelines/{timeline_id}", response_model=AudioTimeline)
    async def read_audio_timeline(timeline_id: str):
        if timeline_id not in audio_timelines:
            raise HTTPException(status_code=404, detail="AudioTimeline not found")
        return audio_timelines[timeline_id]

    @app.get("/audio-timelines", response_model=List[AudioTimeline])
    async def list_audio_timelines():
        return list(audio_timelines.values())

    @app.put("/audio-timelines/{timeline_id}", response_model=AudioTimeline)
    async def update_audio_timeline(timeline_id: str, audio_timeline: AudioTimeline):
        if timeline_id not in audio_timelines:
            raise HTTPException(status_code=404, detail="AudioTimeline not found")
        audio_timelines[timeline_id] = audio_timeline
        return audio_timeline

    @app.delete("/audio-timelines/{timeline_id}")
    async def delete_audio_timeline(timeline_id: str):
        if timeline_id not in audio_timelines:
            raise HTTPException(status_code=404, detail="AudioTimeline not found")
        del audio_timelines[timeline_id]
        return {"message": "AudioTimeline deleted successfully"}

# Audio file upload endpoint
if app:
    @app.post("/upload-audio")
    async def upload_audio(file: UploadFile = File(...)):
        file_location = f"storage/audio/uploads/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        return {"filename": file.filename, "file_path": file_location}

# FastAPI endpoints
if app:
    @app.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        voices = fetch_voice_ids()
        prompt_files = glob.glob('storage/prompts/*.md')
        prompts = [os.path.basename(file).replace('.md', '').replace('_', ' ').title() for file in prompt_files]
        script_files = glob.glob('storage/scripts/*.md')
        scripts = [os.path.basename(file).replace('.md', '').replace('_', ' ').title() for file in script_files]
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
        prompts = [{"name": os.path.basename(file).replace('.md', '').replace('_', ' ').title(), "id": os.path.basename(file).replace('.md', '')} for file in prompt_files]
        return {"prompts": prompts}

    @app.get("/scripts", response_model=ScriptResponse)
    def api_get_scripts():
        script_files = glob.glob('storage/scripts/*.md')
        scripts = [{"name": os.path.basename(file).replace('.md', '').replace('_', ' ').title(), "id": os.path.basename(file).replace('.md', '')} for file in script_files]
        return {"scripts": scripts}

    @app.get("/podcasts", response_model=PodcastResponse)
    def api_get_audio_files():
        audio_files = glob.glob('storage/audio/output/*.mp3')
        podcasts = [{"name": os.path.basename(file), "id": os.path.basename(file)} for file in audio_files]
        return {"podcasts": podcasts}
    
# Function to generate the podcast from an existing script
async def generate_podcast_from_script(voice_id=None, model_id=None):
    # Call the new function to get script options
    script_options = get_script_options()
    
    # Print available scripts
    print("\nAvailable scripts:")
    for i, (display_name, _) in enumerate(script_options, 1):
        print(f"{i}: {display_name}")
    
    # Get user choice
    choice = int(input("\nSelect a script by number: ")) - 1
    if choice < 0 or choice >= len(script_options):
        print("Invalid script selection")
        return
        
    _, script_name = script_options[choice]
    script_filename = f"storage/scripts/{script_name}.md"
    
    # Read and display the script content
    with open(script_filename, 'r') as file:
        user_input = file.read()
        print("\nScript content:")
        print(user_input)
    
    # Get available voices if not provided
    if voice_id is None:
        voices = fetch_voice_ids()
        if not voices:
            print("Error: Could not fetch voice IDs")
            return
            
        # Print available voices
        print("\nAvailable voices:")
        for i, voice in enumerate(voices, 1):
            print(f"{i}: {voice.get('name', 'Unknown')}")
            print("  Labels:")
            for label_key, label_value in voice.get('labels', {}).items():
                print(f"  {label_key}: {label_value}")
    
        # Prompt user to select a voice
        choice = int(input("\nSelect a voice by number: ")) - 1
        if choice < 0 or choice >= len(voices):
            print("Invalid voice selection")
            return
        selected_voice_id = voices[choice]['voice_id']
    else:
        selected_voice_id = voice_id
    
    # Perform text-to-speech conversion
    if model_id is None:
        text_to_speech(selected_voice_id, user_input, script_name)
    else:
        text_to_speech(selected_voice_id, user_input, script_name, model_id)

if app:
    @app.get("/prompts/{prompt_id}", response_class=PlainTextResponse)
    async def get_prompt_content(prompt_id: str):
        try:
            with open(f'storage/prompts/{prompt_id}.md', 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Prompt not found")

    @app.get("/scripts/{script_id}", response_class=PlainTextResponse)
    async def get_script_content(script_id: str):
        try:
            with open(f'storage/scripts/{script_id}.md', 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Script not found")

    @app.get("/random-topics", response_model=List[str])
    async def api_get_random_topics(get_fresh_topics: bool = False):
        if get_fresh_topics:
            # Generate new topics using Claude
            messages = [
                {
                    "role": "user",
                    "content": "Generate 10 random interesting podcast topics. Return them as a simple list, one per line, without numbering or bullet points."
                }
            ]
            
            response = await anthropic_client.messages.create(
                model=MODEL_NAME,
                max_tokens=300,
                messages=messages,
                temperature=1.0
            )
            
            # Split the response into lines and clean them up
            new_topics = [line.strip() for line in response.content[0].text.split('\n') if line.strip()]
            
            # Cache the topics
            cache_random_topics(new_topics)
            
            return new_topics
        else:
            # Try to read from cache first
            cache_file = 'storage/cache/random_topics.json'
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as file:
                        cached_data = json.load(file)
                        return cached_data.get('topics', [])
                except (json.JSONDecodeError, KeyError):
                    pass
            
            # If cache doesn't exist or is invalid, generate new topics
            return await api_get_random_topics(get_fresh_topics=True)

    @app.post("/create-podcast", response_model=PodcastResponse)
    async def api_create_podcast(request: PodcastRequest):
        # Generate the prompt
        prompt = await create_script_prompt(request.topic)
        
        # Generate the script using the prompt
        script = await generate_script(prompt, request.topic)
        
        # Convert script to audio using text-to-speech
        audio_filename = text_to_speech(request.voice_id, script)
        
        # Create a new podcast entry
        podcast = {
            "id": str(uuid.uuid4()),
            "name": f"{request.topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "audio_file": audio_filename
        }
        
        return {"podcast": podcast}

    @app.get("/audio/{podcast_name}")
    async def get_audio_file(podcast_name: str):
        try:
            file_path = f"storage/audio/output/{unquote(podcast_name)}"
            return FileResponse(file_path, media_type="audio/mpeg", filename=podcast_name)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Audio file not found")

    @app.post("/text-to-speech")
    async def api_text_to_speech(request: dict):
        voice_id = request.get("voice_id")
        text = request.get("text")
        
        if not voice_id or not text:
            raise HTTPException(status_code=400, detail="Missing voice_id or text")
            
        try:
            audio_filename = text_to_speech(voice_id, text)
            return {"filename": audio_filename}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

async def main():
    print("Select an option:")
    print("1: Create a new script prompt")
    print("2: Generate a new script using an existing prompt")
    print("3: Generate the podcast from an existing script")
    print("4: List available voices")
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == "1":
        await create_script_prompt(input("Enter a topic for the script prompt: "))
    elif choice == "2":
        await generate_script_from_prompt()
    elif choice == "3":
        # Get available voices first
        voices = fetch_voice_ids()
        if not voices:
            print("Error: Could not fetch voice IDs")
            return
            
        # Print available voices
        print("\nAvailable voices:")
        for i, voice in enumerate(voices, 1):
            print(f"{i}: {voice.get('name', 'Unknown')} (ID: {voice.get('voice_id', 'Unknown')})")
        
        # Get voice selection
        voice_choice = int(input("\nSelect a voice (enter number): ")) - 1
        if voice_choice < 0 or voice_choice >= len(voices):
            print("Invalid voice selection")
            return
        selected_voice_id = voices[voice_choice]['voice_id']
        
        # Display available models
        print("\nAvailable models (sorted by cost):")
        models = {
            1: {"name": "Eleven English v1", "description": "Legacy model, English only", "cost": 0.00003},
            2: {"name": "Eleven Multilingual v1", "description": "Legacy multilingual model", "cost": 0.00003},
            3: {"name": "Eleven English v2", "description": "Improved English model", "cost": 0.00004},
            4: {"name": "Eleven Multilingual v2", "description": "Latest multilingual model", "cost": 0.00004}
        }
        
        for model_id, model_info in models.items():
            print(f"{model_id}: {model_info['name']} - {model_info['description']}")
            print(f"   Cost: ${model_info['cost']} per character")
        
        # Get model selection
        model_choice = input("\nSelect a model (enter number): ")
        try:
            model_id = int(model_choice)
            if model_id not in models:
                print("Invalid model selection, using default model")
                model_id = None
        except ValueError:
            print("Invalid input, using default model")
            model_id = None
        
        await generate_podcast_from_script(voice_id=selected_voice_id, model_id=model_id)
    elif choice == "4":
        voices = fetch_voice_ids()
        if not voices:
            print("Error: Could not fetch voice IDs")
            return
            
        print("\nAvailable voices:")
        for i, voice in enumerate(voices, 1):
            print(f"Name: {voice.get('name', 'Unknown')}")
            print(f"ID: {voice.get('voice_id', 'Unknown')}")
            print(f"Description: {voice.get('description', 'None')}")
            print("---")
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "web"  # Default to web mode
    if mode == "cli":
        asyncio.run(main())