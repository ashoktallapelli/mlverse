import argparse
import subprocess
import sys

def run_cli(extra_args):
    subprocess.run(["python", "-m", "interfaces.cli.cli_main"] + extra_args)


def run_web():
    subprocess.run(["streamlit", "run", "interfaces/web/main.py"])

def run_api():
    subprocess.run(["uvicorn", "interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"])

def run_tui():
    subprocess.run(["python", "-m", "interfaces.tui.tui_main"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["cli", "web", "api", "tui"], required=True)
    args, unknown = parser.parse_known_args()  # unknown will capture extra args

    if args.mode == "cli":
        run_cli(unknown)
    elif args.mode == "web":
        run_web()
    elif args.mode == "api":
        run_api()
    elif args.mode == "tui":
        run_tui()
    else:
        print("Invalid mode. Choose from 'cli', 'web', 'api', or 'tui'.")
        sys.exit(1)
