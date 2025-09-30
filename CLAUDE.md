# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Restaurant AI application built with Python, Flask, and PyTorch/Transformers. The project uses the Qwen2-VL-7B-Instruct model for AI processing of restaurant-related tasks including receipt processing and text analysis.

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **`main.py`** - Application entry point that initializes AIProcessor and WebServer
- **`src/ai_processor.py`** - Core AI processing engine using transformers
- **`src/web_server.py`** - Flask web service for handling HTTP requests
- **`src/prompt_manager.py`** - Manages AI prompts with modular prompt system
- **`src/database.py`** - Database operations and data persistence
- **`src/prompts/`** - Modular prompt system split by domain (receipt_prompts.py, text_prompts.py)
- **`config/prompt_config.yaml`** - Configuration for prompts, models, and AI settings
- **`frontend/`** - Web interface with js/, static/, and templates/ directories
- **`models/`** - Contains the qwen2-vl-7b-instruct model files
- **`test/`** - Test modules and test data

## Common Development Commands

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Run main application
python main.py

# For development with auto-reload (if Flask development mode is configured)
flask run --debug
```

### Testing
```bash
# Run all tests
python -m pytest test/

# Run specific test file
python -m pytest test/test_prompts.py

# Run test with verbose output
python -m pytest -v
```

### AI Model Management
- The default model is `qwen2-vl-7b-instruct` located in `models/`
- Model configuration is managed through `config/prompt_config.yaml`
- Temperature is set to 0.7 with max_tokens of 2048

## Key Dependencies
- **Flask** ≥2.3.0 - Web framework
- **torch** ≥2.0.0 - PyTorch for deep learning
- **transformers** ≥4.35.0 - Hugging Face transformers library
- **Pillow** ≥10.0.0 - Image processing
- **PyYAML** ≥6.0 - YAML configuration parsing
- **requests** ≥2.31.0 - HTTP client library

## Development Notes
- The project is in early development stage with mostly stub classes
- Prompt management is modular and domain-specific (receipt vs text processing)
- Configuration is externalized in YAML format
- The architecture supports both image (receipt) and text processing workflows