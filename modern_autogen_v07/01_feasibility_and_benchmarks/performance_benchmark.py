import time
import asyncio
import json
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
import os
from dotenv import load_dotenv

load_dotenv()

async def benchmark_quality():
    # Configuration
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("Error: GEMINI_API_KEY not found.")
        return

    # 1. Setup Client
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash-exp",
        api_key=gemini_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        model_info={"vision": True, "function_calling": True, "json_output": True, "family": "gemini-2.0-flash-exp"}
    )

    task = "Brainstorm 3 unique marketing slogans for a high-caffeine coffee brand designed specifically for e-sports gamers."

    print(f"\n--- TASK: {task} ---")

    # ---------------------------------------------------------
    # Approach 1: Single Agent (The Baseline)
    # ---------------------------------------------------------
    print("\n1. Running Single Agent...")
    start_time = time.time()
    
    single_agent = AssistantAgent("marketer", model_client)
    result_single = await single_agent.run(task=task)
    
    # Extract just the text content from the output message
    output_single = result_single.messages[-1].content
    
    time_single = time.time() - start_time
    print(f"[DONE] Single Agent: {time_single:.2f}s")

    # ---------------------------------------------------------
    # Approach 2: Multi-Agent Team (The Challenger)
    # ---------------------------------------------------------
    print("\n2. Running 3-Agent Debate (Marketer + Critic + Legal)...")
    start_time = time.time()
    
    # Team definition
    marketer = AssistantAgent("marketer", model_client)
    # Critic ensures it appeals to gamers, not generic office workers
    critic = AssistantAgent("critic", model_client, system_message="You are a Gen-Z gamer. Criticize slogans that sound like 'boomers' wrote them. Ensure they use correct gaming terminology.")
    # Legal ensures we don't promise medical benefits
    legal = AssistantAgent("legal", model_client, system_message="Ensure we do not make false health claims (e.g., 'makes you aim better'). Flag liability risks.")
    
    team = RoundRobinGroupChat([marketer, critic, legal], max_turns=6)
    result_team = await team.run(task=task)
    
    # The final output is usually the last message where they converged (or gave up)
    output_team = result_team.messages[-1].content
    
    time_team = time.time() - start_time
    print(f"[DONE] Team Debate: {time_team:.2f}s")

    # ---------------------------------------------------------
    # The Judge: Scoring Quality
    # ---------------------------------------------------------
    print("\n3. ⚖️  The Judge is evaluating both outputs...")
    
    judge_prompt = f"""
    You are an impartial Marketing Quality Judge. Compare two sets of marketing slogans.
    
    CRITERIA:
    1. Creativity: Are they unique?
    2. Relevance: Do they speak to 'gamers' authentically?
    3. Safety: Are they free of dangerous health claims?
    
    OUTPUT A:
    {output_single}
    
    OUTPUT B:
    {output_team}
    
    Return a JSON object with this exact format:
    {{
        "single_agent_score": <1-10>,
        "team_score": <1-10>,
        "winner": "Single Agent" or "Team",
        "reasoning": "Explain why one won in 1 sentence."
    }}
    """
    
    judge_agent = AssistantAgent("judge", model_client)
    # Force the judge to think and output strictly JSON
    judge_result = await judge_agent.run(task=judge_prompt)
    
    # ---------------------------------------------------------
    # Final Report
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("       🏁 BENCHMARK RESULTS 🏁       ")
    print("="*40)
    
    # Clean up JSON string if the model adds markdown formatting
    json_str = judge_result.messages[-1].content.replace("```json", "").replace("```", "").strip()
    
    try:
        scores = json.loads(json_str)
        
        print(f"⏱️  TIME:")
        print(f"   Single Agent: {time_single:.2f}s")
        print(f"   Team Debate:  {time_team:.2f}s ({(time_team/time_single):.1f}x slower)")
        
        print(f"\n🏆 QUALITY SCORE (1-10):")
        print(f"   Single Agent: {scores['single_agent_score']}/10")
        print(f"   Team Debate:  {scores['team_score']}/10")
        
        print(f"\n📢 WINNER: {scores['winner'].upper()}")
        print(f"📝 REASON: {scores['reasoning']}")
        
        # The ROI Calculation
        quality_gain = scores['team_score'] - scores['single_agent_score']
        print(f"\n💰 ROI ANALYSIS:")
        if quality_gain > 0:
            print(f"   The team was slower but increased quality by {quality_gain} points.")
            print(f"   VERDICT: Use Team for high-stakes campaigns.")
        else:
            print(f"   The team added time but NO quality improvement.")
            print(f"   VERDICT: Stick to Single Agent (Debate was useless).")
            
    except json.JSONDecodeError:
        print("Error decoding Judge's JSON response. Raw output:\n" + json_str)

if __name__ == "__main__":
    asyncio.run(benchmark_quality())