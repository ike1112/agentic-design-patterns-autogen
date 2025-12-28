"""
Design Pattern: Orchestrated Problem Solving (MagenticOne)

Why this Pattern?
-----------------
This script implements the 'MagenticOne' pattern, 
which is designed for complex, multi-step problems
where the solution path is NOT known in advance (like Incident Response).

Unlike a linear pipeline, the Orchestrator (built into MagenticOneGroupChat) dynamically delegates
tasks to specialized agents (Coder, FileSurfer) based on the current state of the investigation.

Implementation Note: Manual vs Helper Class
-------------------------------------------
While `MagenticOne(client=...)` exists as a helper, we implement the team MANUALLY here (`MagenticOneGroupChat`).
Reason: The `Coder` agent requires a Docker container for safe code execution. The high-level helper
does not automatically manage the asyncio lifecycle (start/stop) of the Docker container.
By Manually assembling the team, we can use the `async with` context manager to ensure the
Docker container is properly started before the agents try to use it.
"""

import asyncio
import os
import logging
import platform
from dotenv import load_dotenv

# AutoGen Core & Extensions
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.agents.magentic_one import MagenticOneCoderAgent
from autogen_ext.agents.file_surfer import FileSurfer
from autogen_ext.teams.magentic_one import MagenticOneGroupChat

load_dotenv()

async def run_magentic_one_orchestrator():
    # 0. Setup Logging
    logging.basicConfig(
        filename='magentic_one.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filemode='w'
    )
    print("Logging configured to write to 'magentic_one.log'")

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("Error: GEMINI_API_KEY not found.")
        return

    # 1. Define the Brain (Gemini 2.0 Flash)
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash-exp",
        api_key=gemini_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        model_info={
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
            "family": "gemini-2.0-flash-exp"
        }
    )

    # 2. Setup Incident Environment (Mock Data)
    print("Setting up mock incident environment...")
    log_content = """
2023-10-27 10:00:01 INFO [AuthService] User login successful: user_id=1001
2023-10-27 10:05:23 WARN [DbConnection] Pool usage at 85%
2023-10-27 10:06:00 ERROR [ApiGateway] 503 Service Unavailable - Upstream connect error
2023-10-27 10:06:01 ERROR [OrderService] ConnectionRefusedError: [Errno 111] Connection refused
    at /app/services/order.py:45 in create_order
    at /app/db/connection.py:12 in get_db
Caused by: FATAL: remaining connection slots are reserved for non-replication superuser connections
2023-10-27 10:06:05 INFO [HealthCheck] Retry attempt 1 failed
    """
    # Create logs in the current directory (Host)
    # The Docker container will need to access this.
    # By default, DockerExecutor mounts the workspace.
    with open("production_logs.txt", "w") as f:
        f.write(log_content)
    print("Created 'production_logs.txt' on Host.")

    task = (
        "You are an Incident Response Team. "
        "1. VERIFICATION STEP: Run a Python script to print the current OS (platform.platform()) and "
        "Working Directory (os.getcwd()) to prove you are in a container. "
        "2. Read the file 'production_logs.txt' to identify the error patterns. "
        "3. Determine the root cause of the 503 errors. "
        "4. Write a short 'post_mortem.txt' file summarizing the root cause and recommended fix."
    )

    print(f"[START] Starting Manual MagenticOne Team with Docker...\nTask: {task}\n")

    # 3. Create the Team MANUALLY to manage Docker lifecycle
    try:
        # --- CRITICAL CONFIGURATION ---
        # We use 'async with' to manage the Docker lifecycle.
        # This ensures the container is started before use and stopped/cleaned up after.
        # Failing to do this causes "ValueError: Container is not running".
        async with DockerCommandLineCodeExecutor(image="python:3.12-slim") as executor:
            
            # Agent 1: Coder
            # Uses the Docker executor to run Python code safely.
            # It can determine root causes by writing scripts to parse logs or test hypotheses.
            coder = MagenticOneCoderAgent("Coder", model_client=model_client, code_executor=executor)
            
            # Agent 2: FileSurfer
            # Allows the team to read local files (like our mock production logs).
            file_surfer = FileSurfer("FileSurfer", model_client=model_client)
            
            # Team: MagenticOneGroupChat
            # This is the "Brain". It contains a built-in Orchestrator agent that:
            # 1. Plans the next step.
            # 2. Selects the right agent (Coder or FileSurfer).
            # 3. Aggregates results.
            # 4. Decides when the task is complete.
            team = MagenticOneGroupChat(
                participants=[coder, file_surfer],
                model_client=model_client
            )

            # Run the Team
            result = await team.run(task=task)
            
            # --- Format & Save Result as Markdown ---
            # The 'result' object contains a list of messages. We want to extract the final output
            # which usually contains the post-mortem content or the final answer.
            
            markdown_content = "# Incident Response Report\n\n"
            markdown_content += "## Execution Log\n\n"
            
            for msg in result.messages:
                source = msg.source
                content = msg.content
                # Simple cleaning
                if isinstance(content, str):
                   markdown_content += f"### **{source}**\n\n"
                   markdown_content += f"{content}\n\n"
                   markdown_content += "---\n\n"

            with open("final_report.md", "w") as f:
                f.write(markdown_content)
                
            # Print Result
            print("\n--- FINAL RESULT ---")
            print(f"Report saved to 'final_report.md'")
            print("\nFull execution logs saved to 'magentic_one.log'")
            
    except Exception as e:
        print(f"\n[ERROR] execution failed: {e}")
        logging.error(f"Execution failed: {e}", exc_info=True)
        print("Please ensure Docker Desktop is running.")

if __name__ == "__main__":
    asyncio.run(run_magentic_one_orchestrator())

"""
--- KEY TAKEAWAYS (MagenticOne Pattern) ---

1. DYNAMIC ORCHESTRATION IS POWERFUL
   Unlike a linear script (A -> B -> C), the MagenticOne Orchestrator dynamically decides 
   what to do next. It saw the logs, decided to ask the Coder to verify the OS, 
   then asked for the file content, then analyzed it. You didn't write `if/else` logic 
   for this; the "Brain" figured it out.

2. SAFETY REQUIRES ISOLATION (DOCKER)
   The `Coder` agent has the power to write and execute ANY Python code. 
   Running this on your host machine is dangerous (it could delete files). 
   By forcing it into a Docker container, we ensure that `rm -rf /` only destroys 
   a disposable container, not your laptop.

3. EXPLICIT LIFECYCLE MANAGEMENT
   High-level helpers like `MagenticOne()` are great for demos, but for real production 
   apps, you often need Manual Assembly (like we did here). This gives you control over:
   - When the Docker container starts/stops.
   - Which specific agents are in the team.
   - Where the logs and files are saved.
"""
