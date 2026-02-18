# fetch_tech_news

Fetch and send top Hacker News CS stories to Discord daily.

## Usage

**Manual (agent):**
```
exec(command="cd /home/lucasz/repos/cs-student-assistant-bot/nanobot/skills/fetch_tech_news && python3 fetch_tech_news.py 'YOUR_DISCORD_WEBHOOK'")
```

**Daily automation (8AM PST):**
```
cron(action="add", cron_expr="0 8 * * *", tz="America/Los_Angeles", message="Daily HN CS news to Discord", job_id="hn-cs-daily")
```
(Pre-set DISCORD_WEBHOOK env or pass as arg.)

## Features
- Fetches top 30 HN stories
- Filters CS-relevant (AI/ML, langs, algos, etc.)
- Formats Discord-friendly digest (top 10)
- Webhook-based sending (no bot needed)

## Setup
1. Get Discord webhook: Server Settings → Integrations → Webhooks → New
2. Run: `python3 fetch_tech_news.py 'https://discord.com/api/webhooks/...'` 
3. Schedule with cron skill.

**Keywords**: HN, Hacker News, tech news, CS digest
