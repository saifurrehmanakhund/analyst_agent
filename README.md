# Talk-to-Your-Data Slack Bot

An AI-powered Slack bot that lets you query your PostgreSQL database using natural language. Ask questions in plain English and get instant, formatted answers with tables and summaries.

## Features

- 🤖 **Natural Language Queries**: Ask questions like "How many active users with annual subscriptions do we have?"
- 🔒 **Built-in Security**: PII protection, code injection prevention, and input validation
- 📊 **Smart Formatting**: Results displayed as text summaries with markdown tables
- 🚀 **Multi-Table Support**: Automatically joins data from users, subscriptions, sessions, and payments tables
- ⚡ **Real-time**: Socket Mode for instant message processing in Slack

## Prerequisites

- Python 3.10 or 3.11 (Python 3.13 may have compatibility issues with some dependencies)
- Poetry (dependency manager)
- PostgreSQL database with required tables
- Slack workspace with bot permissions
- OpenAI API key

## Installation

1. **Clone the repository**
	```bash
	git clone <your-repo-url>
	cd analyst_agent
	```

2. **Install dependencies with Poetry**
	```bash
	poetry install
	```

3. **Set up environment variables**
	```bash
	cp .env.example .env
	```
   
	Edit `.env` and fill in your credentials:
	- **Slack credentials**: Get from https://api.slack.com/apps
	- **Database credentials**: Your PostgreSQL connection details
	- **OpenAI API key**: Get from https://platform.openai.com/api-keys

## Slack App Setup

1. **Create a Slack App** at https://api.slack.com/apps
	- Click "Create New App" → "From scratch"
	- Give it a name and select your workspace

2. **Enable Socket Mode**
	- Go to "Socket Mode" in the sidebar
	- Enable Socket Mode
	- Generate an app-level token with `connections:write` scope
	- Copy the token (starts with `xapp-`) to `SLACK_APP_TOKEN` in `.env`

3. **Configure Bot Token Scopes**
	- Go to "OAuth & Permissions"
	- Add these Bot Token Scopes:
	  - `chat:write`
	  - `files:write`
	  - `channels:history`
	  - `groups:history`
	  - `im:history`
	  - `mpim:history`
	- Install the app to your workspace
	- Copy the "Bot User OAuth Token" (starts with `xoxb-`) to `SLACK_BOT_TOKEN` in `.env`

4. **Get the Signing Secret**
	- Go to "Basic Information"
	- Copy the "Signing Secret" to `SLACK_SIGNING_SECRET` in `.env`

5. **Subscribe to Events**
	- Go to "Event Subscriptions"
	- Enable Events
	- Subscribe to these bot events:
	  - `message.channels`
	  - `message.groups`
	  - `message.im`
	  - `message.mpim`

## Database Schema

Your PostgreSQL database should have these tables:

- **users**: `id`, `name`, `email`
- **subscriptions**: `subscription_id`, `user_id`, `plan`, `start_date`, `end_date`, `status`
- **sessions**: `session_id`, `user_id`, `session_date`, `duration_minutes`, `activity_type`
- **payments**: `payment_id`, `subscription_id`, `payment_date`, `amount_usd`, `method`

## Usage

1. **Start the bot**
	```bash
	poetry run python src/main.py
	```

2. **Wait for datasets to load**
	```
	Loading datasets from PostgreSQL...
	  ✓ Users: 150 rows (1.2s)
	  ✓ Subscriptions: 300 rows (1.5s)
	  ✓ Sessions: 5000 rows (3.2s)
	  ✓ Payments: 800 rows (2.1s)
	All datasets loaded in 8.0s
	Initializing PandasAI Agent...
	Agent ready!
	⚡️ Bolt app is running!
	```

3. **Ask questions in Slack**
	- Message the bot directly or mention it in a channel
	- Examples:
	  - "How many active users do we have?"
	  - "Show me all annual subscriptions from 2025"
	  - "What's the total revenue from monthly subscriptions?"
	  - "Which users have the most sessions?"

## Example Interactions

**Question:** "How many active users with annual subscriptions?"

**Response:**
```
📊 Query Results: 45 rows × 3 columns

| name          | plan   | status |
|---------------|--------|--------|
| John Doe      | annual | active |
| Jane Smith    | annual | active |
...
```

## Security Features

The bot includes multiple layers of protection:

- ✅ **PII Protection**: Blocks queries requesting emails, phone numbers, SSNs, etc.
- ✅ **Code Injection Prevention**: Blocks malicious patterns (exec, eval, os.system, etc.)
- ✅ **SQL Injection Prevention**: No direct SQL execution; uses parameterized queries
- ✅ **Input Validation**: 1000-character limit, empty question rejection
- ✅ **Read-Only Database**: No write/update/delete operations

**Blocked queries will receive user-friendly error messages:**
- "❌ Cannot process queries involving personal information"
- "❌ Your question contains potentially unsafe patterns"

## Testing

Run the test suite:
```bash
poetry run pytest tests/ -v
```

All 56 tests should pass:
- 30 security/guardrails tests
- 18 output formatting tests
- 9 query client tests

## Troubleshooting

**Bot not responding:**
- Check that Socket Mode is enabled
- Verify all environment variables are set
- Check bot has the required OAuth scopes
- Ensure bot is added to the channel

**Database connection errors:**
- Verify PostgreSQL credentials in `.env`
- Check database server is reachable
- Ensure SSL mode matches your database config (currently set to `sslmode=require`)

**Slow queries:**
- First query after startup takes 10-20s (LLM processing)
- Subsequent queries should be faster
- Check your OpenAI API rate limits

**Module import errors:**
- Make sure you're using `poetry run python src/main.py`
- Verify all dependencies installed: `poetry install`

## Architecture

```
User Message → Slack Bot → Guardrails Check → Query Engine → PandasAI/LLM → Format Results → Response
```

See [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) for detailed architecture documentation.

## Project Structure

```
analyst_agent/
├── src/
│   ├── main.py              # Entry point
│   ├── slack_bot/
│   │   └── slack_bot.py     # Slack event handlers
│   ├── engine/
│   │   ├── pandas_ai.py     # PandasAI query engine
│   │   └── client.py        # Query wrapper with error handling
│   ├── output/
│   │   └── formatter.py     # Result formatting for Slack
│   └── guardrails.py        # Security checks (PII, malicious input)
├── tests/                   # Test suite (56 tests)
├── .env.example            # Environment variable template
├── pyproject.toml          # Poetry dependencies
└── README.md               # This file
```

## Contributing

See [AGENTS.md](AGENTS.md) for development guidelines:
- Always propose a plan before making changes
- Run `pytest -q` after code changes
- Use PEP8 style with NumPy docstrings
- Never commit secrets or datasets

## License

[Add your license here]

## Support

For issues or questions, please [open an issue](link-to-issues) or contact the development team.
# Talk-to-Your-Data Slack Bot

An AI-powered Slack bot that lets you ask natural language questions about your data.

**Example:** "How many active annual subscriptions do we have?" → Bot queries the database and returns a formatted result.

---

## Quick Start

### 1. Prerequisites
- Python 3.10+
- PostgreSQL database with data tables
- Slack workspace with admin access

### 2. Setup

**Install dependencies:**
```bash
poetry install
```

**Create `.env` file:**
```env
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_TOKEN=xapp-your-app-token

# PostgreSQL Configuration
DB_USER=postgres
DB_PASS=your-password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
```

### 3. Run the Bot

```bash
python src/main.py
```

The bot will start listening for messages on your Slack workspace.

---

## Usage

In any Slack channel where the bot is installed, simply ask a question:

```
@databot How many active users do we have?
```

The bot will:
1. Check if the question is safe (no PII exposure)
2. Execute the query against your database
3. Return formatted results with a summary and table

### Examples

**✅ Valid questions:**
- "Show me all active users with annual subscriptions and their total payments"
- "How many sessions happened in the last 7 days?"
- "What's the average subscription duration?"

**❌ Blocked questions:**
- "Show me all user emails" (PII protection)
- "Get all phone numbers" (PII protection)
- "Export all user data" (PII protection)

---

## Architecture

See [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) for detailed system design, architecture diagram, and design rationale.

---

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

**Coverage:**
- 41 tests covering guardrails, formatting, and query client
- All tests pass ✅

---

## Files & Modules

```
src/
├── slack_bot/
│   └── slack_bot.py           # Slack event handling & orchestration
├── engine/
│   ├── pandas_ai.py           # PandasAI configuration & datasets
│   └── client.py              # Query client with error handling
├── output/
│   └── formatter.py           # Result formatting for Slack
├── guardrails.py              # PII detection & security
└── main.py                    # Bot entry point

tests/
├── test_guardrails.py         # PII detection tests
├── test_formatter.py          # Output formatting tests
└── test_client.py             # Query client tests
```

---

## Development Notes

- **Logging**: All modules log to console with INFO+ level. Check logs for debugging.
- **Timeout**: Queries timeout after 30 seconds. Use more specific questions for faster results.
- **Message limit**: Results truncated to 3000 characters (Slack limit is 4000).
- **PII Protection**: Conservative approach—queries asking for sensitive data are blocked, not warned.

---

## Security Considerations

- ✅ Environment variables for all secrets (never hardcoded)
- ✅ PII protection blocks email, phone, SSN, credit card queries
- ✅ Database read-only (no write operations)
- ✅ Input validation (empty questions rejected)
- ⚠️ Assumes all Slack users have equal database access
- ⚠️ LLM responses not validated for prompt injection (low-risk context)

---

## Troubleshooting

**Bot not responding:**
1. Check Slack tokens are valid
2. Verify PostgreSQL connection
3. Check logs for errors

**Query timeout:**
- Ask a more specific question
- Increase `timeout_seconds` in `engine/client.py`

**"Cannot process PII queries":**
- The bot blocks queries asking for emails, phone numbers, SSNs, etc.
- This is intentional for data protection
- Rephrase your question without mentioning sensitive fields

**Database connection error:**
- Verify PostgreSQL is running
- Check credentials in `.env`
- Ensure `sslmode=require` is appropriate for your setup

---

## Next Steps

See [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) for future enhancement paths (row-level security, caching, data export, etc.).
