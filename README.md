# Compare ThreadPool vs. ProcessPool in Python

This repository contains experiments comparing the performance of `ThreadPoolExecutor` and `ProcessPoolExecutor` from Python's `concurrent.futures` module.

## The Problem: Python's GIL

In CPython, the **Global Interpreter Lock (GIL)** is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes at once. This means that even on a multi-core CPU, CPU-bound workloads often cannot run in parallel when using threads.

## Experiment Overview

The goal of this project is to demonstrate how the GIL affects performance across different types of workloads:

1. **CPU-Bound Tasks:** Heavy mathematical computations (e.g., calculating factorials or primes). These require constant CPU cycles.
2. **I/O-Bound Tasks:** Tasks that involve waiting (e.g., `time.sleep()`, file I/O, or network requests). The GIL is released during these waiting periods.

## Comparison Table

| Feature | ThreadPoolExecutor | ProcessPoolExecutor |
| --- | --- | --- |
| **Parallelism** | Limited by GIL (Concurrency only) | True Parallelism (Bypasses GIL) |
| **Memory** | Shares memory space | Separate memory space per process |
| **Overhead** | Low (Lightweight threads) | High (Starting new processes/IPC) |
| **Best For** | I/O-bound tasks (API calls, DB queries) | CPU-bound tasks (Data processing, Math) |

## Getting Started

### Prerequisites

* Python 3.x

### Running the Experiment

Clone the repository and run the main script to see the benchmark results:

```bash
git clone https://github.com/tkuro11/compare_between_threadpool_and_processpool.git
cd compare_between_threadpool_and_processpool
python main.py

```

## Expected Results

* **For CPU-bound tasks:** You will likely observe that `ProcessPoolExecutor` is significantly faster because it utilizes multiple CPU cores simultaneously. `ThreadPoolExecutor` may even be slower than a single-threaded execution due to lock contention overhead.
* **For I/O-bound tasks:** Both will show improvements over sequential execution, but `ThreadPoolExecutor` is generally preferred here due to lower resource consumption and faster startup times.
