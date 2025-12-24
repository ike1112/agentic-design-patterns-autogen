# Reflection Agent Pattern: Blog Post Writer

This project demonstrates the **Reflection** agentic design pattern using AutoGen. It features a Writer agent that collaborates with a Critic agent (who manages a team of specialized reviewers) to iteratively refine and improve a blog post.

## 🧠 Key Insights & Design Pattern

The core concept demonstrated here is **Reflection with Nested Chats**.

1.  **Iterative Refinement**: Instead of accepting the first draft, the system forces a feedback loop. The Writer produces a draft, and the Critic reviews it.
2.  **The "Manager" Critic**: The Critic agent isn't just a simple LLM prompt. It acts as a **manager** for a "Review Council."
    *   When the Critic receives a draft, it triggers a **Nested Chat**.
    *   It consults specialized agents: **SEO Reviewer**, **Legal Reviewer**, and **Ethics Reviewer**.
    *   A **Meta Reviewer** aggregates all their specific feedback into one cohesive response.
3.  **Separation of Concerns**: By splitting the review process into specialized roles (SEO, Legal, Ethics), we get much higher quality, targeted feedback than asking a single model to "review for everything."

## 📂 Files

*   `reflection_and_blogpost_writing.py`: The main script that orchestrates the agents.
*   `../utils.py`: Shared utility for loading API keys.

## 🚀 How It Works (Flow)

1.  **Writer** generates an initial blog post about DeepLearning.AI.
2.  **Critic** receives the message.
3.  **Trigger**: The Critic's `register_nested_chats` detects the message from the Writer.
4.  **Nested Reflection**:
    *   **SEO Agent** checks for keywords and traffic potential.
    *   **Legal Agent** checks for compliance issues.
    *   **Ethics Agent** ensures the content is sound.
    *   **Meta Reviewer** combines all checks into a final critique.
5.  **Feedback**: The Writer receives the Meta Reviewer's feedback and updates the blog post.
6.  This cycle repeats for a maximum of 2 turns.

## 🛠️ How to Run

Ensure you have your environment set up and the `GOOGLE_API_KEY` loaded in your `.env` file.

```bash
python reflection_and_blogpost_writing.py
```
