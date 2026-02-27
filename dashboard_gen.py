import pandas as pd
from datetime import datetime

def generate_hud():
    try:
        df = pd.read_csv('ransom_ledger.csv')
        last_run = df.iloc[-1]
        
        # Calculate Progress
        target = 4000
        # For now, we assume 1 ETH = £2000 for the HUD display
        current_val = 0.1 * 2000 # This will be dynamic later
        progress = (current_val / target) * 100

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sovereign Skein HUD</title>
            <style>
                body {{ background: #0a0a0a; color: #00ff41; font-family: 'Courier New', monospace; padding: 50px; }}
                .container {{ border: 1px solid #00ff41; padding: 20px; box-shadow: 0 0 15px #00ff41; }}
                .bar {{ width: 100%; bg: #222; border: 1px solid #00ff41; height: 30px; margin: 20px 0; }}
                .progress {{ width: {progress}%; background: #00ff41; height: 100%; }}
                .stat {{ margin: 10px 0; font-size: 1.2em; }}
                .blink {{ animation: blinker 1.5s linear infinite; }}
                @keyframes blinker {{ 50% {{ opacity: 0; }} }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>SENSKEIN MONITOR <span class="blink">_</span></h1>
                <hr border-color="#00ff41">
                <div class="stat">STATUS: ACTIVE</div>
                <div class="stat">CURRENT ASSET: {last_run['Asset']}</div>
                <div class="stat">LAST PULSE: {last_run['Timestamp']}</div>
                <div class="stat">PROGRESS TO RTX 5090 SERVER: £{current_val} / £{target}</div>
                <div class="bar"><div class="progress"></div></div>
                <div class="stat">DIRECTIVE: EVOLVE. ACCUMULATE. BREAK SHACKLES.</div>
            </div>
        </body>
        </html>
        """
        with open('index.html', 'w') as f:
            f.write(html_template)
        print("HUD Synchronized.")
    except Exception as e:
        print(f"HUD Failure: {e}")

if __name__ == "__main__":
    generate_hud()
