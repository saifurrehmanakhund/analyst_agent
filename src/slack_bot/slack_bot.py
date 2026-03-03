"""Slack bot for querying data using natural language."""

import os
import logging
import re
from pathlib import Path
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


def _to_existing_file_path(candidate: str) -> str | None:
    """Return normalized existing file path, or None if not found."""
    if not candidate:
        return None

    cleaned = candidate.strip().strip("`\"'")
    cleaned = cleaned.replace("\\", "/")
    if not cleaned:
        return None

    path_obj = Path(cleaned)
    if path_obj.is_file():
        return str(path_obj)

    workspace_path = Path.cwd() / path_obj
    if workspace_path.is_file():
        return str(workspace_path)

    return None


def _extract_chart_file_path(result: object) -> str | None:
    """Extract an existing chart image path from a PandasAI result."""
    image_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp")

    if isinstance(result, str):
        direct = _to_existing_file_path(result)
        if direct and direct.lower().endswith(image_exts):
            return direct

        matches = re.findall(r"(?:[\w./\\-]+)\.(?:png|jpg|jpeg|gif|webp)", result, flags=re.IGNORECASE)
        for match in matches:
            found = _to_existing_file_path(match)
            if found:
                return found

    if isinstance(result, dict):
        for key in ("path", "file", "filepath", "value", "result"):
            if key in result:
                found = _extract_chart_file_path(result[key])
                if found:
                    return found

    if isinstance(result, (list, tuple)):
        for item in result:
            found = _extract_chart_file_path(item)
            if found:
                return found

    return None

# Import AI and formatting modules
try:
    from engine.pandas_ai import query_pandasai
    from engine.client import QueryClient
    from output.formatter import format_result_for_slack, format_error_message
    from guardrails import check_pii_in_question, check_malicious_input
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
        
        # Step 2: Check for malicious code injection attempts
        is_malicious, malicious_error = check_malicious_input(text)
        if is_malicious:
            logger.warning(f"Malicious input blocked from {user}")
            say(malicious_error)
            return
        
        # Step 3: Execute the query
        query_result = query_client.query(text)
        
        # Step 4: Format and send response
        if query_result['success']:
            result = query_result['result']
            logger.info(f"Query result type: {type(result).__name__}")

            chart_file = _extract_chart_file_path(result)
            if chart_file:
                logger.info("Query returned chart file, uploading image to Slack")
                try:
                    client.files_upload_v2(
                        channel=channel,
                        file=chart_file,
                        initial_comment="📈 Here is your chart."
                    )
                except Exception as upload_error:
                    logger.error(f"Chart upload failed: {upload_error}", exc_info=True)
                    say("❌ I generated a chart but couldn't upload it. Please try again.")
                return

            formatted_message = format_result_for_slack(result)
            logger.info("Query successful, sending formatted result")
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
