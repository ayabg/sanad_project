# API Setup Guide - Learning Chatbot

## Overview
The chatbot now has learning capabilities and can use external APIs for more intelligent responses.

## Features Added

1. **Conversation Storage**: Saves all conversations to learn patterns
2. **Learning System**: Extracts patterns from successful conversations
3. **API Integration**: Can use OpenAI, local LLM, or Hugging Face APIs

## Configuration Options

### Option 1: Use OpenAI API (Recommended for best results)

1. **Get OpenAI API Key**:
   - Sign up at https://platform.openai.com
   - Get your API key from the dashboard

2. **Set Environment Variables**:
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="your-api-key-here"
   $env:USE_OPENAI="true"
   
   # Or create a .env file in sanad_backend/
   OPENAI_API_KEY=your-api-key-here
   USE_OPENAI=true
   ```

3. **Install OpenAI Library**:
   ```bash
   pip install openai
   ```

### Option 2: Use Local LLM (Free, but requires setup)

1. **Install Ollama** (or similar):
   - Download from https://ollama.ai
   - Install and run: `ollama pull llama2`

2. **Set Environment Variables**:
   ```bash
   $env:USE_LOCAL_LLM="true"
   $env:LOCAL_LLM_URL="http://localhost:11434"
   ```

### Option 3: Use Current System (No API needed)
- The system will work with rule-based responses
- It will still learn from conversations
- No additional setup needed

## How It Works

1. **User sends message** → System analyzes sentiment and mental health context
2. **Check for API** → If configured, tries to get AI response from API
3. **Fallback** → If no API or API fails, uses rule-based therapeutic responses
4. **Save & Learn** → Every conversation is saved and patterns are extracted
5. **Improve** → Learned patterns influence future responses

## Data Storage

- **Location**: `sanad_backend/conversation_data/`
- **Files**:
  - `conversation_history.json` - All conversation history
  - `learned_patterns.json` - Extracted successful patterns

## Testing

1. **Without API** (current setup):
   - Just use the chatbot - it will learn from conversations
   - Responses use rule-based system

2. **With OpenAI API**:
   - Set environment variables
   - Restart backend
   - Chatbot will use GPT-3.5/GPT-4 for responses

3. **With Local LLM**:
   - Start Ollama: `ollama serve`
   - Set environment variables
   - Restart backend
   - Chatbot will use local model

## Next Steps for Training

See `TRAINING_GUIDE.md` for instructions on:
- Fine-tuning models on mental health data
- Creating custom datasets
- Training your own model

