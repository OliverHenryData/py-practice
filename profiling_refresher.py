





# cProfile is a built-in Python module that provides a way to measure the performance of Python code. It allows you to profile your code and gather statistics about the time spent in each function, the number of calls made to each function, and other performance-related information.
# how often functions are called and how much time is spent in each function. 
# can help to identify performance bottlenecks 
# and optimize your code for better efficiency.

# Terms:
#   wall time: elapsed clock time
#   n_calls: number of calls to the function
#   totime: time spent in this func only NOT including subcalls!!!
#   cumtime: cumulative time spent in this func AND all subcalls!!!
#   percall: time per call 
#   sort_stats("cumtime") sorts by cumulative time spent in the function and its subcalls, which is useful for identifying functions 
#       that are taking a long time to execute overall. can choose what to sort by

import cProfile
import pstats
import time
from io import StringIO
import numpy as np
import pandas as pd

#timing decorator to time functions
# allows us to write @timer before any funciton to time it
import functools 

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args,**kwargs)
        end_time = time.perf_counter()
        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    
    return wrapper

@timer
def basic_time_demo(n:int = 10_000_000) -> None:

    for _ in range(n):
        pass
    return None


def profile_function(func, *args, sort_by: str = "cumtime", lines: int = 20):
    """
    
    """

    profiler = cProfile.Profile()

    profiler.enable() # begin collecting data

    result = func(*args)

    profiler.disable() # stop collecting data

    #pstats turns raw profiler data into readable stats
    output = StringIO()
    # gives a fake file object in memory, 
    # so we can capture the output of the stats and print it later

    stats = pstats.Stats(profiler,stream=output) #stream given as the output
    #Instead of printing pstats output directly to the terminal,
    #write it into this in-memory text buffer.

    #remove long file paths to make output readable
    stats.strip_dirs()

    #sort and print slowest functions

    stats.sort_stats(sort_by)
    stats.print_stats(lines)

    print(output.getvalue())
    return result

def python_loop_sum_squares(n: int) -> int:
    """
    Slow-ish pure Python loop.

    This is CPU-bound Python work.

    The loop runs in Python bytecode, so it is much slower than equivalent
    vectorised NumPy code for large arrays.
    """

    total = 0

    for i in range(n):
        total += i * i

    return total

def numpy_sum_squares(n: int) -> int:
    """
    Fast NumPy version.

    np.arange(n) creates a NumPy array.
    arr * arr is vectorised.
    The loop happens in fast compiled code, not in Python bytecode.

    Important:
        NumPy integer types can overflow if numbers get too large.
        Here n is chosen small enough for demonstration.
    """

    arr = np.arange(n, dtype=np.int64)
    return int(np.sum(arr * arr))

def make_price_dataframe(n: int) -> pd.DataFrame:
    """
    Create fake OHLC-style market data.

    This gives us a dataframe similar to what a trading app might use.

    We create:
        close
        fast_ma
        slow_ma
        signal-like columns later

    np.random.default_rng(42):
        Creates a reproducible random number generator.
        The seed 42 means the same fake data is generated each run.
    """

    rng = np.random.default_rng(42)

    # Random normal returns.
    returns = rng.normal(loc=0.0, scale=1.0, size=n)

    # Random walk price series.
    close = 100 + np.cumsum(returns)

    df = pd.DataFrame(
        {
            "close": close,
        }
    )

    # Rolling moving averages.
    # min_periods=1 avoids NaN at the start.
    df["fast_ma"] = df["close"].rolling(window=10, min_periods=1).mean()
    df["slow_ma"] = df["close"].rolling(window=50, min_periods=1).mean()

    return df

def signal_count_iterrows(df: pd.DataFrame) -> int:
    """
    Deliberately slow pandas pattern.

    iterrows() loops over dataframe rows as index, Series pairs.

    Each row becomes a pandas Series.
    That is convenient but slow.

    This is a common performance problem in beginner/intermediate pandas code.
    """

    count = 0

    for _, row in df.iterrows():
        if row["fast_ma"] > row["slow_ma"]:
            count += 1

    return count


def signal_count_itertuples(df: pd.DataFrame) -> int:
    """
    Faster row iteration.

    itertuples() returns lightweight namedtuples.

    It is usually much faster than iterrows(), but still a Python-level loop.

    This is a decent fallback if vectorisation is awkward.
    """

    count = 0

    for row in df.itertuples(index=False):
        if row.fast_ma > row.slow_ma:
            count += 1

    return count


def signal_count_vectorised(df: pd.DataFrame) -> int:
    """
    Fast vectorised pandas version.

    df["fast_ma"] > df["slow_ma"] creates a boolean Series.
    sum() counts True values because True behaves like 1 and False like 0.

    This pushes the comparison into optimised pandas/NumPy internals.
    """

    return int((df["fast_ma"] > df["slow_ma"]).sum())


# ------------------------------------------------------------
# Bad dataframe construction pattern
# ------------------------------------------------------------

def build_dataframe_bad_concat(n: int) -> pd.DataFrame:
    """
    Deliberately bad pattern.

    Repeatedly concatenating dataframes in a loop is usually slow.

    Why?
        Each concat may allocate/copy data repeatedly.

    This kind of pattern can appear in backtests when someone appends one row
    at a time to a dataframe.
    """

    df = pd.DataFrame(columns=["i", "value"])

    for i in range(n):
        new_row = pd.DataFrame(
            {
                "i": [i],
                "value": [i * i],
            }
        )

        df = pd.concat([df, new_row], ignore_index=True)

    return df


def build_dataframe_list_then_once(n: int) -> pd.DataFrame:
    """
    Better pattern.

    Build a normal Python list of dictionaries first.
    Then create the dataframe once.

    This avoids repeated dataframe reallocation/copying.
    """

    rows = []

    for i in range(n):
        rows.append(
            {
                "i": i,
                "value": i * i,
            }
        )

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# Mini trading-style pipeline to profile
# ------------------------------------------------------------

def deliberately_slow_pipeline(df: pd.DataFrame) -> dict:
    """
    Deliberately slow fake strategy pipeline.

    This imitates a bad trading-app pattern:
        - row-by-row pandas iteration
        - repeated calculations
        - Python-level loops

    We profile this so cProfile can show where time goes.
    """

    count_iterrows = signal_count_iterrows(df)
    count_itertuples = signal_count_itertuples(df)
    count_vectorised = signal_count_vectorised(df)

    return {
        "iterrows_count": count_iterrows,
        "itertuples_count": count_itertuples,
        "vectorised_count": count_vectorised,
    }


def better_pipeline(df: pd.DataFrame) -> dict:
    """
    Better fake strategy pipeline.

    This uses vectorised pandas operations.

    The point is not that vectorisation is always possible,
    but that you should avoid row-wise pandas loops when a vectorised
    expression is simple and clear.
    """

    count_vectorised = signal_count_vectorised(df)

    # Example of a vectorised signal column.
    signal = df["fast_ma"] > df["slow_ma"]

    # Count signal changes.
    # signal.ne(signal.shift()) means:
    #     True when current signal differs from previous signal.
    signal_changes = int(signal.ne(signal.shift()).sum())

    return {
        "vectorised_count": count_vectorised,
        "signal_changes": signal_changes,
    }

def run_dataframe_building_demo() -> None:
    """
    Compare bad repeated concat with list-then-dataframe.

    n is kept small because repeated concat gets bad quickly.
    """

    print("\n=== DataFrame building demo ===")

    n = 2_000

    
    df_bad = build_dataframe_bad_concat(
        n,
    )

    df_good = build_dataframe_list_then_once(
        n,
    )

    print("\nSame number of rows?")
    print(len(df_bad) == len(df_good))

def main():
    n = 10_000_000

    print("\nRunning basic timer decorated function")
    basic_time_demo()

    # Profile the pure Python loop
    print("\nProfiling pure Python loop:")
    profile_function(python_loop_sum_squares, n)

    # Profile the vectorised NumPy code
    print("\nProfiling vectorised NumPy code:")
    profile_function(numpy_sum_squares, n)

    print("\nProfiling dataframe building:")
    profile_function(run_dataframe_building_demo)

if __name__ == "__main__":
    print("Begin profiling...")
    main()