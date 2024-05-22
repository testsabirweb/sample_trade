import os
import logging
import colorlog
import re
import pytz
from datetime import datetime
import threading  # Import threading to manage WebSocket connection in a separate thread
import time as time_module


# Path for the logs directory
log_path = os.path.join(os.getcwd(), "logs")
# Create the logs directory if it doesn't exist
if not os.path.exists(log_path):
    os.makedirs(log_path)

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler for logging to a file
log_file = os.path.join(log_path, "script.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Create a color formatter with IST time and add it to the file handler
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s IST - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %Z%z",
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "white",
        "WARNING": "yellow",
        "ERROR": "magenta",
        "CRITICAL": "red",
    },
)
ist_timezone = pytz.timezone("Asia/Kolkata")
formatter.converter = lambda *args: datetime.now(ist_timezone).timetuple()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Create a StreamHandler for logging to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a lock to synchronize file access
file_lock = threading.Lock()


# Function to convert ANSI escape sequences to HTML span elements with styles
def ansi_to_html(match):
    color_map = {
        "30": "black",
        "31": "red",
        "32": "green",
        "33": "yellow",
        "34": "blue",
        "35": "magenta",
        "36": "cyan",
        "37": "white",
    }
    color_code = match.group(1)
    color = color_map.get(color_code, "white")  # Use "black" as default color
    return f'<span style="color: {color}">'


def convert_logs_to_html(log_content):
    # Convert ANSI escape sequences to HTML span elements
    log_content_html = re.sub(r"\033\[(\d+)m", ansi_to_html, log_content)

    # Add timestamps to log entries
    log_content_html = re.sub(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Z]+\+\d+ \w+ - [A-Z]+ - .+)",
        r"<br>\1",
        log_content_html,
    )

    # Wrap log entries in a <pre> tag for monospace font
    log_content_html = f"<pre>{log_content_html}</pre>"

    return log_content_html


def write_html_log(shutdown_event):
    while not shutdown_event.is_set():  # Add shutdown event check
        with file_lock:
            # Read the log file
            with open("logs/script.log", "r") as log_file:
                log_content = log_file.read()

            # Convert log content to HTML
            log_content_html = convert_logs_to_html(log_content)

            # Generate HTML content with dark gray background
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Log Viewer</title>
            </head>
            <body style="background-color: rgb(34, 34, 34);">
            {log_content_html}
            </body>
            </html>
            """

            # Write HTML content to file
            with open("log_viewer.html", "w") as html_file:
                html_file.write(html_content)

        # Sleep for 1 second before updating again
        time_module.sleep(1)
