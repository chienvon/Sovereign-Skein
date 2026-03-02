import requests
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
