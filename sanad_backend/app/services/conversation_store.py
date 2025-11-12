"""
Conversation storage and learning system.
Stores conversation history and learns patterns from user interactions.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# Simple file-based storage (in production, use a database)
STORAGE_DIR = "conversation_data"
HISTORY_FILE = os.path.join(STORAGE_DIR, "conversation_history.json")
LEARNED_PATTERNS_FILE = os.path.join(STORAGE_DIR, "learned_patterns.json")

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

def load_conversation_history(session_id: str) -> List[Dict]:
    """Load conversation history for a session."""
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            all_history = json.load(f)
            return all_history.get(session_id, [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_conversation(session_id: str, user_message: str, bot_response: str, context: Dict):
    """Save a conversation turn to history."""
    if not os.path.exists(HISTORY_FILE):
        all_history = {}
    else:
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                all_history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            all_history = {}
    
    if session_id not in all_history:
        all_history[session_id] = []
    
    conversation_turn = {
        "timestamp": datetime.now().isoformat(),
        "user_message": user_message,
        "bot_response": bot_response,
        "context": context,  # Includes sentiment, risk_score, conditions detected
    }
    
    all_history[session_id].append(conversation_turn)
    
    # Keep only last 50 conversations per session
    all_history[session_id] = all_history[session_id][-50:]
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_history, f, indent=2, ensure_ascii=False)

def get_conversation_context(session_id: str, last_n: int = 5) -> str:
    """Get recent conversation context as a string for API prompts."""
    history = load_conversation_history(session_id)
    if not history:
        return ""
    
    recent = history[-last_n:]
    context_parts = []
    for turn in recent:
        context_parts.append(f"User: {turn['user_message']}")
        context_parts.append(f"Therapist: {turn['bot_response']}")
    
    return "\n".join(context_parts)

def learn_from_conversation(session_id: str, user_message: str, bot_response: str, user_satisfaction: Optional[bool] = None):
    """Learn patterns from conversations (simple pattern extraction)."""
    if not os.path.exists(LEARNED_PATTERNS_FILE):
        patterns = {}
    else:
        try:
            with open(LEARNED_PATTERNS_FILE, 'r', encoding='utf-8') as f:
                patterns = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            patterns = {}
    
    # Extract key phrases from user messages
    key_phrases = extract_key_phrases(user_message)
    
    for phrase in key_phrases:
        if phrase not in patterns:
            patterns[phrase] = {
                "count": 0,
                "successful_responses": [],
                "contexts": []
            }
        
        patterns[phrase]["count"] += 1
        if user_satisfaction:
            patterns[phrase]["successful_responses"].append(bot_response)
        patterns[phrase]["contexts"].append({
            "user_msg": user_message,
            "bot_response": bot_response
        })
    
    # Keep only top patterns
    with open(LEARNED_PATTERNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)

def extract_key_phrases(text: str) -> List[str]:
    """Extract key phrases from text for learning."""
    text_lower = text.lower()
    key_phrases = []
    
    # Common mental health phrases
    mental_health_phrases = [
        "i feel", "i'm feeling", "i have", "i can't", "i don't",
        "depression", "anxious", "sad", "worried", "stressed",
        "help me", "i need", "i want", "i wish"
    ]
    
    for phrase in mental_health_phrases:
        if phrase in text_lower:
            key_phrases.append(phrase)
    
    return key_phrases

def get_learned_responses(key_phrase: str) -> List[str]:
    """Get learned successful responses for a key phrase."""
    if not os.path.exists(LEARNED_PATTERNS_FILE):
        return []
    
    try:
        with open(LEARNED_PATTERNS_FILE, 'r', encoding='utf-8') as f:
            patterns = json.load(f)
            if key_phrase in patterns:
                return patterns[key_phrase].get("successful_responses", [])
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    
    return []

