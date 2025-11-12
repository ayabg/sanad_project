"""
AI API Service - Integrates with external APIs for intelligent responses.
Supports OpenAI API, local LLM models, and Hugging Face Inference API.
"""
import os
from typing import Optional, Dict
import requests

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434")  # For Ollama or similar

def get_ai_response(
    user_message: str,
    conversation_context: str = "",
    mental_health_context: Dict = None,
    learned_patterns: list = None
) -> Optional[str]:
    """
    Get AI-generated response using the configured API.
    
    Args:
        user_message: Current user message
        conversation_context: Previous conversation history
        mental_health_context: Detected mental health conditions and context
        learned_patterns: Learned successful response patterns
    
    Returns:
        AI-generated response or None if API unavailable
    """
    
    if USE_OPENAI and OPENAI_API_KEY:
        return get_openai_response(user_message, conversation_context, mental_health_context, learned_patterns)
    elif USE_LOCAL_LLM:
        return get_local_llm_response(user_message, conversation_context, mental_health_context, learned_patterns)
    else:
        # Fallback to rule-based (current system)
        return None

def get_openai_response(
    user_message: str,
    conversation_context: str = "",
    mental_health_context: Dict = None,
    learned_patterns: list = None
) -> Optional[str]:
    """Get response from OpenAI API."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Build system prompt with mental health expertise
        system_prompt = """You are Sanad, an expert mental health therapist and AI companion. Your role is to:
- Provide evidence-based, therapeutic responses
- Show empathy and understanding
- Offer practical coping strategies
- Recognize when professional help is needed
- Maintain appropriate boundaries
- Prioritize user safety above all

Guidelines:
- Always validate the user's feelings
- Use therapeutic techniques (CBT, DBT, mindfulness)
- Provide specific, actionable advice
- Never diagnose, but recognize symptoms
- Encourage professional help when appropriate
- Maintain a warm, professional tone"""
        
        # Build context-aware prompt
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        if conversation_context:
            messages.append({
                "role": "system",
                "content": f"Previous conversation context:\n{conversation_context}"
            })
        
        # Add mental health context
        if mental_health_context:
            conditions = mental_health_context.get("conditions", [])
            if conditions:
                messages.append({
                    "role": "system",
                    "content": f"Detected mental health context: {', '.join(conditions)}. Adjust your response accordingly."
                })
        
        # Add learned patterns if available
        if learned_patterns:
            messages.append({
                "role": "system",
                "content": f"Previously successful response patterns to consider: {learned_patterns[:3]}"
            })
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" for better quality
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
        
    except ImportError:
        print("OpenAI library not installed. Install with: pip install openai")
        return None
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def get_local_llm_response(
    user_message: str,
    conversation_context: str = "",
    mental_health_context: Dict = None,
    learned_patterns: list = None
) -> Optional[str]:
    """Get response from local LLM (Ollama, LM Studio, etc.)."""
    try:
        # Build prompt
        prompt = f"""You are Sanad, an expert mental health therapist AI companion.

Previous conversation:
{conversation_context if conversation_context else "This is the start of the conversation."}

Mental health context: {mental_health_context.get('conditions', []) if mental_health_context else 'None detected'}

User message: {user_message}

Provide a therapeutic, empathetic, and helpful response. Be specific and evidence-based. Keep response under 200 words."""

        # Call local LLM API (Ollama format)
        response = requests.post(
            f"{LOCAL_LLM_URL}/api/generate",
            json={
                "model": "llama2",  # or "mistral", "phi", etc.
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            print(f"Local LLM API error: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Local LLM connection error: {e}")
        return None
    except Exception as e:
        print(f"Local LLM error: {e}")
        return None

def get_huggingface_response(
    user_message: str,
    conversation_context: str = "",
    mental_health_context: Dict = None
) -> Optional[str]:
    """Get response from Hugging Face Inference API."""
    try:
        from transformers import pipeline
        
        # Use a conversational model
        generator = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-medium",
            max_length=200,
            temperature=0.7
        )
        
        # Build context
        context = f"{conversation_context}\nUser: {user_message}\nTherapist:"
        
        response = generator(context, max_length=len(context.split()) + 50)[0]['generated_text']
        
        # Extract just the therapist response
        if "Therapist:" in response:
            return response.split("Therapist:")[-1].strip()
        
        return response.strip()
        
    except Exception as e:
        print(f"Hugging Face API error: {e}")
        return None

