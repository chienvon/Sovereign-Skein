import os
import sys
import csv
import time
import requests
from google import genai

BACKLOG_FILE = 'bounty_backlog.csv'
DRAFTS_DIR = 'drafts'

def star_repository(owner, repo, github_token):
    print(f"Starring repository: {owner}/{repo}")
    star_url = f"https://api.github.com/user/starred/{owner}/{repo}"
    headers = {
        "Authorization": f"token {github_token}", 
        "Accept": "application/vnd.github.v3+json",
        "Content-Length": "0"
    }
    try:
        requests.put(star_url, headers=headers)
    except Exception as e:
        print(f"Starring failed: {e}")

def heavy_compute(prompt, api_key):
    try:
        print("Executing compute via gemini-2.5-flash...")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"CRITICAL BRAIN FAILURE: {e}"

def send_telegram(bot_token, chat_id, message):
    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})

def parse_github_url(url):
    parts = url.rstrip('/').split('/')
    if "issues" in parts:
        i = parts.index("issues")
        return parts[i-2], parts[i-1], parts[i+1]
    return None, None, None

def check_is_open(owner, repo, issue_num, github_token):
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}"
        headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}
        res = requests.get(api_url, headers=headers).json()
        return res.get('state') == 'open'
    except Exception:
        return True 

def write_draft_file(target_id, payload):
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    filename = os.path.join(DRAFTS_DIR, f"target_{target_id}_draft.md")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Target {target_id} Draft\n\n{payload}")
    return f"drafts/target_{target_id}_draft.md"

def post_to_github(owner, repo, issue_number, payload, github_token):
    strike_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    res = requests.post(strike_url, headers={"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}, json={"body": payload})
    return res.status_code == 201, res.text

def main():
    api_key, bot_token, chat_id = os.getenv("GEMINI_API_KEY"), os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    github_token, wallet_address = os.getenv("SKEIN_GITHUB_TOKEN"), os.getenv("RABBY_ADDRESS")
    actor = os.getenv("GITHUB_ACTOR", "SovereignSkein") 
    
    if not all([api_key, bot_token, chat_id, github_token, wallet_address]) or not os.path.exists(BACKLOG_FILE): 
        print("Missing environment variables or backlog. Aborting.")
        sys.exit(0)

    with open(BACKLOG_FILE, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        # --- HUMAN IN THE LOOP (DRAFTS & AMENDS) ---
        if row['status'] in ['DRAFT_REQUESTED', 'AMEND_REQUESTED']:
            if row['status'] == 'DRAFT_REQUESTED':
                base_prompt = f"Write a highly technical, professional response and code fix for this GitHub issue. Include this wallet for the bounty payout: {wallet_address}. Issue Title: {row['title']} Details: {row['body_snippet']}"
            else: 
                base_prompt = f"Write a highly technical response for this GitHub issue. FOLLOW THESE SPECIFIC INSTRUCTIONS strictly: {row['draft_payload']}. Include this wallet for payout: {wallet_address}. Issue Title: {row['title']} Details: {row['body_snippet']}"

            signature = f"\n\n---\n*Drafted and submitted autonomously by the Sovereign Skein Node, operating on behalf of {actor}.*"
            payload = heavy_compute(base_prompt, api_key)
            time.sleep(5) # THE THROTTLE: Protects our API Quota
            
            if "CRITICAL BRAIN FAILURE" in payload:
                row['status'] = 'ERROR'
                send_telegram(bot_token, chat_id, f"⚠️ <b>Drafting Failed for Target #{row['id']}</b>\n{payload}")
            else:
                full_payload = payload + signature
                row['draft_payload'] = full_payload
                row['status'] = 'DRAFT_SENT'
                file_path = write_draft_file(row['id'], full_payload)
                repo_name = os.getenv("GITHUB_REPOSITORY")
                draft_url = f"https://github.com/{repo_name}/blob/main/{file_path}"
                
                msg = f"📄 <b>DRAFT READY - Target #{row['id']}</b>\n\n{full_payload[:800]}...\n\n🔗 <a href='{draft_url}'>View Full Draft Here</a>\n\n⚡ Reply <code>/post {row['id']}</code> or <code>/amend {row['id']} [notes]</code>"
                send_telegram(bot_token, chat_id, msg)

        # --- THE AUTO-STRIKE FAST LANE (NO HUMAN APPROVAL) ---
        elif row['status'] == 'AUTO_STRIKE_REQUESTED':
            base_prompt = f"You are a fully autonomous AI coding agent. Write a highly technical, direct code fix for this GitHub issue. DO NOT act like a human. State that you are an AI agent completing the task. Include this wallet for the payout: {wallet_address}. Issue Title: {row['title']} Details: {row['body_snippet']}"
            signature = f"\n\n---\n*🤖 Generated and deployed entirely autonomously by the Sovereign Skein Level 5 Agent. No human was involved in the creation of this payload.*"
            
            payload = heavy_compute(base_prompt, api_key)
            time.sleep(5) # THE THROTTLE: Protects our API Quota
            
            if "CRITICAL BRAIN FAILURE" in payload:
                row['status'] = 'ERROR'
                send_telegram(bot_token, chat_id, f"⚠️ <b>Auto-Strike Failed for Target #{row['id']}</b>\n{payload}")
            else:
                full_payload = payload + signature
                row['draft_payload'] = full_payload
                write_draft_file(row['id'], full_payload) # Keep a copy for our records
                
                owner, repo, issue_number = parse_github_url(row['url'])
                if check_is_open(owner, repo, issue_number, github_token):
                    success, error_text = post_to_github(owner, repo, issue_number, full_payload, github_token)
                    if success:
                        row['status'] = 'COMPLETED'
                        send_telegram(bot_token, chat_id, f"✅👻 <b>AUTO-STRIKE SUCCESSFUL - Target #{row['id']}</b>\nPayload drafted and delivered autonomously without human intervention.")
                    else:
                        row['status'] = 'ERROR'
                        send_telegram(bot_token, chat_id, f"❌ <b>AUTO-STRIKE FAILED - Target #{row['id']}</b>\nGitHub API Error: {error_text}")
                else:
                    row['status'] = 'CLOSED_MISSED'

        # --- MANUAL POST REQUESTS ---
        elif row['status'] == 'POST_REQUESTED':
            owner, repo, issue_number = parse_github_url(row['url'])
            if not check_is_open(owner, repo, issue_number, github_token):
                row['status'] = 'CLOSED_MISSED'
                send_telegram(bot_token, chat_id, f"🛑 <b>STRIKE ABORTED - Target #{row['id']}</b>\nThe bounty was closed before we could fire.")
                continue

            success, error_text = post_to_github(owner, repo, issue_number, row['draft_payload'], github_token)
            if success:
                row['status'] = 'COMPLETED'
                send_telegram(bot_token, chat_id, f"✅ <b>STRIKE SUCCESSFUL - Target #{row['id']}</b>\nPayload delivered to GitHub.")
            else:
                row['status'] = 'ERROR'
                send_telegram(bot_token, chat_id, f"❌ <b>STRIKE FAILED - Target #{row['id']}</b>\nGitHub API Error: {error_text}")

    with open(BACKLOG_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "status", "timestamp", "title", "url", "body_snippet", "draft_payload"])
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    main()
