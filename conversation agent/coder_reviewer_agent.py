
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from autogen import ConversableAgent
from utils import get_gemini_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve API Key
GOOGLE_API_KEY = get_gemini_api_key()

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    exit(1)

# Configure Gemini for AutoGen
# Note: AG2 (formerly AutoGen) standard dictionary configuration.
llm_config = {
    "config_list": [
        {
            "model": "gemini-2.0-flash",
            "api_key": GOOGLE_API_KEY,
            "api_type": "google"
        }
    ]
}

# Define agents
coder = ConversableAgent(
    name="coder",
    system_message="You are a Python developer. Write short Python scripts.",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

reviewer = ConversableAgent(
    name="reviewer",
    system_message="You are a code reviewer. Analyze provided code and suggest improvements. "
                   "Do not generate code, only suggest improvements.",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

print("--- Starting Code & Review ---")

# Start a conversation
# Note: initiate_chat returns a ChatResult object in newer versions
chat_result = reviewer.initiate_chat(
    recipient=coder,
    message="Write a Python function that computes Fibonacci numbers.",
    max_turns=3
)

# In AG2/AutoGen, 'chat_result' contains the history and summary
print("\n--- Summary ---")
# Depending on version, it might print chat_result.summary or chat_result.chat_history
print(chat_result)