
import os
import sys
import datetime
import yfinance
import matplotlib.pyplot as plt
from autogen import ConversableAgent, AssistantAgent
from autogen.coding import LocalCommandLineCodeExecutor

# Add parent directory to sys.path to import utils
# Assuming this script is in "Coding agent/" and utils.py is in the root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import get_gemini_api_key

# --------------------------------------------------------------------------------
# Environment Setup (Fix for Subprocesses)
# --------------------------------------------------------------------------------
# Ensure the executor uses the same python environment as this script
# by prepending the current python's directory to PATH.
venv_scripts = os.path.dirname(sys.executable)
os.environ["PATH"] = venv_scripts + os.pathsep + os.environ["PATH"]

# --------------------------------------------------------------------------------
# Setup LLM Configuration
# --------------------------------------------------------------------------------
GOOGLE_API_KEY = get_gemini_api_key()

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
# User Defined Functions
# --------------------------------------------------------------------------------
def get_stock_prices(stock_symbols, start_date, end_date):
    """Get the stock prices for the given stock symbols between
    the start and end dates.

    Args:
        stock_symbols (str or list): The stock symbols to get the
        prices for.
        start_date (str): The start date in the format 
        'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.
    
    Returns:
        pandas.DataFrame: The stock prices for the given stock
        symbols indexed by date, with one column per stock 
        symbol.
    """
    # Ensure stock_symbols is a list if it's a string
    if isinstance(stock_symbols, str):
        stock_symbols = [stock_symbols]

    # IMPORT IS REQUIRED HERE: 
    # AutoGen execution happens in a separate script/process 
    # where global imports from the main file are NOT available.
    import yfinance

    stock_data = yfinance.download(
        stock_symbols, start=start_date, end=end_date
    )
    
    # If multiple stocks, yfinance returns a MultiIndex column. We want just the Close prices.
    # If single stock, it returns just columns.
    if "Close" in stock_data:
        return stock_data["Close"]
    else:
        # Fallback or different version of yfinance might behave differently
        return stock_data

def plot_stock_prices(stock_prices, filename):
    """Plot the stock prices for the given stock symbols.

    Args:
        stock_prices (pandas.DataFrame): The stock prices for the 
        given stock symbols.
        filename (str): The filename to save the plot to.
    """

    # IMPORT IS REQUIRED HERE: 
    # AutoGen execution happens in a separate script/process.
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 5))
    
    # Check structure of stock_prices just in case
    # If it's a Series (one stock), convert to DF
    if hasattr(stock_prices, 'columns'):
        for column in stock_prices.columns:
            plt.plot(
                stock_prices.index, stock_prices[column], label=column
            )
    else:
        # It's likely a Series
        plt.plot(stock_prices.index, stock_prices, label=stock_prices.name)

    plt.title("Stock Prices")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.legend()
    plt.savefig(filename)
    print(f"Plot saved to {filename}")

# --------------------------------------------------------------------------------
# Agents and Executor Setup
# --------------------------------------------------------------------------------

# Create the coding directory if it doesn't exist
work_dir = "coding"
if not os.path.exists(work_dir):
    os.makedirs(work_dir)

# Create the executor with User Defined Functions
executor = LocalCommandLineCodeExecutor(
    timeout=60,
    work_dir=work_dir,
    functions=[get_stock_prices, plot_stock_prices],
)

# Initialize the Code Writer Agent
# We need to manually add the function definitions to the system message 
# because we are registering them with the executor, but the writer needs to know about them.
code_writer_agent = AssistantAgent(
    name="code_writer_agent",
    llm_config=llm_config,
    code_execution_config=False,
    human_input_mode="NEVER",
)

code_writer_agent_system_message = code_writer_agent.system_message + executor.format_functions_for_prompt()

code_writer_agent = ConversableAgent(
    name="code_writer_agent",
    system_message=code_writer_agent_system_message,
    llm_config=llm_config,
    code_execution_config=False,
    human_input_mode="NEVER",
)

# Initialize the Code Executor Agent
code_executor_agent = ConversableAgent(
    name="code_executor_agent",
    llm_config=False,
    code_execution_config={"executor": executor},
    human_input_mode="ALWAYS",
    default_auto_reply="Please continue. If everything is done, reply 'TERMINATE'.",
)

# --------------------------------------------------------------------------------
# Main Task Execution
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    today = datetime.datetime.now().date()
    
    # Ensure cleaner chat history by resetting/initiating fresh if needed, 
    # though in script run it's always fresh.
    
    message = (
        f"Today is {today}. "
        "Download the stock prices YTD for NVDA and TSLA and create "
        "a plot. Make sure the code is in markdown code block and "
        "save the figure to a file stock_prices_YTD_plot.png."
    )
    
    # print(f"Starting chat with message:\n{message}\n")
    
    chat_result = code_executor_agent.initiate_chat(
        code_writer_agent,
        message=message,
    )
    
    # print("Chat finished.")
