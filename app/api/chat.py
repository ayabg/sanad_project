from fastapi import APIRouter
from pydantic import BaseModel
from ..services.ai_service import analyze_sentiment_and_risk # Import the AI core

router = APIRouter()

# Data validation for incoming message
# app/api/chat.py

    # app/api/chat.py - Ajoutez ceci en haut
from typing import List

# Structure pour un message unique dans l'historique
class HistoryMessage(BaseModel):
    role: str  # 'user' ou 'assistant'
    content: str

# Structure de la requête entrante complète
class MessageIn(BaseModel):
    user_session_id: str
    text: str
    history: List[HistoryMessage] = [] # Ajout de l'historique
# Data validation for outgoing response
class MessageOut(BaseModel):
    response_text: str
    action: str  # e.g., 'CONTINUE_CHAT', 'EMERGENCY_TRIGGERED'

@router.post("/message", response_model=MessageOut)
async def handle_user_message(msg: MessageIn):
    # 1. AI Analysis
    ai_data = analyze_sentiment_and_risk(msg.text)
    risk_score = ai_data["risk_score"]
    sentiment = ai_data["sentiment"]

    # 2. Response Logic Engine (The Safety Triage)
    response_text = "I hear you. Tell me more about what you're feeling."
    action = "CONTINUE_CHAT"

    if risk_score >= 0.95:
        # *** CRISIS INTERVENTION ***
        response_text = "⚠️ **EMERGENCY INTERVENTION:** Your safety is paramount. Please contact a local crisis hotline immediately. We are here, but you need human help now."
        action = "EMERGENCY_TRIGGERED"
    elif sentiment == 'NEGATIVE' and risk_score >= 0.5:
        # Guided Exercise (UX: offer support)
        response_text = "That sounds incredibly heavy. Would you like to try a 3-minute guided breathing exercise?"
        action = "GUIDED_EXERCISE"
    
    # 3. Secure Logging (Database logic omitted for brevity, but crucial!)
    
    return MessageOut(response_text=response_text, action=action)
# app/api/chat.py
# (Assurez-vous d'importer HistoryMessage et d'utiliser la nouvelle classe MessageIn)

from fastapi import APIRouter
from pydantic import BaseModel
# Importez la nouvelle fonction asynchrone
from ..services.ai_service import analyze_and_respond, HistoryMessage

router = APIRouter()

# Schémas MessageIn/MessageOut/HistoryMessage (assurez-vous qu'ils sont définis comme dans l'étape 2)

@router.post("/message", response_model=MessageOut)
async def handle_user_message(msg: MessageIn):
    
    # 1. AI Analysis and Response Generation (via Ollama)
    # On passe le texte actuel ET l'historique
# app/api/chat.py
ai_data = await analyze_and_respond(msg.text, msg.history)
    
    risk_score = ai_data["risk_score"]
    
    # La réponse est maintenant générée directement par Phi-3
    response_text = ai_data["response_text"]
    action = "CONTINUE_CHAT"
    
    # 2. Response Logic Engine (Le Triage de Sécurité)
    
    if risk_score >= 0.95:
        # 🚨 High-Risk Protocol (Priorité absolue)
        response_text = "⚠️ **INTERVENTION D'URGENCE:** Votre sécurité est notre priorité. Veuillez contacter un service d'urgence local immédiatement. La conversation est temporairement mise en pause."
        action = "EMERGENCY_TRIGGERED"
    elif ai_data["sentiment"] == 'NEGATIVE' and risk_score < 0.95:
        # Le modèle (Phi-3) aura déjà fourni une réponse empathique,
        # nous pouvons simplement ajouter une suggestion d'action si nécessaire.
        if "aide" in msg.text.lower():
             action = "GUIDED_EXERCISE"

    # Le Frontend devra maintenant envoyer l'historique de chat à chaque requête!
    return MessageOut(response_text=response_text, action=action)