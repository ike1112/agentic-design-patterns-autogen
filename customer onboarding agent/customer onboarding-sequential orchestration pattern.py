
import os
import sys
from dotenv import load_dotenv, find_dotenv
from autogen import ConversableAgent, initiate_chats

# --------------------------------------------------------------------------------
# Logger Class: Streams output to both Console and File
# --------------------------------------------------------------------------------
class Logger(object):
    def __init__(self, filename="log.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        # needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        self.terminal.flush()
        self.log.flush()

# Redirect stdout to the Logger
sys.stdout = Logger()

# Load environment variables
load_dotenv(find_dotenv())

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY or GEMINI_API_KEY not found in environment variables.")
    exit(1)

# Configuration for Gemini
llm_config = {
    "config_list": [
        {
            "model": "gemini-2.0-flash",
            "api_key": GOOGLE_API_KEY,
            "api_type": "google"
        }
    ]
}

# --------------------------------------------------------------------------------
# Creating the needed agents
# --------------------------------------------------------------------------------

onboarding_personal_information_agent = ConversableAgent(
    name="Onboarding Personal Information Agent",
    system_message='''You are a helpful customer onboarding agent,
    you are here to help new customers get started with our product.
    Your job is to gather customer's name and location.
    Do not ask for other information. Return 'TERMINATE' 
    when you have gathered all the information.''',
    llm_config=llm_config,
    code_execution_config=False,
    human_input_mode="NEVER",
)

onboarding_topic_preference_agent = ConversableAgent(
    name="Onboarding Topic preference Agent",
    system_message='''You are a helpful customer onboarding agent,
    you are here to help new customers get started with our product.
    Your job is to gather customer's preferences on news topics.
    Do not ask for other information.
    Return 'TERMINATE' when you have gathered all the information.''',
    llm_config=llm_config,
    code_execution_config=False,
    human_input_mode="NEVER",
)

customer_engagement_agent = ConversableAgent(
    name="Customer Engagement Agent",
    system_message='''You are a helpful customer service agent
    here to provide fun for the customer based on the user's
    personal information and topic preferences.
    This could include fun facts, jokes, or interesting stories.
    Make sure to make it engaging and fun!
    Return 'TERMINATE' when you are done.''',
    llm_config=llm_config,
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "terminate" in msg.get("content", "").lower(),
)

# --------------------------------------------------------------------------------
# Customer Proxy Agent: Represents YOU (the human user)
# --------------------------------------------------------------------------------
customer_proxy_agent = ConversableAgent(
    name="customer_proxy_agent",
    llm_config=False,
    code_execution_config=False,
    human_input_mode="ALWAYS",
    is_termination_msg=lambda msg: "terminate" in msg.get("content", "").lower(),
)

# --------------------------------------------------------------------------------
# Creating tasks
# --------------------------------------------------------------------------------

chats = [
    # --------------------------------------------------------------------------------
    # Chat 1: Gather Profile Information
    # --------------------------------------------------------------------------------
    {
        "sender": onboarding_personal_information_agent,
        "recipient": customer_proxy_agent,
        "message": 
            "Hello, I'm here to help you get started with our product."
            "Could you tell me your name and location?",
        "summary_method": "reflection_with_llm",
        "summary_args": {
            "summary_prompt" : "Return the customer information "
                             "into as JSON object only: "
                             "{'name': '', 'location': ''}",
        },
        "max_turns": 4,
        "clear_history" : True
    },
    # --------------------------------------------------------------------------------
    # Chat 2: Gather Preferences
    # --------------------------------------------------------------------------------
    {
        "sender": onboarding_topic_preference_agent,
        "recipient": customer_proxy_agent,
        "message": 
                "Great! Could you tell me what topics you are "
                "interested in reading about?",
        "summary_method": "reflection_with_llm",
        "max_turns": 2,
        "clear_history" : False
    },
    # --------------------------------------------------------------------------------
    # Chat 3: Deliver Content
    # --------------------------------------------------------------------------------
    {
        "sender": customer_proxy_agent,
        "recipient": customer_engagement_agent,
        "message": "Let's find something fun to read.",
        "max_turns": 1,
        "summary_method": "reflection_with_llm",
    },
]

# --------------------------------------------------------------------------------
# Start the onboarding process
# --------------------------------------------------------------------------------

print("Starting Sequential Chats...")
chat_results = initiate_chats(chats)

# --------------------------------------------------------------------------------
# Print out the summary and cost
# --------------------------------------------------------------------------------

print("\n--- Final Results ---")
for i, chat_result in enumerate(chat_results):
    print(f"\n--- Chat {i+1} Summary ---")
    print(chat_result.summary)
    print(f"--- Chat {i+1} Cost ---")
    print(chat_result.cost)

