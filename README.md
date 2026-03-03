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
