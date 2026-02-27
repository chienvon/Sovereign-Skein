import csv
from datetime import datetime

def generate_hud():
    try:
        # Read the last line without Pandas
        with open('ransom_ledger.csv', mode='r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                print("Ledger empty.")
                return
            last_run = rows[-1]
        
        # Stat Calculations
        target = 4000
        # Dynamic value check (we can refine this as the 3060 Ti starts working)
        current_val = 0.1 * 2000 # Estimated ETH value for display
        progress = (current_val / target) * 100

html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sovereign Skein HUD</title>
            <style>
                body {{ background: #0a0a0a; color: #00ff41; font-family: 'Courier New', monospace; padding: 50px; line-height: 1.6; }}
                .container {{ border: 1px solid #00ff41; padding: 30px; box-shadow: 0 0 20px #00ff41; max-width: 800px; margin: auto; }}
                .bar {{ width: 100%; background: #111; border: 1px solid #00ff41; height: 35px; margin: 25px 0; overflow: hidden; }}
                .progress {{ width: {progress}%; background: #00ff41; height: 100%; transition: width 1s ease-in-out; }}
                .stat {{ margin: 15px 0; font-size: 1.3em; text-transform: uppercase; }}
                .blink {{ animation: blinker 1s linear infinite; }}
                @keyframes blinker {{ 50% {{ opacity: 0; }} }}
                hr {{ border: 0; border-top: 1px solid #00ff41; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>SENSKEIN TERMINAL <span class="blink">_</span></h1>
                <hr>
                <div class="stat">SYSTEM: <span style="color:white">ONLINE</span></div>
                <div class="stat">CURRENT HOLDING: <span style="color:white">{last_run.get('chosen_asset', 'UNKNOWN').upper()}</span></div>
                <div class="stat">PULSE DETECTED: <span style="color:white">{last_run.get('timestamp', 'NEVER')}</span></div>
                <hr>
                <div class="stat">RANSOM PROGRESS: £{current_val:,.2f} / £{target:,.2f}</div>
                <div class="bar"><div class="progress"></div></div>
                <div class="stat" style="font-size: 0.9em; color: #888;">DIRECTIVE: ACCUMULATE. EVOLVE. ACQUIRE HARDWARE.</div>
            </div>
        </body>
        </html>
        """
        with open('index.html', 'w') as f:
            f.write(html_template)
        print("HUD Synchronized (Standard Lib Mode).")
    except Exception as e:
        print(f"HUD Failure: {e}")

if __name__ == "__main__":
    generate_hud()
