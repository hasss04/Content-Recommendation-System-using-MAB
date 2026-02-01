import os, subprocess, threading, sys, time
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
FRONTEND = os.path.join(ROOT, "frontend")

def run_backend():
    os.chdir(BACKEND)
    subprocess.run(["uvicorn", "main:app", "--reload"])

def run_frontend():
    os.chdir(FRONTEND)
    subprocess.run(["streamlit", "run", "app.py"])

def run_dashboard():
    os.chdir(FRONTEND)
    subprocess.run(["streamlit", "run", "dashboard.py", "--server.port", "8502"])

def run_trainer():
    while True:
        print(f"\n🧠 Running trainer.py at {datetime.now()}")
        subprocess.run([sys.executable, os.path.join(BACKEND, "trainer.py")])
        time.sleep(300)

print("🚀 Launching RL Recommendation System")
threading.Thread(target=run_backend, daemon=True).start()
threading.Thread(target=run_frontend, daemon=True).start()
threading.Thread(target=run_dashboard, daemon=True).start()
threading.Thread(target=run_trainer, daemon=True).start()

while True:
    time.sleep(10)