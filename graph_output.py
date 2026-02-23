import re
import glob
import os
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

            # Data line: extract max_wks (if present) and elapsed time
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


def plot_graphs(filepath):
    """Generate 2 graphs from a log file: first 3 blocks and last 3 blocks."""
    blocks = parse_log(filepath)
    if len(blocks) != 6:
        raise ValueError(f"Expected 6 blocks, got {len(blocks)} in {filepath}")

    log_name = os.path.splitext(os.path.basename(filepath))[0]
    groups = [blocks[:3], blocks[3:]]
    group_labels = ["Pure Python", "Numpy"]

    for gi, (group, label) in enumerate(zip(groups, group_labels)):
        fig, ax = plt.subplots(figsize=(10, 6))

        for block in group:
            if not block["max_wks"]:
                # SEQUENTIAL — draw as horizontal baseline
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
        ax.set_title(f"{log_name} — {label}")
        ax.legend()
        ax.grid(True, alpha=0.3)

        out_path = os.path.join(
            os.path.dirname(filepath), f"{log_name}_{label.replace(' ', '_')}.png"
        )
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {out_path}")


def main():
    log_dir = os.path.join(os.path.dirname(__file__), "results")
    log_files = sorted(glob.glob(os.path.join(log_dir, "*.log")))

    if not log_files:
        print(f"No .log files found in {log_dir}")
        return

    for filepath in log_files:
        print(f"Processing: {filepath}")
        plot_graphs(filepath)


if __name__ == "__main__":
    main()
