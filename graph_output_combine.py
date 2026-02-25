import re
import glob
import os
from collections import defaultdict
import matplotlib.pyplot as plt


def parse_log(filepath):
    """Parse a log file into 6 blocks separated by '#### (title) ####' lines.

    Returns a list of dicts:
        {"title": str, "max_wks": list[int], "elapsed": list[float]}
    For SEQUENTIAL blocks, max_wks is empty and elapsed has one value.
    """
    blocks = []
    current = None

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            title_match = re.match(r"^####\s+(.+?)\s+####$", line)
            if title_match:
                if current is not None:
                    blocks.append(current)
                current = {
                    "title": title_match.group(1),
                    "max_wks": [],
                    "elapsed": [],
                }
                continue

            if current is None:
                continue

            wks_match = re.search(r"max_wks\s*=\s*(\d+)", line)
            time_match = re.search(
                r"(?:elapsed|average)\s*(?:time)?\s*:\s*([\d.]+)", line
            )
            if time_match:
                elapsed = float(time_match.group(1))
                if wks_match:
                    current["max_wks"].append(int(wks_match.group(1)))
                current["elapsed"].append(elapsed)

    if current is not None:
        blocks.append(current)

    return blocks


def parse_filename(log_name):
    """Extract (cpu, mode) from log basename without extension.

    e.g. 'Apple M2_python3.14_GIL' -> ('Apple M2', 'GIL')
    """
    print(log_name)
    m = re.match(r"^(.+?)[-_]python[\db.]+[_-](.+)$", log_name)
    print(m)
    if not m:
        raise ValueError(f"Cannot parse log name: {log_name}")
    return m.group(1), m.group(2)


def plot_group(ax, group):
    """Plot one group of 3 blocks onto the given axes."""
    for block in group:
        if not block["max_wks"]:
            ax.axhline(
                y=block["elapsed"][0],
                linestyle="--",
                label=f"{block['title']} ({block['elapsed'][0]:.3f}s)",
            )
        else:
            ax.plot(
                block["max_wks"],
                block["elapsed"],
                marker="o",
                label=block["title"],
            )

    ax.set_xlabel("max_workers")
    ax.set_ylabel("Elapsed Time (s)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

def get_log_files():
    """Retrieve results/ folder from this file's dirname """
    log_dir = os.path.join(os.path.dirname(__file__), "results")
    log_files = sorted(glob.glob(os.path.join(log_dir, "*.log")))

    if not log_files:
        raise(FileNotFoundError(f"No .log files found in {log_dir}"))
    else:
        return log_files, log_dir

def main():
    log_files, log_dir = get_log_files()

    # Build data[cpu][mode] = blocks, preserving insertion order
    data = defaultdict(dict)
    cpus_ordered = []
    modes_ordered = []

    for filepath in log_files:
        print(f"Processing: {filepath}")
        log_name = os.path.splitext(os.path.basename(filepath))[0]
        cpu, mode = parse_filename(log_name)
        blocks = parse_log(filepath)
        if len(blocks) != 6:
            raise ValueError(f"Expected 6 blocks, got {len(blocks)} in {filepath}")
        data[cpu][mode] = blocks
        if cpu not in cpus_ordered:
            cpus_ordered.append(cpu)
        if mode not in modes_ordered:
            modes_ordered.append(mode)

    workloads = [
        ("Pure Python", slice(None, 3), "combined_pure_python.png"),
        ("Numpy",       slice(3, None), "combined_numpy.png"),
    ]
    n_rows = len(cpus_ordered)
    n_cols = len(modes_ordered)

    for workload_name, group_slice, filename in workloads:
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(7 * n_cols, 5 * n_rows))
        # Normalise to 2-D list for uniform indexing
        if n_rows == 1 and n_cols == 1:
            axes = [[axes]]
        elif n_rows == 1:
            axes = [list(axes)]
        elif n_cols == 1:
            axes = [[ax] for ax in axes]
        else:
            axes = [list(row) for row in axes]

        # Column headers (modes)
        for col, mode in enumerate(modes_ordered):
            axes[0][col].set_title(mode, fontsize=12, fontweight="bold", pad=16)

        for row, cpu in enumerate(cpus_ordered):
            for col, mode in enumerate(modes_ordered):
                ax = axes[row][col]
                group = data[cpu][mode][group_slice]
                plot_group(ax, group)

            # Row label on the left y-axis
            axes[row][0].set_ylabel(f"{cpu}\n\nElapsed Time (s)", fontsize=8)

        fig.suptitle(
            f"ThreadPool vs ProcessPool — {workload_name}",
            fontsize=13, fontweight="bold",
        )
        fig.tight_layout(rect=(0, 0, 1, 0.97))

        out_path = os.path.join(log_dir, filename)
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
