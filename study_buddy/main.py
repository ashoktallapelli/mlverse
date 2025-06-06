import argparse
import subprocess

def run_cli():
    subprocess.run(["python", "interfaces/cli/main.py"])

def run_web():
    subprocess.run(["streamlit", "run", "interfaces/web/main.py"])

def run_api():
    subprocess.run(["uvicorn", "interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["cli", "web", "api"], required=True)
    args = parser.parse_args()

    if args.mode == "cli":
        run_cli()
    elif args.mode == "web":
        run_web()
    elif args.mode == "api":
        run_api()
