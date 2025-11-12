# --- Load Model Once at Startup ---
try:
    from transformers import pipeline
    # Using a common sentiment model placeholder for quick start
    # You would replace this with your fine-tuned security/mental health model
    sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception as e:
    print(f"Error loading AI model or dependencies: {e}")
    print("Backend will run without AI functionality. Please install Visual C++ Redistributables to fix PyTorch.")
    sentiment_model = None

def analyze_sentiment_and_risk(text: str) -> dict:
    """Analyzes text for sentiment and estimates risk level."""
    if not sentiment_model:
        # Fallback: Simple keyword-based analysis when AI model is unavailable
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in ["end it all", "suicide", "hurt myself"]):
            return {"sentiment": "NEGATIVE", "risk_score": 0.99}
        elif any(keyword in text_lower for keyword in ["sad", "depressed", "hopeless", "anxious"]):
            return {"sentiment": "NEGATIVE", "risk_score": 0.5}
        else:
            return {"sentiment": "POSITIVE", "risk_score": 0.0}

    # 1. Run inference
    result = sentiment_model(text)[0]
    
    # 2. Simple Risk Logic (Placeholder for Complex NLP logic)
    risk_score = 0.0
    if result['label'] == 'NEGATIVE' and result['score'] > 0.8:
        # Simple keyword check for extreme risk (MUST BE ADVANCED LATER)
        if any(keyword in text.lower() for keyword in ["end it all", "suicide", "hurt myself"]):
            risk_score = 0.99  # IMMEDIATE INTERVENTION
        else:
            risk_score = result['score'] * 0.5  # Moderate Risk

    return {
        "sentiment": result['label'],
        "risk_score": round(risk_score, 2)
    }

def analyze_mental_health_context(text: str) -> dict:
    """Analyzes text for mental health context and symptoms."""
    text_lower = text.lower()
    
    # Mental health conditions and symptoms
    conditions = {
        "depression": ["depression", "depressed", "sad", "hopeless", "worthless", "empty", "numb"],
        "anxiety": ["anxiety", "anxious", "worried", "panic", "fear", "nervous", "stressed"],
        "suicidal": ["suicide", "kill myself", "end it all", "hurt myself", "not worth living"],
        "trauma": ["trauma", "ptsd", "flashback", "triggered", "abuse", "assault"],
        "eating_disorder": ["eating disorder", "anorexia", "bulimia", "binge", "not eating"],
        "sleep": ["insomnia", "can't sleep", "sleeping too much", "nightmares"],
        "substance": ["alcohol", "drugs", "addiction", "using", "drinking too much"],
        "relationship": ["relationship", "breakup", "divorce", "lonely", "isolated"],
        "work": ["work stress", "job", "unemployed", "career", "boss"],
        "grief": ["grief", "loss", "death", "died", "mourning", "funeral"]
    }
    
    detected_conditions = []
    severity_indicators = []
    
    for condition, keywords in conditions.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_conditions.append(condition)
            # Check for severity indicators
            if any(severity in text_lower for severity in ["very", "extremely", "severe", "terrible", "awful", "worst"]):
                severity_indicators.append("high")
    
    # Extract key concerns
    concerns = []
    if "can't" in text_lower or "cannot" in text_lower:
        concerns.append("functionality_issues")
    if "help" in text_lower or "need" in text_lower:
        concerns.append("seeking_help")
    if "better" in text_lower or "improve" in text_lower:
        concerns.append("seeking_improvement")
    
    return {
        "conditions": detected_conditions,
        "severity": "high" if severity_indicators else "moderate" if detected_conditions else "low",
        "concerns": concerns,
        "needs_immediate_attention": "suicidal" in detected_conditions
    }

