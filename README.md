# Generative Podcast CLI

A powerful command-line tool for generating AI-powered podcasts using Claude AI for content generation and ElevenLabs for text-to-speech synthesis.

## Features

- AI-powered script generation using Claude 3.5 Sonnet
- High-quality text-to-speech using ElevenLabs API
- Custom voice selection from ElevenLabs' voice library
- Cost-effective model selection with multiple TTS options
- Markdown-based script storage
- Flexible workflow from prompt to final audio

## Prerequisites

- Python 3.8+
- An ElevenLabs API key
- An Anthropic API key (for Claude)
- Make (for running commands)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jonathanhudak/generative-podcast.git
cd gen-podcast
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```env
XI_API_KEY=your_elevenlabs_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## CLI Usage

The CLI tool provides several options for generating podcasts. Run the tool using:

```bash
make cli
```

### Available Commands

When you run the CLI, you'll be presented with four options:

1. **Create a new script prompt** (Option 1)
   - Generates an AI-powered script prompt based on your topic
   - Input: Topic of your choice
   - Output: Saves the prompt in `storage/prompts/`

2. **Generate a new script using an existing prompt** (Option 2)
   - Uses a previously generated prompt to create a full script
   - Lets you select from available prompts
   - Output: Saves the script in `storage/scripts/`

3. **Generate the podcast from an existing script** (Option 3)
   - Converts a script into audio using ElevenLabs
   - Features:
     - Select from available voices
     - Choose TTS model based on cost/quality preferences
     - Output: Saves audio in `storage/audio/output/`

4. **List available voices** (Option 4)
   - Displays all available ElevenLabs voices
   - Shows detailed information including:
     - Voice name
     - Voice ID
     - Description

### Text-to-Speech Models

The tool supports multiple ElevenLabs models with different pricing:

1. **Eleven English v1**
   - Legacy model, English only
   - Cost: $0.00003 per character
   - Best for: Cost-effective English content

2. **Eleven Multilingual v1**
   - Legacy multilingual model
   - Cost: $0.00003 per character
   - Best for: Multi-language content on a budget

3. **Eleven English v2**
   - Improved English model
   - Cost: $0.00004 per character
   - Best for: Higher quality English content

4. **Eleven Multilingual v2**
   - Latest multilingual model
   - Cost: $0.00004 per character
   - Best for: Premium multi-language content

### Using Custom Voices

You can use any voice from your ElevenLabs account. To find your available voices:

1. Run the CLI tool with option 4 to list all voices:
```bash
make cli
# Select option 4
```

2. Note down the Voice ID of the voice you want to use. Voice IDs look like this: `pNInz6obpgDQGcFmaJgB`

3. When generating a podcast (option 3):
   - You'll see a list of available voices with their IDs
   - Each voice will be shown as: `Name (ID: voice_id_here)`
   - Select the number corresponding to your desired voice

Tips for using custom voices:
- You can add new voices to your ElevenLabs account through their website
- Voice IDs are unique to your account
- Professional voices may have different pricing
- Test your voice with a small script first to ensure quality

### Example Workflow

1. Generate a script prompt:
```bash
make cli
# Select option 1
# Enter topic: "The History of Coffee"
```

2. Generate a full script:
```bash
make cli
# Select option 2
# Choose your previously generated prompt
```

3. Create the podcast:
```bash
make cli
# Select option 3
# Choose a voice from the list
# Select a TTS model based on your needs
```

### Output Directory Structure

```
storage/
├── prompts/         # Stores generated prompts
├── scripts/         # Stores generated scripts
├── audio/
│   ├── output/     # Stores generated audio files
│   └── uploads/    # Stores uploaded audio files
└── cache/          # Stores API response caches
```
