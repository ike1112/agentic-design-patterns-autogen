import autogen
from autogen import AssistantAgent
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import get_gemini_api_key

GOOGLE_API_KEY = get_gemini_api_key()

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    exit(1)

llm_config = {
    "config_list": [
        {
            "model": "gemini-2.0-flash",
            "api_key": GOOGLE_API_KEY,
            "api_type": "google"
        }
    ]
}

task = '''
        Write a concise but engaging blogpost about
       DeepLearning.AI. Make sure the blogpost is
       within 100 words.
       '''

writer = autogen.AssistantAgent(
    name="Writer",
    system_message="You are a writer. You write engaging and concise "
        "blogpost (with title) on given topics. You must polish your "
        "writing based on the feedback you receive and give a refined "
        "version. Only return your final work without additional comments.",
    llm_config=llm_config,
)



print("--- Adding Reflection ---")
critic = autogen.AssistantAgent(
    name="Critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=llm_config,
    system_message="You are a critic. You review the work of "
                "the writer and provide constructive "
                "feedback to help improve the quality of the content.",
)

print("--- Nested Chat Setup ---")
SEO_reviewer = autogen.AssistantAgent(
    name="SEO Reviewer",
    llm_config=llm_config,
    system_message="You are an SEO reviewer, known for "
        "your ability to optimize content for search engines, "
        "ensuring that it ranks well and attracts organic traffic. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role.",
)

legal_reviewer = autogen.AssistantAgent(
    name="Legal Reviewer",
    llm_config=llm_config,
    system_message="You are a legal reviewer, known for "
        "your ability to ensure that content is legally compliant "
        "and free from any potential legal issues. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role.",
)

ethics_reviewer = autogen.AssistantAgent(
    name="Ethics Reviewer",
    llm_config=llm_config,
    system_message="You are an ethics reviewer, known for "
        "your ability to ensure that content is ethically sound "
        "and free from any potential ethical issues. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role. ",
)

meta_reviewer = autogen.AssistantAgent(
    name="Meta Reviewer",
    llm_config=llm_config,
    system_message="You are a meta reviewer, you aggragate and review "
    "the work of other reviewers and give a final suggestion on the content.",
)

def reflection_message(recipient, messages, sender, config):
    return f'''Review the following content. 
            \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''

review_chats = [
    {
        "recipient": SEO_reviewer, 
        "message": reflection_message, 
        "summary_method": "reflection_with_llm",
        "summary_args": {
            "summary_prompt": "Return review into as JSON object only: {'Reviewer': '', 'Review': ''}. Here Reviewer should be your role",
        },
        "max_turns": 1
    },
    {
        "recipient": legal_reviewer, 
        "message": reflection_message, 
        "summary_method": "reflection_with_llm",
        "summary_args": {
            "summary_prompt": "Return review into as JSON object only: {'Reviewer': '', 'Review': ''}.",
        },
        "max_turns": 1
    },
    {
        "recipient": ethics_reviewer, 
        "message": reflection_message, 
        "summary_method": "reflection_with_llm",
        "summary_args": {
            "summary_prompt": "Return review into as JSON object only: {'reviewer': '', 'review': ''}",
        },
        "max_turns": 1
    },
    {
        "recipient": meta_reviewer, 
        "message": "Aggregrate feedback from all reviewers and give final suggestions on the writing.", 
        "max_turns": 1
    },
]

# --------------------------------------------------------------------------------
# Register Nested Chats: The Core Reflection Mechanism
# --------------------------------------------------------------------------------
# This function sets up the "Reflection" pattern. 
# Here is how it works:
# 1. TRIGGER: We set `trigger=writer`. This means whenever the `Critic` receives 
#    a message from the `Writer`, this nested chat sequence is automatically triggered.
# 2. SEQUENCE: The `Critic` will NOT reply immediately. Instead, it pauses and 
#    initiates the `review_chats` sequence we defined above effectively holding 
#    a side-meeting with the SEO, Legal, Ethics, and Meta agents.
# 3. RESPONSE: The output of the FINAL chat in the list (the Meta Reviewer's summary)
#    is automatically used as the `Critic`'s response back to the `Writer`.
critic.register_nested_chats(
    review_chats,
    trigger=writer,
)

# --------------------------------------------------------------------------------
# Execution Flow Explanation:
# --------------------------------------------------------------------------------
# 1. Start: The Critic initiates the chat and sends the `task` to the Writer.
# 2. Turn 1 (Writer): The Writer receives the task and generates **Draft 1**.
#    - TRIGGER: The Critic detects a message from the Writer.
#    - REFLECTION: The Critic pauses and runs the Nested Chats (SEO, Legal, Ethics, Meta).
# 3. Turn 1 (Critic): The Critic sends the aggregated feedback (from Meta Reviewer) to the Writer.
# 4. Turn 2 (Writer): The Writer receives the feedback, reflects on it, and generates **Draft 2** (Improved).
# 5. Stop: `max_turns=2` is reached. The conversation ends before the Critic can review Draft 2.
# 6. Result: The final output is **Draft 2**.

print("--- Starting Orchestrated Chat ---")
res = critic.initiate_chat(
    recipient=writer,
    message=task,
    max_turns=2,
    summary_method="last_msg"
)

print("--- Final Summary ---")
print(res.summary)
