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
git clone https://github.com/yourusername/gen-podcast.git
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
