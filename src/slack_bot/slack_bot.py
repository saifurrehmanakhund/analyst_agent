"""Slack bot for querying data using natural language."""

import os
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.error import BoltError

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load from environment variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

# Validate environment variables
missing_vars = []
if not SLACK_BOT_TOKEN:
    missing_vars.append("SLACK_BOT_TOKEN")
if not SLACK_SIGNING_SECRET:
    missing_vars.append("SLACK_SIGNING_SECRET")
if not SLACK_APP_TOKEN:
    missing_vars.append("SLACK_APP_TOKEN")

if missing_vars:
    logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize Slack app
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

# Import AI and formatting modules
try:
    from engine.pandas_ai import query_pandasai
    from engine.client import QueryClient
    from output.formatter import format_result_for_slack, format_error_message
    from guardrails import check_pii_in_question
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise

# Initialize the query client
query_client = QueryClient(query_pandasai, timeout_seconds=30)


# Listen to all messages in channels where bot is mentioned or in DMs
@app.event("message")
def handle_message(event, say, client):
    """
    Handle incoming messages and route to the AI query engine.
    
    Checks for PII requests, executes query, and formats results.
    """
    # Ignore messages from the bot itself
    if event.get("subtype") == "bot_message":
        return
    
    user = event.get("user")
    text = event.get("text", "").strip()
    channel = event.get("channel")
    
    # Skip if no user or empty message
    if not user or not text:
        return
    
    try:
        logger.info(f"Received message from {user}: {text[:100]}")
        
        # Show typing indicator
        try:
            client.conversations_info(channel=channel)
        except Exception:
            pass  # Typing indicator is optional
        
        # Step 1: Check for PII exposure attempts
        has_pii_request, pii_error = check_pii_in_question(text)
        if has_pii_request:
            logger.warning(f"PII request blocked from {user}")
            say(pii_error)
            return
        
        # Step 2: Execute the query
        query_result = query_client.query(text)
        
        # Step 3: Format and send response
        if query_result['success']:
            formatted_message = format_result_for_slack(query_result['result'])
            logger.info(f"Query successful, sending formatted result")
            say(formatted_message)
        else:
            error_message = format_error_message(query_result['error'])
            logger.warning(f"Query failed: {query_result['error']}")
            say(error_message)
    
    except Exception as e:
        error_msg = format_error_message(str(e))
        logger.error(f"Unexpected error handling message: {e}", exc_info=True)
        say(error_msg)


# Optional: Handle mentions of the bot name (for more explicit queries)
@app.message("ask")
def handle_ask_command(ack, body, say):
    """Handle explicit 'ask' command for clarity."""
    ack()
    # This will be handled by the general message handler


@app.error
def custom_error_handler(error, body):
    """Log errors from Slack events."""
    logger.error(f"Slack error: {error}")
    logger.debug(f"Request body: {body}")
