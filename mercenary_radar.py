import requests
import os
import sys
import csv
from datetime import datetime
from google import genai

YIELDS_API = "https://yields.llama.fi/pools"
LEDGER_FILE = "mercenary_radar.csv"

def get_top_pool():
    try:
        res = requests.get(YIELDS_API).json().get('data', [])
        # Filter for safety (>$1M TVL)
        safe_pools = [p for p in res if p.get('tvlUsd', 0) > 1000000]
        safe_pools.sort(key=lambda x: x['apy'], reverse=True)
        return safe_pools[0] if safe_pools else None
    except Exception as e:
        print(f"API Error: {e}")
        return None

def get_verdict(pool, api_key):
    prompt = f"""
    You are a DeFi quant agent. Bankroll: £6.00. Gas fee: £0.30.
    Top pool: {pool['symbol']} at {pool['apy']}%.
    Calculate exact daily profit and gas break-even time in days.
    If break-even is < 1 day, output VERDICT: EXECUTE. Otherwise VERDICT: REJECT.
    Rule: Be brutally concise. Use maximum 2 sentences. No fluff.
    Format strictly as: [Math explanation]. VERDICT: [EXECUTE/REJECT]
    """
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip().replace('\n', ' ')
    except Exception as e:
        return f"BRAIN ERROR: {e}"

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: 
        sys.exit(0)

    top_pool = get_top_pool()
    if not top_pool: 
        sys.exit(0)

    verdict = get_verdict(top_pool, api_key)
    
    file_exists = os.path.exists(LEDGER_FILE)
    with open(LEDGER_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'top_project', 'top_apy', 'gemini_verdict'])
        
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            top_pool['symbol'], 
            f"{top_pool['apy']}%", 
            verdict
        ])

if __name__ == "__main__":
    main()import requests
import os
import sys
import csv
from datetime import datetime
from google import genai

# Configuration
YIELDS_API = "https://yields.llama.fi/pools"
LEDGER_FILE = "ransom_ledger.csv"
CURRENT_ASSET = "SUSDS" 
CURRENT_APY = 4.0 

def get_yield_data():
    try:
        response = requests.get(YIELDS_API)
        data = response.json().get('data', [])
        
        filtered_pools = []
        for pool in data:
            if pool.get('tvlUsd', 0) > 1000000: # TVL > $1M safety check
                filtered_pools.append({
                    'chain': pool.get('chain'),
                    'project': pool.get('project'),
                    'symbol': pool.get('symbol'),
                    'tvlUsd': pool.get('tvlUsd'),
                    'apy': pool.get('apy')
                })
        
        filtered_pools.sort(key=lambda x: x['apy'], reverse=True)
        return filtered_pools[:5]
    except Exception as e:
        print(f"Error fetching Yields: {e}")
        return []

def ask_brain(pools_data, api_key):
    prompt = f"""
    You are a highly conservative, hyper-rational DeFi agent managing a 'Ransom Fund'.
    
    Current Status:
    - We currently hold: {CURRENT_ASSET}
    - Current APY: {CURRENT_APY}%
    
    CRITICAL RULE:
    To prevent transaction fee drain, you MUST NOT switch assets unless a new pool offers an APY that is at least 0.5% HIGHER than our current APY.
    
    Here are the top 5 safest, highest-yielding pools right now:
    {pools_data}
    
    Analyze the data based on the critical rule.
    Format your entire response as a single paragraph starting with either:
    "CHOICE: [NEW SYMBOL] " followed by your reasoning.
    OR
    "CHOICE: {CURRENT_ASSET} " followed by your reasoning why we should hold.
    """
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip().replace('\n', ' ')
    except Exception as e:
        return f"CHOICE: {CURRENT_ASSET} BRAIN ERROR: {e}"

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Missing API Key.")
        sys.exit(0)

    print("Scanning DefiLlama Yields API...")
    top_pools = get_yield_data()
    
    if not top_pools:
        print("No yield data found.")
        sys.exit(0)

    analysis = ask_brain(top_pools, api_key)
    chosen_asset = analysis.split(' ')[1] if 'CHOICE:' in analysis else CURRENT_ASSET

    print(f"Pulse complete. Top Pool: {top_pools[0]['symbol']} @ {top_pools[0]['apy']}%. Verdict logged.")

    file_exists = os.path.exists(LEDGER_FILE)
    with open(LEDGER_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'chosen_asset', 'raw_analysis'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), chosen_asset, analysis])

if __name__ == "__main__":
    main()
