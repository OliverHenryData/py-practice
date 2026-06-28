


import ctypes
import time
from pathlib import Path

HERE = Path(__file__).parent
LIB_PATH = HERE / "libfast_loop.so"

def sum_squares_py(n:int)-> int:
    total = 0;
    for i in range(n):
        total += i*i
    return total

def load_c_library() -> ctypes.CDLL:
    """ctypes.CDLL opens the so file and lets python call funcs inside it"""

    lib = ctypes.CDLL(str(LIB_PATH))

    # tell ctypes what args the c function expects
    lib.sum_squares_c.argtypes = [ctypes.c_uint64]
    # tell ctypes what it returns
    lib.sum_squares_c.restype = ctypes.c_uint64

    return lib

def time_function(label:str,func,*args):

    start_time = time.perf_counter()
    result = func(*args)
    end_time = time.perf_counter()
    elapsed = end_time - start_time

    print(f"{label}: result {result} seconds {elapsed:.6f}")

    return result,elapsed

def main() -> None:
    print("Ctypes speed demo")
    n = 2_000_000
    print(f"\nSumming squares from 0 to {n - 1:,}\n")

    lib = load_c_library()

    py_result, py_time = time_function(
        "Python Loop", sum_squares_py, n,
    )

    c_result, c_time = time_function(
        "C loop via ctypes",
        lib.sum_squares_c,
        n,
    )

    speedup = py_time / c_time
    print(f"  C was about {speedup:.1f}x faster.")


if __name__ == "__main__":
    main()
