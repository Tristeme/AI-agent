import os
import logging

# Ensure log directory exists (important for Docker / production environments)
os.makedirs("logs", exist_ok=True)

# Configure logging system
logging.basicConfig(
    filename="logs/app.log",   # Log file path
    level=logging.INFO,        # Log level (INFO, WARNING, ERROR, DEBUG)
    format="%(asctime)s - %(levelname)s - %(message)s"  # Log format
)

# Create logger instance for this module
logger = logging.getLogger(__name__)