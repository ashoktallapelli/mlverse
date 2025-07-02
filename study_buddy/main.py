import argparse
import subprocess
import sys

def run_cli(extra_args):
    subprocess.run(["python", "-m", "interfaces.cli.cli_main"] + extra_args)

def run_web():
    subprocess.run(["streamlit", "run", "interfaces/web/web_main.py"])

def run_api():
    subprocess.run(["uvicorn", "interfaces.api.api_main:app", "--host", "0.0.0.0", "--port", "1000"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["cli", "web", "api"], required=True)
    args, unknown = parser.parse_known_args()  # unknown will capture extra args

    if args.mode == "cli":
        run_cli(unknown)
    elif args.mode == "web":
        run_web()
    elif args.mode == "api":
        run_api()
    else:
        print("Invalid mode. Choose from 'cli', 'web', 'api', or 'tui'.")
        sys.exit(1)
