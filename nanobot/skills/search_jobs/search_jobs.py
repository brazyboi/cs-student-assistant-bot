import subprocess
import json
import sys
import os
from datetime import datetime
import requests

DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY')

def read_webhook():
    try:
        with open(WEBHOOK_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def mcp_tool_call(query, location, results_per_page=10):
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise ValueError("Missing ADZUNA_APP_ID or ADZUNA_APP_KEY in environment")

    env = os.environ.copy()

    proc = subprocess.Popen(
        ['uvx', 'adzuna-mcp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env
    )

    # JSON-RPC tools/call (MCP stdio transport)
    call_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_jobs",
            "arguments": {
                "country": "us",
                "keywords": query,
                "location": location,
                "results_per_page": results_per_page,
                "full_time": True
            }
        }
    }
    proc.stdin.write(json.dumps(call_msg) + '\n')
    proc.stdin.flush()

    # Parse SSE-like response lines
    result = None
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        if line.startswith('data: '):
            try:
                data = json.loads(line[6:])
                if 'result' in data and data['id'] == 1:
                    result = data['result']
                    break
            except json.JSONDecodeError:
                continue

    proc.stdin.close()
    proc.terminate()
    proc.wait()

    if result is None:
        raise ValueError("No valid result from MCP server")

    # Parse Adzuna response (stringified JSON in some MCP impls)
    if isinstance(result, str):
        result = json.loads(result)
    return result

def format_jobs(data):
    jobs = data.get('results', [])
    if not jobs:
        return "No jobs found today. Try broader terms/location."

    date_str = datetime.now().strftime('%Y-%m-%d')
    msg = f"**Adzuna {data.get(\"count\", \"?\")} Jobs** - {date_str}\n\n"
    for i, job in enumerate(jobs[:10], 1):
        title = job.get('title', 'N/A')
        company = job.get('company', {}).get('display_name', 'N/A')
        loc = job.get('location', {}).get('display_name', 'N/A')
        salary_min = job.get('salary_min')
        salary = f"${int(salary_min):,}k" if salary_min else "N/A"
        url = job.get('redirect_url', '')

        msg += f"{i}. **{title}** @ **{company}**\n"
        msg += f"   💰 {salary}/yr | 📍 {loc}\n"
        if url:
            msg += f"   🔗 {url}\n"
        msg += "\n"

    return msg

def send_to_discord(DISCORD_WEBHOOK, message):
    if len(message) > 1900:
        message = message[:1890] + "\n*(truncated)*"
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10).raise_for_status()
        print("Sent to Discord!")
    except Exception as e:
        print(f"Discord send failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 search_jobs.py 'AI/ML' 'Irvine'")
        sys.exit(1)

    if not DISCORD_WEBHOOK:
        print("Missing DISCORD_WEBHOOK environment variable")
        sys.exit(1)

    query, location = sys.argv[1], sys.argv[2]

    if not DISCORD_WEBHOOK:
        print("Missing Discord webhook: ~/.config/nanobot/discord_webhook.txt")
        sys.exit(1)

    print(f"Searching Adzuna (via config MCP) for '{query}' in '{location}'...")
    try:
        jobs_data = mcp_tool_call(query, location)
        message = format_jobs(jobs_data)
        print(message)
        send_to_discord(DISCORD_WEBHOOK, message)
    except Exception as e:
        err_msg = f"Error: {str(e)}"
        print(err_msg)
        send_to_discord(DISCORD_WEBHOOK, err_msg)
