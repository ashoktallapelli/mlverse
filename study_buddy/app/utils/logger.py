import logging

# Configure logging once, globally
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Create and export a reusable logger
logger = logging.getLogger("study_buddy")


def log(msg):
    print(f"[LOG] {msg}")
