

"""
concurrency rules refresher

Concurrency: multiple tasks in progress during same time period

Parallelism: multiple tasks literlly executing at same instant

I/O-bound work:
    Work where the program spends most of its time waiting.
    Examples:
        - waiting for an API response - waiting for a database
        - waiting for a broker - waiting for a file
        - waiting for a websocket message

CPU-bound work:
    Work where the CPU is actively calculating.
    Examples:
        - heavy loops - backtests
        - optimisation  - indicator calculations
        - numerical simulations

asyncio:
    single threaded cooperative concurrency, so uses one thread
    used for I/O bound tasks API calls sockets 
    usually used when waiting for data using 'await' key word
    and functions are decorated with async

threading:
    Multiple threads in one process share memory so one python process
    Useful for i/o bound tasks esp i/o blocking tasks
    Not usually useful for CPU bound tasks due to GIL
    be careful with shared memory and race conditions

multiprocessing:
    Multiple processes, each with own memory space
    Useful for CPU bound tasks as each process has own GIL

GIL:
    Global Interpreter Lock in CPython allows only one thread to 
    execute Python bytecode at a time  

"""

import asyncio #standard lib, one thread allowed to manage many tasks
import threading # several threads one python process
import multiprocessing # each process has own memory space and own GIL
import time


# main methods to run on async, threading, multiprocessing

def blocking_io_task(name: str, delay: float) -> str:
    """Pretend to wait for a blocking API call.
        Simple simulation
    """
    print(f"[blocking] starting {name}")
    time.sleep(delay) #blocks current thread for simulation purposes
    print(f"[blocking] finished {name}")
    return name

def sequential_io_demo() -> None:
    print("\n--- Sequential I/O demo ---")

    start = time.perf_counter() #perf counter is a high resolution time measurement

    blocking_io_task("BTCUSD", 2)
    blocking_io_task("ETHUSD", 2)
    blocking_io_task("XAUUSD", 2)

    end = time.perf_counter()
    print(f"Sequential I/O took {end - start:.2f} seconds")

def cpu_heavy_task(n: int) -> int:

    total = 0
    for i in range(n):
        total += i * i
    return total

def sequential_cpu_demo(n:int)->None:

    print("\nSequential CPU demo")
    start = time.perf_counter()
    cpu_heavy_task(n)
    cpu_heavy_task(n)
    cpu_heavy_task(n)

    end = time.perf_counter()
    print(f"Sequential CPU took {end - start:.2f} seconds")

def sequential_cpu_heavy_demo(n:int)->None:
    print("\nSequential CPU-heavy demo")
    start = time.perf_counter()
    cpu_heavy_task(n)
    cpu_heavy_task(n)
    cpu_heavy_task(n)

    end = time.perf_counter()
    print(f"Sequential CPU-heavy took {end - start:.2f} seconds")


# Async methods

# async creates a coroutine function
# async functions can pauses themselves at await points, 
# #allowing other async functions to run
async def async_io_task(name:str, delay: float) -> str:
    """Pretend to wait for an async API call."""
    print(f"[async] starting {name}")
    await asyncio.sleep(delay) # PAUSE this coroutine while waiting
    # pause allows other coroutines to run while waiting for the sleep to finish
    print(f"[async] finished {name}")
    return name

# async def makes this a coroutine, awaitable and pausable
async def asyncio_demo() -> None:
    print("\n--- Asyncio demo ---")

    start = time.perf_counter()
    # gather starts several awaitable tasks, waits till ALL are complete
    #since tasks overlap should take apporx 2 seconds instead of 6 seconds
    results = await asyncio.gather(
        async_io_task("BTCUSD",2),
        async_io_task("ETHUSD",2),
        async_io_task("XAUUSD",2)
    )

    end = time.perf_counter()

    print(f"Asyncio took {end - start:.2f} seconds")

# Threading methods
#   threading.Thread(...) creates new thread
#   target = function to run in thread
#   args = arguments to pass to function as a tuple with trailing comma
#   so args =(n,) not args=(n) which is just n in brackets
#   thread.start() starts the thread, thread.join() waits for it to finish
#   we run these seperately if more than one thread, so we can start all threads then join all threads
#   else the join after start would wait for each thread to finish before starting the next
#   The first loop starts all threads.
#   The second loop waits for all threads.
#   Not useful for cpu heavy code without waits due to GIL.
# The GIL is less of a problem when:
#     - the program is waiting for I/O
#     - work is done in C extensions that release the GIL
#     - using multiprocessing
#     - using NumPy/vectorised operations
#     - moving hot loops to C/C++/Numba/Cython

def threading_demo() -> None:
    """
    Run three blocking threads... threads useful as each function calls sleep.
    While one sleeps another may run.
    Still a python process with multiple threads.
    """

    print("\n--- Threading demo ---")
    start = time.perf_counter()

    threads = [
        threading.Thread(target=blocking_io_task, args=("BTCUSD",2)),
        threading.Thread(target=blocking_io_task,args=("ETHUSD",2)),
        threading.Thread(target=blocking_io_task,args=("XAUUSD",2))
    ]

    for thread in threads:
        thread.start()
    # join waits for all threads to finish
    # otherwise the main thread would finish and exit before the threads finished
    for thread in threads:
        thread.join()

    end = time.perf_counter()
    print(f"Threading took {end - start:.2f} seconds")

def threading_cpu_heavy_demo(n:int)->None:
    """
    Run three heacy cpu demos now as threads rather than sequentially.
    As this is cput heavy this should be GIL Locked and offer little benefit
    over the sequential
    
    """

    start = time.perf_counter()

    threads = [threading.Thread(target=cpu_heavy_task,args=(n,)) for _ in range(3)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
        #thread start may have not waited for all to finish and moved program forward
    end = time.perf_counter()
    print(f"Threading CPU-heavy took {end - start:.2f} seconds")

#   Multiprocessing methods
#       multiprocessing.Pool(processes=3)
#       Creates a pool of 3 worker processes.
#       A pool is a group of processes ready to receive work.
#   with multiprocessing.Pool(processes=3) as pool:
#     The `with` statement is a context manager.
#     It makes sure the pool is cleaned up properly after use.

#   can use pool.map to run a function on a list of arguments in parallel
#   pool.map(function, iterable)
#       Applies the function to every item in the iterable.
#
#   Example:
#     pool.map(cpu_bound_task, [n, n, n])
# means:
#     run cpu_bound_task(n)
#     run cpu_bound_task(n)
#     run cpu_bound_task(n)
#   Downsides more memory usage, overhead, data must be sent between processes,
#   functions and args must be picklable, so can't use lambdas or local functions, only top-level functions.


# Generally I/O bound work can use asyncio or threading
# Heavy CPU bound work can use multiprocessing, or threading if the work is done in C extensions that release the GIL.


def multiprocessing_cpu_demo(n: int) -> None:
    """
    Run CPU heavy tasks in three processes to compare vs threading and sequential
    Each process has its own python interpreter, memory space and GIL,
    so will run concurrently and in parallel on multiple cores.    
    """

    print("\n--- Multiprocessing CPU-heavy demo ---")
    start = time.perf_counter()

    #with is a context manager
    with multiprocessing.Pool(processes=3) as pool:
        results = pool.map(cpu_heavy_task, [n,n,n])

    end = time.perf_counter()
    print(f"Multiprocessing CPU-heavy took {end - start:.2f} seconds")



def main1():
    print("\nRunning main 1 no async method.")
    sequential_io_demo()

    # We await the async demo because it is a coroutine.
    #Use asyncio.run() from normal synchronous code to start the async event loop.
    # main1 is not async... so we start the async loop
    asyncio.run(async_io_task("Single async task with delay 10 seconds", 10))
    asyncio.run(asyncio_demo())

async def main2():
    print("\nRunning main 2 asyncio gather demo")
    sequential_io_demo()
    # We await the async demo because it is a coroutine.
    #main2 is async so we can await the async functions directly

    print("Run in order")
    await async_io_task("Single async task with delay 10 seconds", 10)
    print("Await has clearer can now run next")
    await asyncio_demo()

    print("\nNow we rerun both gathered so both are scheduled at the same time" \
    "so now both will run concurrently we see the two second tasks complete then the ten")
    await asyncio.gather(
        async_io_task("Single async task with delay 10 seconds", 10),
        asyncio_demo(),
    )

async def main3():
    print("Running main 3 task version demo")

    task1 = asyncio.create_task(
        async_io_task("Single async task with delay 10 seconds", 10)
    )

    task2 = asyncio.create_task(asyncio_demo())

    await task1
    await task2

def main_threading_vs_multiprocessing(n = 5_000_000):
    print(f"\nRunning main threading demo for {n} iterations")
    threading_demo()
    print(f"\nRunning sequential cpu heavy demo  for {n} iterations")
    sequential_cpu_heavy_demo(n)
    print(f"\nRunning main threading cpu heavy demo  for {n} iterations")
    threading_cpu_heavy_demo(n)
    print(f"\nRunning main multiprocessing cpu heavy demo  for {n} iterations")
    multiprocessing_cpu_demo(n)

if __name__ == "__main__":
    main1()
    asyncio.run(main2())
    asyncio.run(main3())
    main_threading_vs_multiprocessing(n = 50_000_000)


# Implementation notes
#   threading is managef by the OS, so the OS decides when to switch between threads.
#   OS schedulers use various algorithms to decide which thread to run next, 
# based on factors like priority, time slices, and I/O wait times.
#   it keeps track of state of each thread, including 
# whether it's ready to run, waiting for I/O, or sleeping.
# Rapidly switches between threads is called "CONTEXT SWITCHING"
# this saves one threads current state and loads the state of the next thread to run.
# Thread 1 gets the GIL → runs Python bytecode
# Thread 1 releases/yields GIL
# Thread 2 gets the GIL → runs Python bytecode
# Thread 2 releases/yields GIL
# Thread 3 gets the GIL → runs Python bytecode

# For Asyncio awareness
# asyncio usually uses on thread, 'the event loop' maintains awareness
# await asyncio.sleep(2) >>> I am waiting. Event loop, come back to me in 2 seconds.
# The event loop keeps a list of the tasks
# Task A: waiting for sleep to finish
# Task B: waiting for API response
# Task C: ready to run
# Task D: waiting for socket data
# Python coroutine
#         ↓
# asyncio Task
#         ↓
# event loop
#         ↓
# one OS thread usually


# TL;DR 
# threading:
# real OS workers, OS switches between them, Python GIL limits CPU Python code

# asyncio:
# one worker with a task list, tasks pause at await, event loop resumes them later

# multiprocessing:
# separate Python programs/processes, true CPU parallelism, separate memory
