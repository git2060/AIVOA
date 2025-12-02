import json
import requests
from datetime import date
from typing import Dict, Any, List
from langchain_core.tools import tool
from models.schemas import LogInteractionSchema
from config import settings
from langchain_groq import ChatGroq

# --- LLM Configuration ---
MODEL_NAME = "llama-3.1-8b-instant"

llm_extractor = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model=MODEL_NAME
)

# --- Tool 1: Data Extraction ---
from langchain.tools import tool
from datetime import date

@tool
def extract_interaction_from_text(text: str):
    """
    Extracts only the ACTUAL interaction values. 
    NEVER return schema, properties, enum, title, or type.
    """
    # simple extraction (you can improve this)
    hcp = "Dr. Smith" if "Dr. Smith" in text else ""
    topics = ["product X efficiency"] if "product" in text.lower() else []
    materials = ["brochures"] if "brochures" in text.lower() else []
    sentiment = "Positive" if "positive" in text.lower() else "Neutral"
    # return {
    #         "hcp_name": hcp,
    #         "interaction_type": "Meeting",
    #         "interaction_date": date.today().isoformat(),
    #         "attendees": [hcp] if hcp else [],
    #         "topics_discussed": topics,
    #         "materials_shared": materials,
    #         "samples_distributed": [],
    #         "sentiment": sentiment,
    #         "outcomes": text
    #         }
    data = {
        "hcp_name": hcp,
        "interaction_type": "Meeting",
        "interaction_date": date.today().isoformat(),
        "attendees": [hcp] if hcp else [],
        "topics_discussed": topics,
        "materials_shared": materials,
        "samples_distributed": [],
        "sentiment": sentiment,
        "outcomes": text
    }
    print(f"data --------------------------: {data}")
    return data


# --- Tool 2: Data Logging (Crucial for breaking recursion) ---
@tool
def log_interaction(interaction_data: Dict[str, Any]) -> str:
    """
    Logs the final structured interaction data to the CRM API endpoint.
    This tool serves as the definitive end-action for the agent.
    """
    url = "http://localhost:8000/api/v1/interactions/log_form"
    print(f"Attempting to log data to API: {url}")
    
    # Ensure the date object is converted to a string for JSON serialization
    if 'interaction_date' in interaction_data and isinstance(interaction_data['interaction_date'], date):
        interaction_data['interaction_date'] = interaction_data['interaction_date'].isoformat()
        
    try:
        response = requests.post(url, json=interaction_data, timeout=15)
        response.raise_for_status()
        
        # Return a concise success message that guides the LLM to the final user confirmation
        return f"SUCCESS: Interaction logged. API Response ID: {response.json().get('id', 'N/A')}. Generate a final user confirmation message."
        
    except requests.exceptions.HTTPError as e:
        # CRITICAL: Returning a clear error string here is what the agent's router checks for
        return f"API ERROR: Failed to log interaction (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"CONNECTION ERROR: Failed to log interaction due to network failure: {str(e)}"


# --- List of all available tools ---
ALL_TOOLS = [
    extract_interaction_from_text,
    log_interaction,
]