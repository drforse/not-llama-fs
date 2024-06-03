# NotLlamaFS

NotLlamaFS is an AI self-organizing file manager. It automatically renames and organizes your files based on their contents and well-known conventions (e.g., time) using Chat AI. Currently the support is made for text files and image files (if used model supports it).

It's made out of fun and in my opinion is useless.

## Inspiration

I just wanted [llama_fs](https://github.com/iyaja/llama-fs) to actually work. So I rewrote it from scratch.

> Open your `~/Downloads` directory. Or your Desktop. It's probably a mess...

## Proclamation
It's not doing anything yet, just demonstrating the concept.
NotLlamaFS is not a fork, but a rewrite from scratch!

## Installation

### Prerequisites

Before installing, ensure you have the following requirements:  
- Python 3.10 or higher  
- pip (Python package installer)  

If you want to use NotLlamaFS with local llama models, you need to install [Ollama](https://ollama.com/) and pull the llama3 and llava models like that:  
```bash
ollama pull llama3 
ollama pull llava
```

If you want to use Groq, ChatGPT or Claude, you will need to get the API keys.  

### Installing

To install the project, follow these steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/drforse/not-llama-fs.git
   ```

2. Navigate to the project directory:
    ```bash
    cd not-llama-fs
    ```

3. Install requirements
   ```bash
   pip install -r requirements.txt
   ```
   or with poetry
    ```bash
    poetry install 
    ```
## Usage

To see the demo of the resulting file structure, run the command:

For local llama3+llava (requires their installation! check [prerequisites section](#prerequisites) for more details)    
   ```bash
   python -m app demo "path/to/directory/with/files/to/organize" --producer ollama 
   ```

For groq  
```bash
python -m app demo "path/to/directory/with/files/to/organize" --producer groq --apikey "your-groq-api-key" 
```  

For OpenAI (ChatGPT)  
```bash 
python -m app demo "path/to/directory/with/files/to/organize" --producer openai --apikey "your-openai-api-key"
```  

For Claude
```bash
python -m app demo "path/to/directory/with/files/to/organize" --producer claude --apikey "your-claude-api-key" 
```  

More settings for your run:  
`--text-model`: model for text files    
Defaults are:  
- llama3 for local ollama models  
- llama3-70b-8192 for groq  
- gpt-4o for openai  
- claude-3-haiku-20240307 for claude  

`--image-model`: model for image files  
Defaults are:  
- llava for local ollama models  
- claude-3-haiku-20240307 for claude  
- text model is used for groq (setting ignored, code here is not completely alright)  
- text model is used for openai (setting ignored, code here is not completely alright)  


## Differences from LlamaFS
- NotLlamaFS is much better written, and has a better structure.
- NotLlamaFS works, and documentations is intended to fix not-understandable parts of the launch.
- NotLlamaFS is developed by a Windows's user, so it's more likely to work on Windows.
- NotLlamaFS not implementing an API, but instead it's a cli tool.
- NotLlamaFS supports not only local llama (moondream) and groq, but also ChatGPT and Claude.
- NotLlamaFS doesn't mix producers (moondream, groq, chatgpt, claude), but uses what it's told to use.
- NotLlamaFS won't have a frontend, but it's planned to have a GUI.
- NotLlamaFS doesn't try to say "its extremely fast because of using obvious cache for not reprocessing the same file" :D


## What's next for NotLlamaFS

- Better configuration
- Updating file structure in system
- Better support for different models
- Better support for different file types
- Better documentation
- Improved prompts
- User-friendly interface (GUI)
- Custom rules for organizing files

## Credits
https://github.com/iyaja/llama-fs - for the idea, inspiration and making me angry (for nothing working!) enough to write this.
