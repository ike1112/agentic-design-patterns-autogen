# Financial Analysis Agent 🤖📈

This project executes a stock market analysis task using **AutoGen** agents and **Google Gemini 2.0 Flash**.

## How It Works

1.  **Agents**: Two agents collaborate:
    *   **`code_writer_agent`**: Uses Gemini to write Python code for the task.
    *   **`code_executor_agent`**: Executes the code locally in the `coding/` directory.

2.  **User Defined Functions (UDFs)**:
    *   Instead of writing raw code for every step, the agents are provided with pre-defined functions:
        *   `get_stock_prices(stock_symbols, start_date, end_date)`: Downloads stock data using `yfinance`.
        *   `plot_stock_prices(stock_prices, filename)`: Plots the data using `matplotlib`.

3.  **Process**:
    *   The `code_writer_agent` creates a script that imports and calls these UDFs.
    *   The `code_executor_agent` runs the script.
    *   Because the execution happens in a separate process, the UDFs self-contain their necessary imports (e.g., `import yfinance`), ensuring they run correctly in isolation.

## Setup & Running

1.  **Install Requirements**:
    Ensure you are in the project root:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Analysis**:
    Navigate to the `Coding agent` folder and run:
    ```bash
    python financial_analysis.py
    ```

3.  **Output**:
    *   The agents will discuss and generate code.
    *   The resulting plot will be saved as `coding/stock_prices_YTD_plot.png`.

## Important Note on Imports
Inside `financial_analysis.py`, you will notice imports like `import yfinance` inside the function definitions. This is intentional! The AutoGen `LocalCommandLineCodeExecutor` serializes these functions and runs them in a separate Python process. Global imports from the main script are not shared with this subprocess, so dependencies must be imported locally within the functions.
