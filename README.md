# NanoCSAssistant

An AI agent that delivers daily job listings, tech news, LeetCode problems, and research papers to your Discord. Built on nanobot, no frameworks, fully hackable.

---

## What It Does

| Digest | Schedule | Source |
|---|---|---|
| Entry-level job listings | Daily | Adzuna API (via MCP) |
| Top CS/AI/ML news | Daily | Hacker News |
| LeetCode problem of the day | Daily | LeetCode API |
| New CS/ML papers | Weekly Monday | arXiv |

Everything posts to a Discord channel automatically. You can also talk to the agent directly via CLI.

```
> search jobs entry-level python US
> explain this leetcode problem to me
> what papers dropped this week on transformers
```

---

## Quickstart

**Prerequisites:** Python 3.12+, a Discord webhook URL, an [Adzuna API key](https://developer.adzuna.com) (free)

```bash
git clone https://github.com/your-username/cs-student-assistant
cd cs-student-assistant

python -m venv venv && source venv/bin/activate
pip install -e .
```

Copy and fill in the config:

```bash
cp config.example.json config.json
```

```json
{
  "mcpServers": {
    "adzuna-mcp": {
      "command": "uvx",
      "args": ["adzuna-mcp"],
      "env": {
        "ADZUNA_APP_ID": "your_app_id",
        "ADZUNA_APP_KEY": "your_app_key"
      }
    }
  },
  "channels": {
    "discord": {
      "webhook_url": "https://discord.com/api/webhooks/..."
    }
  },
  "provider": "xai/grok-beta",
  "api_key": "your_grok_api_key"
}
```

Run:

```bash
nanobot agent
```

---

## Set Up Daily Digests

Once the agent is running, use `cron` to schedule tasks:

```
> cron add cron_expr="0 9 * * * America/New_York" message="Run daily digest: jobs, tech news, leetcode"
> cron add cron_expr="0 9 * * 1 America/New_York" message="Run weekly arxiv digest for ML papers"
```

Verify:

```
> cron list
```

To change the schedule or topics, just tell the agent. It updates its own cron entries.

---

## Customize

**Change job search keywords or location**

Edit `nanobot/skills/search_jobs/SKILL.md` and update the default keywords and region. The agent reads this file at runtime.

**Change news topics**

Edit `nanobot/skills/fetch_tech_news/SKILL.md`. Add or remove keywords like `"systems"`, `"security"`, `"algorithms"`.

**Add a new digest**

Create a new folder under `nanobot/skills/` with a `SKILL.md` describing what it does. The agent will pick it up automatically on next run.

---

## How It Works

This project is built on [nanobot](https://github.com/nanobot-ai/nanobot), a minimal Python agent runtime. The goal was to understand each layer of an AI agent without a framework hiding the internals.

```
User / Cron trigger
      |
      v
Agent loop (nanobot/agent/loop.py)
      |
      +--> Reads MEMORY.md (past context, user prefs)
      +--> Reads SKILL.md files (available behaviors)
      +--> Picks a tool (exec, mcp_call, web_search, message)
      |
      v
Tool runs (search_jobs.py, fetch_tech_news.py, etc.)
      |
      v
Output posted to Discord + HISTORY.md updated
```

## Project Status

| Phase | Status |
|---|---|
| Core agent (stripped nanobot, Grok via LiteLLM) | Done |
| MCP integration (Adzuna job search) | Done |
| Cron + daily Discord digests | In progress |
| LeetCode daily | Planned |
| Arxiv weekly digests | Planned |
| Write a custom MCP server from scratch | Planned |
| RAG for news archive + lecture notes | Planned |

---

## Running Tests

```bash
pytest tests/
```

---

## License

MIT
