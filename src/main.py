"""
Entry point for the Talk-to-your-Data Slack bot.

Starts the bot in Socket Mode for real-time message processing.
"""

import sys
import logging
from pathlib import Path

# Add src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from slack_bot.slack_bot import app, SLACK_APP_TOKEN
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        logger.info("Starting Talk-to-your-Data Slack bot...")
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()
        logger.info("Bot started successfully")
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        raise