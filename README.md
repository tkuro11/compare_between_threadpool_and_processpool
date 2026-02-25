# Compare ThreadPoolExecutor and ProcessPoolExecutor

An experimental repository for comparing the performance of `ThreadPoolExecutor` and `ProcessPoolExecutor` from Python's standard library `concurrent.futures`.

## Background

Current Python (CPython) has a **GIL (Global Interpreter Lock)**, which means that even in a multi-threaded environment, only one thread can execute Python bytecode at a time. Starting from Python 3.13, an experimental no-GIL (free-threaded) implementation has been introduced. This experiment covers that as well.

### **ThreadPoolExecutor (Multi-threading):**
* Lightweight due to shared memory space, but affected by the GIL.
* Effective for I/O-bound tasks (e.g., waiting on network), but offers limited parallelization benefits for CPU-bound tasks (e.g., computation).
* With free-threaded version, the GIL no longer applies, so thread is expected to benefit from true parallelization.

### **ProcessPoolExecutor (Multi-processing):**
* Spawns separate Python interpreter processes, each with its own GIL.
* Can distribute CPU-bound tasks across multiple CPU cores for true parallel execution.
* Incurs overhead from inter-process communication and memory copying.

## Experiments

This project runs the following two types of tasks and compares execution times:

1. **CPU Bound Task:** Heavy computation (e.g., large loop processing).
2. **Lock Free (threadable) Task:** GIL-released code such as C native extensions that don't manipulate Python objects (e.g., numpy).

### Dependencies

* uv 0.9.x or above
* Python 3.x

## How to Run

Run the main script to see the results:

```bash
git clone https://github.com/tkuro11/compare_between_threadpool_and_processpool.git
cd compare_between_threadpool_and_processpool
uv sync
uv run comparison.py
```

## Automated Result Collection

The following script collects results using newest major release python3.14 (with GIL) and python3.14t (free-threaded), saving them under `results/`. Files are named `[cpu brand]-python[version]-[GIL|free_thread].log`.

```bash
uv run collect_results.py
```

## Graphing Results

To generate graphs from the collected results:

```bash
uv run graph_output_combine.py
```

## Interpreting Results (Expected Behavior)

* **CPU-bound tasks:**
  * `ProcessPoolExecutor` is overwhelmingly faster, as computation runs in parallel across multiple cores.
  * `ThreadPoolExecutor` suffers from GIL contention and may perform on par with single-threaded execution, or even slower due to thread-switching overhead.

* **Lock-free tasks:**
  * Both executors benefit from parallelization.
  * However, `ThreadPoolExecutor` tends to be slightly more efficient since it avoids process startup costs.

* **Effect of free-threaded:**
  * For CPU-bound tasks, `ThreadPoolExecutor` sometimes outperforms `ProcessPoolExecutor`.
  * For lock-free (numpy) tasks, some improvement is seen at 2 threads/processes, but in many cases performance degrades as the count increases further. Likely causes include: numpy already performing internal multi-threading leading to over-subscription; fine-grained parallelism via SIMD instructions making thread-level parallelism less effective; and `numpy.sum()` being largely memory-bound, where parallel access actually hurts spatial locality and reduces cache line reuse.

## Conclusion

In GIL-enabled Python, **ProcessPool** is generally the right choice when you need to fully utilize computational resources, while **ThreadPool** is better suited for optimizing wait times such as network I/O. ThreadPool can also be effective when the GIL is released (e.g., numpy), but the gains tend to be limited in many cases.

On the other hand, with the free-threaded build, `ThreadPool` can also benefit from parallel execution, and speed improvements can be expected for CPU-bound tasks written in pure Python. However, for memory-bandwidth-intensive (memory-bound) tasks like `numpy.sum()`, parallelization can actually hurt performance by disrupting locality and causing over-subscription.
