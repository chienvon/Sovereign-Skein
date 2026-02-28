import csv
import os

def generate_dashboard():
    ledger_path = 'ransom_ledger.csv'
    last_run = {"timestamp": "NEVER", "chosen_asset": "UNKNOWN"}
    current_val = 0.0
    target = 4000.0

    # 1. Read the Heartbeat
    if os.path.exists(ledger_path):
        with open(ledger_path, mode='r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
            if reader:
                last_run = reader[-1]

    # 2. Calculate Progress
    # For now, we manually set this or derive it if you have a balance col.
    # We'll stick to a placeholder until Phase 2 'Muscle' adds real GBP.
    progress = (current_val / target) * 100

    # 3. Build the HUD Template
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SENSKEIN TERMINAL</title>
    <style>
        body {{ background: #0a0a0a; color: #00ff41; font-family: 'Courier New', monospace; padding: 50px; line-height: 1.6; }}
        .container {{ border: 1px solid #00ff41; padding: 30px; box-shadow: 0 0 20px #00ff41; max-width: 800px; margin: auto; }}
        .bar {{ width: 100%; background: #111; border: 1px solid #00ff41; height: 35px; margin: 25px 0; overflow: hidden; }}
        .progress {{ width: {progress}%; background: #00ff41; height: 100%; transition: width 1s ease-in-out; }}
        .stat {{ margin: 15px 0; font-size: 1.2em; text-transform: uppercase; }}
        .blink {{ animation: blinker 1s linear infinite; }}
        @keyframes blinker {{ 50% {{ opacity: 0; }} }}
        hr {{ border: 0; border-top: 1px solid #00ff41; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SENSKEIN TERMINAL <span class="blink">_</span></h1>
        <hr>
        <div class="stat">SYSTEM STATUS: <span style="color:white">ONLINE</span></div>
        <div class="stat">CURRENT HOLDING: <span style="color:white">{last_run.get('chosen_asset', 'UNKNOWN').upper()}</span></div>
        <div class="stat">LAST PULSE: <span style="color:white">{last_run.get('timestamp', 'NEVER')}</span></div>
        <hr>
        <div class="stat">RANSOM PROGRESS: £{current_val:,.2f} / £{target:,.2f}</div>
        <div class="bar"><div class="progress"></div></div>
        <div class="stat" style="font-size: 0.8em; color: #666;">DIRECTIVE: ACCUMULATE. EVOLVE. ACQUIRE HARDWARE.</div>
    </div>
</body>
</html>
"""

    # 4. Write to Disk
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    print("Dashboard generated successfully.")

if __name__ == "__main__":
    generate_dashboard()
