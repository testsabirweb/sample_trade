import signal
import sys
import threading  # Import threading to manage WebSocket connection in a separate thread
import time as time_module
from fyers_apiv3.FyersWebsocket import data_ws
from custom_logger import logger, log_path, write_html_log
from auto_login import full_access_token
from helper import get_dates, getdata, getBankNiftyExpiryDate
from config import Config
from strategy1 import strategy1

# Global shutdown event for signaling threads
shutdown_event = threading.Event()
# Global config
config = Config()
config.expiry = "NSE:BANKNIFTY" + str(getBankNiftyExpiryDate())


# Function to handle the interrupt signal
def signal_handler(sig, frame):
    logger.info("You pressed Ctrl+C! Closing WebSocket connection and exiting.")
    shutdown_event.set()  # Signal all threads to shutdown
    sys.exit(0)


# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)


#################################################################################
###########         Web socket implementation       #############################
#################################################################################
running = True


# Callback function for handling incoming WebSocket messages
def on_message(message):
    global config

    t = time_module.localtime()
    tmin = time_module.strftime("%M", t)
    tsec = time_module.strftime("%S", t)
    rto, rfrom = get_dates(4)
    if int(tmin) % 5 == 0 and int(tsec) >= 1 and config.fmflag == 0:
        logger.debug("5 ema data updated for 5 min time frame")
        config = getdata(config.sym, 5, rfrom, rto, message["ltp"], config)
        config.fmflag = 1
        if config.p_pos == 0:
            config.p_flag = 0
    if int(tmin) % 5 != 0 and config.fmflag == 1:
        config.fmflag = 0
    if int(tmin) % 5 == 0 and int(tsec) >= 1 and config.fimflag == 0:
        logger.debug("5 ema data updated for 15 min time frame")
        config = getdata(config.sym, 15, rfrom, rto, message["ltp"], config)
        config.fimflag = 1
        if config.c_pos == 0:
            config.c_flag = 0
    if int(tmin) % 5 != 0 and config.fimflag == 1:
        config.fimflag = 0

    logger.info(message)
    if not config.data_5_timeframe.empty and not config.data_15_timeframe.empty:
        strategy1(config, message, logger)


# Callback function for handling WebSocket errors


def on_error(error):
    logger.critical(f"Error:{error}")


# Callback function for handling WebSocket close
def on_close(message):
    logger.critical(f"### closed ###, {message}")
    global running
    running = False


# Callback function for handling WebSocket connection open
def on_open():
    global config
    logger.critical(" WS Connection opened")
    # Subscribe to the required symbol with the data type you need
    symbols = [config.sym]
    data_type = "SymbolUpdate"  # For receiving market data updates
    fyers_ws.subscribe(symbols=symbols, data_type=data_type)


# Initialize the WebSocket object outside the run_websocket function
fyers_ws = data_ws.FyersDataSocket(
    access_token=full_access_token,
    log_path=log_path,
    litemode=True,
    reconnect=True,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_connect=on_open,
)


# Function to manage WebSocket connection
def run_websocket():
    fyers_ws.connect()
    while not shutdown_event.is_set():
        # Keep the thread alive and check for the shutdown signal
        time_module.sleep(1)
    # Ensure the WebSocket is disconnected when shutdown is signaled
    fyers_ws.close_connection()


# Start the WebSocket connection in a separate thread
websocket_thread = threading.Thread(target=run_websocket)
websocket_thread.start()
# Start a thread to continuously write HTML logs
html_writer_thread = threading.Thread(target=write_html_log, args=(shutdown_event,))
html_writer_thread.start()

# Keep the main thread alive until it's time to shutdown
try:
    while not shutdown_event.is_set():
        time_module.sleep(1)
except KeyboardInterrupt:
    # Handle any additional cleanup if necessary
    logger.critical(" Main thread received shutdown signal.")
finally:
    # Wait for the WebSocket thread to finish before completely exiting
    websocket_thread.join()
    # Wait for the HTML writer thread to finish before exiting
    html_writer_thread.join()
    logger.critical(" Script terminated. ")
