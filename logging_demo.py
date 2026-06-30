


"""
Logging demo to refresh knowledge

    - Short and to the point but well commented.

"""

import logging
from functools import wraps
from pathlib import Path

# Logging setup

LOG_DIR = Path("logs") #create path obj
LOG_DIR.mkdir(exist_ok=True)

# Loggers can save logs to a file for easier search
# Can seperate DEBUG INFO, WARNING, ERROR with timestamps
# Allows noisy details outside the console

# logger = logging.getLogger(__name__)
#     logger.info("Program started")


# basicConfig is a convenience function for setting up the ROOT logger.
    # It says:
    # - what minimum level to record
    # - what format to use
    # - what handlers to attach

logging.basicConfig(
    level=logging.DEBUG,

    #format for what each log line will look like
    # 2026-06-30 12:20:15 | INFO     | __main__ | Program started
    #format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    
    format=(
        """%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"""
    )
    ,

    datefmt = "%Y-%m-%d %H:%M:%S",

    #handlers decide where logs go:
    # A logger can have multiple handlers.
    # here two handlers one for a file one for terminal


    handlers = [
        logging.FileHandler(LOG_DIR / "debug.log"),
        logging.StreamHandler(),
    ],

    # Both loggers and handlers can have levels.
    #     A message must pass BOTH gates.
    #     Example:
    #     - logger level = DEBUG
    #     - console handler level = INFO
    #     - file handler level = DEBUG
    #     Then:
    #     - DEBUG goes to file only
    #     - INFO/WARNING/ERROR go to both file and console


)

logger = logging.getLogger(__name__)

#decorator log call a function

def log_call(func):
    """log args and kwarfs a function recieved
        when called, what returned and exceptions if failure
    """
    @wraps(func)
    def wrapper(*args,**kwargs):
        logger.debug(
            "Calling function=%s args=%s kwargs=%s",
            func.__name__,
            args,
            kwargs,
        )

        try:
            result = func(*args,**kwargs) #[ass tp func]
            logger.debug("Function=%s returned result =%s",
                         func.__name__,
                         result)
            return result
        except ValueError as e:
            logger.warning(
                "Function=%s raised ValueError %s",
                func.__name__, e,
            )
            raise # now rerasie it and let the caller handle it
        except ZeroDivisionError as e:
            logger.error(
                "Function=%s raised ZeroDivisionError: %s",
                func.__name__,
                e,
            )
            raise
        except Exception as e:
            logger.exception(
                "Function=%s failed with unexpected exception",
                func.__name__,
            )
            raise

        finally:
            print("Finally always runs - gentle reminder")
            logger.debug(
                "Finished call to function =%s", func.__name__,
            )

    return wrapper

    
@log_call
def divide(a,b):
    return a/b

@log_call
def parse_trade(symbol,price,quantity=1,side="BUY"):

    if price < 0:
        raise ValueError("Price must be positive")
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    if side not in {'BUY','SELL'}:
        raise ValueError("Side must be buy or sell")
    
    trade = { "symbol": symbol,  "price": price,
        "quantity": quantity,"side": side,
        "notional": price * quantity,
    }

    return trade

@log_call
def risky_lookup(data, key):
    """
    Demonstrates KeyError.

    KeyError happens when you ask a dictionary for a key that does not exist.
    """

    return data[key]


# VARARGS REMINDER

#def func(*args, **kwargs): 
# args collects extra position arguments into a tuple
# kwargs collects extra keyword arguments into a dict

# func("BTCUSD", 65000, side="BUY", quantity=0.5)
# inside func becomes 
#   args = ("BTCUSD", 65000)
#   kwargs = {"side": "BUY", "quantity": 0.5}

def show_varargs_collection(*args, **kwargs):

    print(f"Type of args {type(args)}")
    print(f"Type of kwargs {type(kwargs)}")

    print(f"Args: {args}")
    print(f"Kwargs: {kwargs}")

def target_function(symbol, price, quantity=1, side="BUY"):
    """
    A normal function with a normal signature.
    target_function(*args, **kwargs)
    That will unpack a tuple and dict into this function.
    """

    print("\n--- TARGET FUNCTION RECEIVED ---")
    print("symbol:", symbol)
    print("price:", price)
    print("quantity:", quantity)
    print("side:", side)

def show_varargs_unpacking():
    """
    This shows the opposite operation:
    taking an existing tuple/dict and unpacking them into a function call.
    """

    args = ("BTCUSD", 65000)
    kwargs = {
        "quantity": 0.5,
        "side": "BUY",
    }

    print("\n--- VARARGS UNPACKING DEMO ---")
    print("About to call:")
    print('target_function(*("BTCUSD", 65000), **{"quantity": 0.5, "side": "BUY"})')

    target_function(*args, **kwargs)

# def wrapper(*args, **kwargs):
#     logger.debug("args=%s kwargs=%s", args, kwargs)
#     return func(*args, **kwargs)
# I do not know or care what signature the original function has.
# I will accept whatever it receives, inspect/log it, then forward it unchanged.


def clean_logger_demo():
    """
    All key points for reading -no run file
    """
    import logging
    from pathlib import Path

    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_DIR / "debug.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def main():

    logger.info("Program started")

    show_varargs_collection(
        "BTCUSD",
        65000,
        side="BUY",
        quantity=0.5,
        live=True,
    )

    show_varargs_unpacking()

    print("\n--- NORMAL FUNCTION CALL ---")
    result = divide(10, 2)
    print("divide result:", result)

    print("\n--- FUNCTION CALL WITH KWARGS ---")
    trade = parse_trade(
        "BTCUSD",
        price=65000,
        quantity=0.5,
        side="BUY",
    )
    print("trade:", trade)


    print("\n--- TRIGGER VALUEERROR ---")

    try:
        parse_trade("ETHUSD", price=-100, quantity=1)
    except ValueError as e:
        print("Caught ValueError in main:", e)


    print("\n--- TRIGGER ZERODIVISIONERROR ---")

    try:
        divide(10, 0)
    except ZeroDivisionError as e:
        print("Caught ZeroDivisionError in main:", e)

    print("\n--- TRIGGER KEYERROR ---")

    try:
        prices = {"BTCUSD": 65000, "ETHUSD": 3500}
        risky_lookup(prices, "XRPUSD")
    except KeyError as e:
        print("Caught KeyError in main:", e)

    logger.info("Program finished")


if __name__ == "__main__":
    main()



