
# Comedy Agent Demo (AG2 + Google Gemini)

This project demonstrates a multi-agent conversation pattern using **AG2** (formerly AutoGen). Two AI agents ("Joe" and "Cathy") autonomously interact, tell jokes, and maintain conversation state using Google's Gemini models.

## Prerequisites

*   **Python:** Version 3.10, 3.11, or 3.12 (Python 3.14 is **not** supported by AG2).
*   **AG2 Library:** The latest fork of AutoGen.
*   **Google API Key:** Access to Gemini models (e.g., `gemini-2.0-flash` or `gemini-pro`).

## Installation

1.  **Create a Virtual Environment** (Must use Python 3.12):
    ```powershell
    py -3.12 -m venv venv
    ```

2.  **Activate & Install Dependencies**:
    ```powershell
    # Windows
    venv\Scripts\activate.ps1
    
    # Install AG2 with OpenAI compatibility layer and Gemini support
    pip install ag2[openai] ag2[gemini] python-dotenv
    ```

3.  **Configuration**:
    Create a `.env` file in the project root:
    ```env
    GOOGLE_API_KEY=your_actual_api_key_here
    ```

## Usage

Run the agent script:

```powershell
venv\Scripts\python "conversation agent\comedy_agent.py"
```

## How It Works

1.  **Initialization:** Two `ConversableAgent` instances are created with specific personas (Joe = Comedian, Cathy = Comedian).
2.  **LLM Configuration:** They connect to Google's Gemini API via AG2's compatibility layer.
3.  **Chat Loop:** Joe initiates the chat. They exchange messages autonomously until the `max_turns` limit is reached.
