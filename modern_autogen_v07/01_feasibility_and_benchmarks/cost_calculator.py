class AutoGenCostCalculator:
    """
    Estimates costs for Google Gemini models in multi-agent systems, accounting for 
    context history re-reading at every turn.
    """
    def __init__(self):
        # Pricing per 1 Million tokens (Dec 2025)
        self.costs = {
            "gemini-1.5-flash": {
                "input": 0.0375 / 1000000,
                "output": 0.15 / 1000000,
                "context_limit": 1000000 
            },
            "gemini-1.5-pro": {
                "input": 3.50 / 1000000,
                "output": 10.50 / 1000000,
                "context_limit": 2000000
            }
        }
        
    def calculate_debate_cost(self, turns, agents, avg_tokens=500, model="gemini-1.5-flash"):
        if model not in self.costs:
            return {"error": f"Model {model} not found in cost table."}
        
        model_info = self.costs[model]

        # 1. Context Window Check
        final_context_size = turns * avg_tokens
        if final_context_size > model_info["context_limit"]:
            return {
                "model": model, 
                "error": f"Context Limit Exceeded! Estimated {final_context_size} > Limit {model_info['context_limit']}"
            }

        # 2. Calculate History Build-up (Input Tokens)
        # Sum of arithmetic series: n * (n+1) / 2
        total_input_tokens = (turns * (turns + 1) / 2) * avg_tokens * agents
        
        # 3. Calculate Generation (Output Tokens)
        total_output_tokens = turns * avg_tokens
        
        # 4. Calculate Total Cost
        cost_input = total_input_tokens * model_info["input"]
        cost_output = total_output_tokens * model_info["output"]
        total_cost = cost_input + cost_output

        return {
            "model": model,
            "cost_usd": f"${round(total_cost, 5):.5f}",
            "breakdown": {
                "input_tokens_read": int(total_input_tokens),
                "output_tokens_written": int(total_output_tokens),
                "final_context_size": int(final_context_size),
                "context_limit": model_info["context_limit"]
            },
            "verdict": "SAFE" if total_cost < 0.50 else "CAUTION"
        }

if __name__ == "__main__":
    calc = AutoGenCostCalculator()
    
    def print_report(result):
        if "error" in result:
            print(f"❌ {result['error']}")
            return

        print(f"   Model:     {result['model']}")
        print(f"   Cost:      {result['cost_usd']}")
        print(f"   Verdict:   {result['verdict']}")
        print(f"   Context:   {result['breakdown']['final_context_size']:,} / {result['breakdown']['context_limit']:,} tokens")
        print(f"   Details:   Read {result['breakdown']['input_tokens_read']:,} input tokens")

    print("\n------------------------------------------------")
    print("      GEMINI MULTI-AGENT COST ESTIMATOR")
    print("------------------------------------------------")

    print("\n1. Quick Debate (Standard)")
    print("   (20 turns, 3 agents, Gemini 1.5 Flash)")
    print_report(calc.calculate_debate_cost(turns=20, agents=3, model="gemini-1.5-flash"))
    
    print("\n2. Deep Research (Pro Model)")
    print("   (50 turns, 3 agents, Gemini 1.5 Pro)")
    print_report(calc.calculate_debate_cost(turns=50, agents=3, model="gemini-1.5-pro"))
