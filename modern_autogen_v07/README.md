# Modern AutoGen (v0.7+) & Microsoft Agent Framework

This directory acts as the workspace for the **AutoGen Expert Study Plan**. All code here uses the modern architecture (`autogen_agentchat`, `autogen_ext`) and is designed to be future-proof for the Microsoft Agent Framework.

## Directory Structure

### 📂 01_feasibility_and_benchmarks
This module focuses on the "Week 0" reality checks required before building complex multi-agent systems.

*   **`cost_calculator.py`**: A utility to estimate the running costs of multi-agent debates.
    *   *Why?* Multi-agent systems re-read conversation history at every turn, leading to quadratic token usage growth. This script visualizes that cost.
    *   *Usage:* `python modern_autogen_v07/01_feasibility_and_benchmarks/cost_calculator.py`

*   **`performance_benchmark.py`**: A race between a Single Agent and a 3-Agent Team.
    *   *Why?* To prove that multi-agent systems are significantly slower and to measure if the "Quality vs. Latency" trade-off (ROI) is worth it for a given task.
    *   *Usage:* `python modern_autogen_v07/01_feasibility_and_benchmarks/performance_benchmark.py`

*(Additional modules will be added as the project expands)*

## Getting Started

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configuration**:
    Ensure your `.env` file in the root directory contains your API keys:
    ```env
    GEMINI_API_KEY=your_key_here
    ```

## Key Differences from Classic AutoGen
- **Imports**: Uses `autogen_agentchat` instead of `autogen`.
- **Orchestration**: Uses `RoundRobinGroupChat`, `MagenticOne`, etc., instead of `GroupChatManager`.
- **Architecture**: Asynchronous-first design using `async/await`.
- **Tools**: First-class support for MCP (Model Context Protocol).
