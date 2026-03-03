# Importing the required libraries
import pandas as pd
import pandasai as pai
from pandasai_litellm.litellm import LiteLLM
from pandasai import Agent
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get values from .env
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Create connection to Postgres
engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require")

# Initialize LiteLLM with an OpenAI model
llm = LiteLLM(model="gpt-4o-mini")


# Load datasets directly from PostgreSQL into pandas DataFrames (cached at module level)
import time
print("Loading datasets from PostgreSQL...")
start_time = time.time()

print("  Loading users table...")
users_df = pd.read_sql_table("users", engine)
print(f"  ✓ Users: {len(users_df)} rows ({time.time() - start_time:.2f}s)")

print("  Loading subscriptions table...")
subscriptions_df = pd.read_sql_table("subscriptions", engine)
print(f"  ✓ Subscriptions: {len(subscriptions_df)} rows ({time.time() - start_time:.2f}s)")

print("  Loading sessions table...")
sessions_df = pd.read_sql_table("sessions", engine)
print(f"  ✓ Sessions: {len(sessions_df)} rows ({time.time() - start_time:.2f}s)")

print("  Loading payments table...")
payments_df = pd.read_sql_table("payments", engine)
print(f"  ✓ Payments: {len(payments_df)} rows ({time.time() - start_time:.2f}s)")

total_time = time.time() - start_time
print(f"All datasets loaded in {total_time:.2f}s")
print(f"Total rows: {len(users_df) + len(subscriptions_df) + len(sessions_df) + len(payments_df)}")

print("Initializing PandasAI Agent...")
# Initialize Agent once at module level (reused for all queries)
agent = Agent([users_df, subscriptions_df, sessions_df, payments_df], config={"llm": llm, "verbose": False})
print("Agent ready!")


def query_pandasai(question: str):
    """
    Query the datasets using PandasAI.
    
    Accepts a natural language question and returns the result.
    Handles multiple datasets: users, subscriptions, sessions, payments.
    
    Parameters
    ----------
    question : str
        Natural language question about the data
        
    Returns
    -------
    Result from PandasAI (typically a DataFrame or string summary)
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    # Use the globally cached agent
    answer = agent.chat(question)
    
    return answer
