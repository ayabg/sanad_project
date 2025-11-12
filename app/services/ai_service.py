
import httpx
import json
from typing import List, Dict, Any

# Structure pour les messages de l'historique (doit correspondre à la structure dans chat.py)
class HistoryMessage(BaseModel):
    role: str
    content: str

# L'adresse locale par défaut d'Ollama
OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "phi3" # Assurez-vous que c'est bien le modèle que vous avez lancé

# Le Prompt Système pour la personnalisation
SYSTEM_PROMPT = (
    "Tu es Sanad. Tu es un compagnon de soutien psychologique par IA. "
    "Tes réponses doivent être courtes, extrêmement empathiques, sans jugement, et réconfortantes. "
    "Tu dois toujours valider le sentiment de l'utilisateur avant de suggérer une action. "
    "N'offre jamais de conseils médicaux ou un diagnostic. Réponds en français."
)

async def analyze_and_respond(user_text: str, history: List[HistoryMessage]) -> Dict[str, Any]:
    """
    Parle à l'API Ollama, inclut le System Prompt et l'Historique.
    """
    
 messages = [
    {"role": "system", "content": SYSTEM_PROMPT} # C'est le premier message crucial
]
# ... puis l'historique et le message utilisateur
    
    # Ajout de l'historique (messages précédents)
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
        
    # Ajout du message actuel de l'utilisateur
    messages.append({"role": "user", "content": user_text})
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False # Nous voulons la réponse complète d'un coup
    }

    async with httpx.AsyncClient(timeout=100.0) as client:
        try:
            response = await client.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP (4xx/5xx)
            
            data = response.json()
            ai_response_content = data['message']['content']
            
            # 2. **Étape Cruciale: Analyse du Sentiment/Risque (Hypothétique)**
            # IMPORTANT: Phi-3 vous donnera une réponse *personnalisée*, mais vous devez
            # toujours avoir un modèle de classification de risque SÉPARÉ ou une logique
            # basée sur des mots-clés pour définir le 'risk_score' (pour le protocole d'urgence).
            
            # --- Placeholder pour l'analyse de risque/sentiment ---
            # Pour l'exemple, nous allons juste faire une détection de risque basée sur des mots-clés simples
            # Idéalement, Phi-3 devrait être invité à CLASSIFIER le risque lui-même dans un appel séparé
            risk_score = 0.0
            if any(keyword in user_text.lower() for keyword in ["mourir", "finir", "plus supporter"]):
                risk_score = 0.99
            # --------------------------------------------------------

            return {
                "response_text": ai_response_content,
                "risk_score": risk_score,
                "sentiment": "NEGATIVE" if risk_score > 0 else "UNKNOWN" 
            }
            
        except httpx.HTTPStatusError as e:
            print(f"Ollama API Error: {e}")
            return {"response_text": "Désolé, je n'arrive pas à communiquer avec mon cœur d'IA (Erreur HTTP).", "risk_score": 0.0, "sentiment": "ERROR"}
        except Exception as e:
            print(f"General AI Error: {e}")
            return {"response_text": "Une erreur inattendue est survenue lors de l'analyse.", "risk_score": 0.0, "sentiment": "ERROR"}