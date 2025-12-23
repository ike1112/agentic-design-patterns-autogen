
import os
import autogen
from autogen import ConversableAgent
from utils import get_gemini_api_key

# Retrieve API Key
GOOGLE_API_KEY = get_gemini_api_key()

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    exit(1)

# Configure Gemini for AutoGen
# Note: AG2 (formerly AutoGen) supports Gemini via the 'google' api_type or 'openai' compatible endpoints.
# Since we installed 'ag2[openai]', we often use the 'google' type or the openai adapter.
# Standard 0.2 configuration for Gemini:
llm_config = {
    "config_list": [
        {
            "model": "gemini-2.0-flash",
            "api_key": GOOGLE_API_KEY,
            "api_type": "google"
        }
    ]
}

# Agent 1: Cathy
cathy = ConversableAgent(
    name="cathy",
    system_message="Your name is Cathy and you are a stand-up comedian. Tell brief, punchy jokes.",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

# Agent 2: Joe
joe = ConversableAgent(
    name="joe",
    system_message=(
        "Your name is Joe and you are a stand-up comedian. "
        "Start the next joke from the punchline of the previous joke."
    ),
    llm_config=llm_config,
    human_input_mode="NEVER",
)

print("--- Starting the Comedy Show (AG2) ---")

# Start the conversation
chat_result = joe.initiate_chat(
    recipient=cathy,
    message="I'm Joe. Cathy, let's keep the jokes rolling.",
    max_turns=2,
)

print("--- Show Over ---")
