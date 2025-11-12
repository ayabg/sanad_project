from fastapi import APIRouter
from pydantic import BaseModel
from ..services.ai_service import analyze_sentiment_and_risk, analyze_mental_health_context
from ..services.conversation_store import (
    get_conversation_context, 
    save_conversation, 
    learn_from_conversation,
    get_learned_responses
)
from ..services.ai_api_service import get_ai_response

router = APIRouter()

# Data validation for incoming message
class MessageIn(BaseModel):
    session_id: str  # For anonymous tracking
    text: str

# Data validation for outgoing response
class MessageOut(BaseModel):
    response_text: str
    action: str  # e.g., 'CONTINUE_CHAT', 'EMERGENCY_TRIGGERED'

@router.post("/message", response_model=MessageOut)
async def handle_user_message(msg: MessageIn):
    # 1. Get conversation history and context
    conversation_context = get_conversation_context(msg.session_id, last_n=5)
    
    # 2. AI Analysis - Sentiment and Risk
    ai_data = analyze_sentiment_and_risk(msg.text)
    risk_score = ai_data["risk_score"]
    sentiment = ai_data["sentiment"]
    
    # 3. Mental Health Context Analysis
    health_context = analyze_mental_health_context(msg.text)
    conditions = health_context["conditions"]
    severity = health_context["severity"]
    concerns = health_context["concerns"]
    
    text_lower = msg.text.lower().strip()
    
    # 4. Check for learned patterns
    key_phrases = [phrase for phrase in ["i feel", "i'm feeling", "i have", "depression", "anxious"] if phrase in text_lower]
    learned_responses = []
    for phrase in key_phrases:
        learned_responses.extend(get_learned_responses(phrase))
    
    # 5. Try to get AI API response first (if configured)
    api_response = get_ai_response(
        user_message=msg.text,
        conversation_context=conversation_context,
        mental_health_context=health_context,
        learned_patterns=learned_responses[:2] if learned_responses else None
    )
    
    # 6. Therapeutic Response Logic (Doctor-like approach)
    response_text = ""
    action = "CONTINUE_CHAT"
    
    # CRISIS INTERVENTION - Highest Priority (always use rule-based for safety)
    if risk_score >= 0.95 or health_context["needs_immediate_attention"]:
        response_text = "⚠️ **CRISIS SUPPORT:** I'm deeply concerned about your safety. Your life has value and meaning. Please reach out immediately:\n\n• National Suicide Prevention Lifeline: 988 (US)\n• Crisis Text Line: Text HOME to 741741\n• Emergency Services: 911\n\nYou don't have to face this alone. Professional help is available right now."
        action = "EMERGENCY_TRIGGERED"
    
    # Use API response if available (and not a crisis)
    elif api_response:
        response_text = api_response
    else:
        # Fall back to rule-based responses
        
        # DEPRESSION - Therapeutic Response
        if "depression" in conditions:
            if severity == "high":
                response_text = "I understand you're experiencing significant depression. This is a real medical condition, not a character flaw. Let's work through this together.\n\n• **What you're feeling is valid** - Depression affects how you think, feel, and function.\n• **You're not alone** - Many people recover with proper support.\n• **Let's identify triggers** - Can you tell me what situations or thoughts make it worse?\n• **Consider professional help** - A therapist or psychiatrist can provide evidence-based treatments.\n\nWhat would be most helpful right now - talking through your feelings, or learning coping strategies?"
            else:
                response_text = "I hear that you're dealing with depression. This can feel overwhelming, but there are effective ways to manage it.\n\n• **Understanding your patterns** - When do you notice these feelings most?\n• **Small steps matter** - Even getting out of bed or showering is progress.\n• **Professional support** - Therapy and sometimes medication can be very effective.\n\nCan you share more about how long you've been feeling this way, or what's been most difficult?"
        
        # ANXIETY - Therapeutic Response
        elif "anxiety" in conditions:
            response_text = "Anxiety can be very distressing. Let me help you understand and manage it.\n\n• **What's happening** - Anxiety is your body's alarm system. It's trying to protect you, but sometimes it's overly sensitive.\n• **Grounding techniques** - Let's try the 5-4-3-2-1 method: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.\n• **Breathing exercise** - Breathe in for 4, hold for 4, out for 6. This activates your body's relaxation response.\n• **Long-term strategies** - Cognitive Behavioral Therapy (CBT) is highly effective for anxiety.\n\nWhat triggers your anxiety most? Understanding this helps us develop better coping strategies."
            action = "GUIDED_EXERCISE"
        
        # TRAUMA - Therapeutic Response
        elif "trauma" in conditions:
            response_text = "I recognize you've experienced trauma. Healing from trauma takes time and the right support.\n\n• **Your response is normal** - Trauma responses are your body's way of trying to protect you.\n• **Safety first** - Are you currently in a safe environment?\n• **Professional trauma therapy** - EMDR, trauma-focused CBT, or somatic therapy can be very helpful.\n• **Self-care** - Grounding exercises, maintaining routines, and connecting with trusted people.\n\nWould you like to talk about what happened, or focus on coping strategies for now? You're in control of this conversation."
        
        # SLEEP ISSUES - Therapeutic Response
        elif "sleep" in conditions:
            response_text = "Sleep problems often go hand-in-hand with mental health challenges. Let's address this systematically.\n\n• **Sleep hygiene** - Same bedtime/wake time, cool dark room, no screens 1 hour before bed.\n• **Relaxation routine** - Try progressive muscle relaxation or guided meditation before bed.\n• **Address underlying issues** - Sleep problems can be symptoms of depression, anxiety, or trauma.\n• **Consider evaluation** - A sleep study might be helpful if this persists.\n\nHow long have you been experiencing sleep issues? And are you having trouble falling asleep, staying asleep, or both?"
        
        # RELATIONSHIP ISSUES - Therapeutic Response
        elif "relationship" in conditions:
            response_text = "Relationship difficulties can significantly impact our mental health. Let's explore this together.\n\n• **Your feelings matter** - Whether it's loneliness, conflict, or loss, these are valid concerns.\n• **Communication patterns** - What communication styles have you noticed in your relationships?\n• **Boundaries** - Healthy boundaries are essential for mental wellbeing.\n• **Support systems** - Who in your life can you trust and rely on?\n\nCan you tell me more about the relationship challenges you're facing? Understanding the specifics helps me provide better guidance."
        
        # WORK STRESS - Therapeutic Response
        elif "work" in conditions:
            response_text = "Work-related stress is a common concern that can significantly impact mental health.\n\n• **Identify stressors** - What specific aspects of work are most challenging?\n• **Work-life balance** - Are you able to disconnect from work during off-hours?\n• **Boundaries** - Setting clear professional boundaries is crucial for mental health.\n• **Support** - Consider discussing accommodations with HR or seeking employee assistance programs.\n\nWhat would help most - strategies to manage work stress, or exploring career changes?"
        
        # GRIEF - Therapeutic Response
        elif "grief" in conditions:
            response_text = "Grief is a natural response to loss, and everyone experiences it differently.\n\n• **No timeline** - There's no 'right' way or timeline for grieving.\n• **Allow feelings** - It's okay to feel sadness, anger, confusion, or even relief.\n• **Self-compassion** - Be gentle with yourself during this time.\n• **Support** - Grief counseling or support groups can be very helpful.\n• **Rituals** - Creating meaningful ways to honor the person you've lost can aid healing.\n\nWould you like to share more about your loss, or focus on coping strategies?"
        
        # EATING DISORDERS - Therapeutic Response
        elif "eating_disorder" in conditions:
            response_text = "Eating disorders are serious medical conditions that require professional treatment.\n\n• **This is treatable** - Recovery is possible with the right support.\n• **Professional help is essential** - Please consider speaking with a therapist specializing in eating disorders and a registered dietitian.\n• **Medical evaluation** - A doctor should assess your physical health.\n• **Support groups** - Connecting with others in recovery can be valuable.\n\nYour health and wellbeing matter. Would you like help finding resources for professional treatment?"
        
        # SUBSTANCE USE - Therapeutic Response
        elif "substance" in conditions:
            response_text = "Substance use concerns often relate to underlying mental health issues. Let's address this with care.\n\n• **No judgment** - I'm here to support you, not judge.\n• **Dual diagnosis** - Often substance use and mental health conditions need to be treated together.\n• **Professional support** - Consider speaking with an addiction counselor or therapist.\n• **Harm reduction** - If you're not ready to stop completely, we can discuss safer use strategies.\n• **Support groups** - AA, NA, SMART Recovery, or other groups provide community support.\n\nWhat would be most helpful - discussing treatment options, or exploring what's driving the substance use?"
        
        # POSITIVE RESPONSES TO OFFERS
        elif any(word in text_lower for word in ["yes", "sure", "ok", "okay", "yeah", "yep", "alright", "let's", "let us"]):
            if "breathing" in text_lower or "exercise" in text_lower or len(msg.text) < 10:
                response_text = "Excellent. Let's practice deep breathing together. This activates your body's relaxation response.\n\n**Step 1:** Find a comfortable seated or lying position.\n**Step 2:** Close your eyes if comfortable, or soften your gaze.\n**Step 3:** Breathe in slowly through your nose for 4 counts... (1... 2... 3... 4...)\n**Step 4:** Hold your breath for 4 counts... (1... 2... 3... 4...)\n**Step 5:** Exhale slowly through your mouth for 6 counts... (1... 2... 3... 4... 5... 6...)\n\nRepeat this cycle 5-10 times. Notice how your body feels. I'm here with you."
                action = "GUIDED_EXERCISE"
            else:
                response_text = "I'm glad you're open to working on this. What specific aspect would you like to focus on first?"
                action = "CONTINUE_CHAT"
        
        # QUESTIONS
        elif any(word in text_lower for word in ["how", "what", "when", "where", "why", "explain", "tell me"]):
            if "breathing" in text_lower or "exercise" in text_lower:
                response_text = "I'll guide you through a breathing exercise step-by-step:\n\n**The 4-4-6 Technique:**\n1. Inhale through your nose for 4 seconds\n2. Hold your breath for 4 seconds\n3. Exhale through your mouth for 6 seconds\n4. Repeat 5-10 times\n\nThis technique activates your parasympathetic nervous system, which helps calm anxiety and stress. The longer exhale is key - it signals safety to your body.\n\nWould you like to try it now?"
                action = "GUIDED_EXERCISE"
            else:
                response_text = "I'm here to help you understand and work through your concerns. What specific question can I help answer?"
                action = "CONTINUE_CHAT"
        
        # GREETINGS
        elif any(word in text_lower for word in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            response_text = "Hello. I'm Sanad, your mental health companion. I'm here to listen, support, and help you work through whatever you're experiencing. \n\nWhat brings you here today? You can share as much or as little as you're comfortable with."
            action = "CONTINUE_CHAT"
        
        # THANKS
        elif any(word in text_lower for word in ["thank", "thanks", "appreciate", "grateful"]):
            response_text = "You're very welcome. Taking care of your mental health is important, and I'm here to support you on this journey.\n\nHow are you feeling now? Is there anything else you'd like to discuss or work on?"
            action = "CONTINUE_CHAT"
        
        # NEGATIVE RESPONSES
        elif any(word in text_lower for word in ["no", "not", "don't", "can't", "won't", "nope"]):
            response_text = "That's completely okay. There's no pressure here - you're in control of this conversation.\n\nWhat would feel most helpful for you right now? We can explore other approaches, or simply talk."
            action = "CONTINUE_CHAT"
        
        # DEFAULT - Based on sentiment and context
        else:
            if sentiment == 'NEGATIVE' and risk_score >= 0.3:
                response_text = "I can sense you're going through something difficult. Your feelings are valid and important.\n\n• **Let's understand** - Can you tell me more about what you're experiencing?\n• **No judgment** - This is a safe space to share.\n• **Working together** - We can explore strategies to help you feel better.\n\nWhat's been weighing on you most?"
            elif concerns and "seeking_help" in concerns:
                response_text = "I'm glad you're reaching out - that takes courage. Let's work together to address what you're facing.\n\n• **Understanding your situation** - Can you share more about what's been challenging?\n• **Evidence-based approaches** - We can explore therapeutic techniques that have been proven effective.\n• **Professional support** - Sometimes working with a therapist alongside our conversations can be very helpful.\n\nWhat would you like to focus on first?"
            else:
                response_text = "I'm listening. Can you tell me more about what you're experiencing or what's on your mind? Understanding your situation better helps me provide more targeted support."
            action = "CONTINUE_CHAT"
    
    # 7. Save conversation and learn from it
    context_data = {
        "sentiment": sentiment,
        "risk_score": risk_score,
        "conditions": conditions,
        "severity": severity,
        "concerns": concerns
    }
    save_conversation(msg.session_id, msg.text, response_text, context_data)
    learn_from_conversation(msg.session_id, msg.text, response_text)
    
    return MessageOut(response_text=response_text, action=action)
