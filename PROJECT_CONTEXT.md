# PROJECT CONTEXT: Talk-to-Your-Data Slack Bot

## Project Overview

**What it is:** An AI-powered Slack bot that lets users ask natural language questions about their data and receive instant, formatted answers.

**Problem it solves:** Modern teams struggle with data accessibility. Non-technical users lack direct query tools (SQL), while analysts spend time answering repetitive questions. This bot democratizes data access—anyone can ask questions conversationally.

**Core value:** Users ask questions in plain English (e.g., "Show me all active users with annual subscriptions and their total payments") and get immediate, human-readable answers with formatted tables.

**Users:** Internal team members, business analysts, managers, product teams—anyone who needs to explore the company's PostgreSQL database without writing SQL.

---

## System Scope

### In Scope
- ✅ Slack interface for asking questions (real-time message handling)
- ✅ Natural language query processing via PandasAI
- ✅ Multi-table querying (users, subscriptions, sessions, payments)
- ✅ Automatic table joins when needed (e.g., users + subscriptions)
- ✅ Result formatting for Slack (text summaries + markdown tables)
- ✅ PII protection (blocking queries that expose sensitive data)
- ✅ Error handling with user-friendly messaging
- ✅ Logging for debugging and monitoring

### Out of Scope
- ❌ Writing to the database (read-only queries only)
- ❌ Real-time dashboards or visualizations (text-based results only)
- ❌ Complex data science workflows (simple aggregations and joins only)
- ❌ Custom dataset creation by users
- ❌ Multi-tenancy or per-user data access controls (assumes shared database)

---

## Architecture Summary

The system uses a **modular pipeline architecture** where each component handles a specific responsibility:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SLACK MESSAGE EVENT                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │   INPUT VALIDATION          │
        │  (guardrails.py)            │
        │  - PII pattern detection    │
        │  - Block sensitive queries  │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │   QUERY EXECUTION                   │
        │  (engine/client.py +                │
        │   engine/pandas_ai.py)              │
        │  - LLM-powered SQL generation       │
        │  - Multi-table join handling        │
        │  - Timeout/error management         │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │   OUTPUT FORMATTING         │
        │  (output/formatter.py)      │
        │  - Text summarization       │
        │  - Markdown table rendering │
        │  - Message truncation       │
        └────────────┬────────────────┘
                     │
                     ▼
    ┌───────────────────────────────────────┐
    │  SLACK BOT SENDS RESPONSE             │
    │  to user via Slack API                │
    └───────────────────────────────────────┘
```

### Core Subsystems

1. **Slack Bot** (`src/slack_bot/slack_bot.py`)
   - Receives messages via Slack Bolt framework
   - Orchestrates the query pipeline
   - Routes errors and results to users

2. **Query Engine** (`src/engine/`)
   - `pandas_ai.py`: Initializes datasets, connects to PostgreSQL, defines PandasAI configuration
   - `client.py`: QueryClient wrapper with error handling, timeout management, result validation

3. **Security Layer** (`src/guardrails.py`)
   - PII pattern detection for column names
   - PII pattern detection for user questions
   - Blocks queries attempting to expose sensitive data

4. **Output Formatter** (`src/output/formatter.py`)
   - Converts results (DataFrames, lists, dicts, strings) into Slack-friendly messages
   - Handles large results (truncation)
   - Maps errors to user-friendly messages

5. **Entry Point** (`src/main.py`)
   - Starts the bot in Socket Mode for real-time event processing

---

## Data Flow & Key Inputs/Outputs

### Inputs
- **Slack Message**: User's natural language question (e.g., "How many active subscriptions do we have?")
- **PostgreSQL Database**: Tables (users, subscriptions, sessions, payments) with structured data

### Processing Steps
1. User sends message in Slack
2. Bot receives message, extracts question text
3. **Guardrails check**: Detect if question asks for PII → if yes, block with explanation
4. **Query execution**: Pass question + datasets to PandasAI
5. **LLM reasoning**: GPT-4 (via LiteLLM) converts natural language to pandas operations
6. **Query result**: DataFrame or aggregated value
7. **Format for Slack**: Convert result to markdown tables + summary text
8. **Send response**: Bot posts formatted message to Slack channel

### Outputs
- **Success case**: Formatted message with results
  - Example: "📊 Query Results: 150 rows × 3 columns\n\n| user_id | plan | status |\n|---|---|---|\n| 1 | annual | active |"
- **Error case**: User-friendly error message
  - Examples: "❌ Cannot process queries involving personal information" or "❌ Query timed out. Try a simpler question."

---

## Design Rationale

### 1. **Why Pipeline Architecture?**
- **Modularity**: Each component (guardrails, query, formatting) can be tested and maintained independently
- **Reusability**: Components can be used in other contexts (API endpoints, batch jobs)
- **Maintainability**: Clear separation of concerns makes debugging easier

### 2. **Why PandasAI + LLM?**
- **Natural language support**: Users don't need SQL knowledge
- **Automatic join detection**: LLM understands relationships between tables (e.g., user_id links users ↔ subscriptions)
- **Flexibility**: New questions don't require code changes; the LLM adapts

### 3. **Why PII Blocking (Not Logging/Warning)?**
- **Conservative security approach**: Sensitive data exposure is irreversible; better to block than warn
- **User requirements**: Team preferred blocking over allowing-with-warning
- **Compliance**: Reduces risk of accidental GDPR/data protection violations

### 4. **Why Slack (Not API Endpoint)?**
- **Context**: Users already in Slack; minimizes friction
- **Notifications**: Natural integration with team workflows
- **Accessibility**: No CLI or API keys needed; anyone with Slack can use it

### 5. **Why Truncate Messages (Not Paginate)?**
- **Slack limitations**: API doesn't natively support message pagination
- **Readability**: 20 rows/items typically sufficient for exploratory analysis
- **Users can refine**: If they need all 500 rows, they can ask a more specific question

### 6. **Error Handling Strategy**
- **Hide technical details from users**: Don't expose database/LLM errors that confuse non-technical users
- **Log everything internally**: Detailed logs for debugging in development/staging
- **Map common errors to friendly messages**: "Connection refused" → "Unable to connect to database"

### 7. **Timeout & Resource Management**
- **30-second timeout**: Prevents long-running queries from freezing the bot
- **Result truncation**: Prevents memory overload from huge result sets
- **Fail fast**: Immediately reject empty/invalid questions without querying

---

## Key Constraints & Dependencies

### Environment Dependencies
- **Python 3.10+**: Required for type hints and modern syntax
- **PostgreSQL database**: With users, subscriptions, sessions, payments tables
- **Slack workspace**: With bot installed and OAuth token configured
- **OpenAI API**: For LLM (gpt-4-mini via LiteLLM)

### Configuration (Environment Variables)
```
SLACK_BOT_TOKEN         # Slack bot oauth token
SLACK_SIGNING_SECRET    # Slack signing secret for verification
SLACK_APP_TOKEN         # Slack app token for Socket Mode
DB_USER, DB_PASS        # PostgreSQL credentials
DB_HOST, DB_PORT        # PostgreSQL connection
DB_NAME                 # Database name
```

### Assumptions
- Database credentials are safely stored in environment (never in code)
- All users in Slack channel have equal data access (no row-level security)
- Database connection is stable; network timeouts handled gracefully
- LLM responses are reasonable (no custom prompt injection handling)

---

## Testing Strategy

**Unit Tests** (41 tests, all passing):
- **test_guardrails.py**: PII detection for columns and questions
- **test_formatter.py**: Result formatting, truncation, error messages
- **test_client.py**: Query client behavior, error handling, empty questions

**Integration Testing** (Manual, in development):
- Test with real Slack workspace and PostgreSQL database
- Verify cross-table joins (e.g., users + subscriptions + payments)
- Validate timeout behavior with slow queries

---

## Future Enhancement Paths

1. **Row-level security**: Add user/role-based access controls to limit which rows are visible
2. **Caching**: Cache frequently asked questions for instant responses
3. **Scheduled queries**: Allow users to schedule recurring reports
4. **Data export**: Add buttons to export results as CSV/JSON
5. **Query preview**: Show the generated SQL before executing for transparency
6. **Multi-language**: Support questions in different languages via LLM translation
