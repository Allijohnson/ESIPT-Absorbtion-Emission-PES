#!/usr/bin/env python3
"""
Gaussian TD-DFT PES Scan Parser and Plotter
Handles excited-state scans (TD=(Root=N)) run with Opt=ModRedundant.
"""

import re
import sys
import argparse
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


ENERGY_RE   = re.compile(r"Total Energy, E\(TD-HF/TD-DFT\)\s*=\s*([-\d.]+)")
OPT_HEAD_RE = re.compile(r"Optimized Parameters")


def find_scan_coord(filepath):
    '''open file'''
    coord_re = re.compile(r"!\s+\w+\s+([\w(),]+)\s+[\d.]+\s+Scan\s+!")
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
        for line in fh:
            m = coord_re.search(line)
            if m:
                return m.group(1)
    return None


def parse_tddft_scan(filepath, coord_label):
    '''keeps a list of the converged energy, by pulling the most recent energy of for each step'''
    coord_re = re.compile(
        r"!\s+\w+\s+" + re.escape(coord_label) + r"\s+([\d.]+)"
    )

    distances  = []
    energies   = []
    last_energy = None

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
        in_opt_block = False
        for line in fh:
            m = ENERGY_RE.search(line)
            if m:
                last_energy = float(m.group(1))
                continue

            if OPT_HEAD_RE.search(line):
                in_opt_block = True
                continue

            if in_opt_block:
                m2 = coord_re.search(line)
                if m2 and last_energy is not None:
                    distances.append(float(m2.group(1)))
                    energies.append(last_energy)
                    in_opt_block = False   
                    last_energy  = None    
                    continue

                if line.strip() == "":
                    in_opt_block = False

    return distances, energies


def relative_kcal(energies):
    '''converts to relative energy in kcal from hartrees'''
    hartree_to_kcal = 627.5094740631
    e_min = min(energies)
    return [(e - e_min) * hartree_to_kcal for e in energies]


def print_table(distances, energies):
    '''table output in terminal with relative energy of each step'''
    rel = relative_kcal(energies)
    print(f"\n{'Point':>6}  {'Distance (Å)':>14}  {'E(TD-DFT) (Hartree)':>22}  {'Rel. E (kcal/mol)':>20}")
    print("-" * 70)
    for i, (d, e, r) in enumerate(zip(distances, energies, rel), 1):
        print(f"{i:>6}  {d:>14.6f}  {e:>22.10f}  {r:>20.4f}")
    print()


def plot_pes(distances, energies, coord_label, output_file=None, title=None):
    '''makes PES plot'''
    rel = relative_kcal(energies)
    min_idx = rel.index(min(rel))

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(
        title or f"TD-DFT Excited-State PES Scan  —  {coord_label}",
        fontsize=14, fontweight="bold", y=1.01
    )

    panels = [
        (axes[0], energies, "E(TD-DFT) (Hartree)",   "Absolute Energy",  "#2563EB"),
        (axes[1], rel,      "Rel. Energy (kcal/mol)", "Relative Energy",  "#DC2626"),
    ]

    for ax, y_vals, ylabel, title, color in panels:
        ax.plot(distances, y_vals, "o-", color=color, linewidth=2,
                markersize=7, markerfacecolor="white", markeredgewidth=2)
        ax.axvline(
            distances[min_idx], color="gray", linestyle="--",
            linewidth=1.2, alpha=0.7,
            label=f"Min @ {distances[min_idx]:.4f} Å"
        )
        y_min = min(y_vals)
        y_max = max(y_vals)

        if ylabel.startswith("Rel."):
            ax.set_ylim(y_min - 2, min(y_max + 2, 35.0))
        else:
            ax.set_ylim(y_min - 0.005, min(y_max + 0.005, y_min +0.056))
            
        ax.set_xlabel(f"{coord_label} Distance (Å)", fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=12)
        ax.legend(fontsize=10)
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
        ax.grid(True, which="major", linestyle="--", alpha=0.4)
        ax.grid(True, which="minor", linestyle=":",  alpha=0.2)
        ax.tick_params(axis="both", which="both", direction="in",
                       top=True, right=True)

    plt.tight_layout()
    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches="tight")
        print(f"Plot saved → {output_file}")
    else:
        plt.show()


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Parse Gaussian TD-DFT PES scan and plot energy vs. distance."
    )
    parser.add_argument("logfile", help="Gaussian .log / .out file")
    parser.add_argument(
        "--save", metavar="OUTPUT.png", nargs="?", const="pes_scan.png",
        help="Save plot to PNG (default: pes_scan.png)"
    )
    parser.add_argument(
        "--coord", metavar="R(4,12)", default=None,
        help="Override the scan coordinate label (auto-detected if omitted)"
    )
    parser.add_argument(
    "--title", metavar="TITLE", default=None,
    help="Custom title for the plot (e.g. 'MS ESIPT Scan - Gas Phase')"
    )
    parser.add_argument(
        "--no-plot", action="store_true",
        help="Print table only, no plot"
    )
    args = parser.parse_args()

    print(f"Parsing: {args.logfile}")

    coord = args.coord or find_scan_coord(args.logfile)
    if not coord:
        print("ERROR: Could not auto-detect scan coordinate.\n"
              "Use --coord R(X,Y) to specify it manually.")
        sys.exit(1)
    print(f"Scan coordinate: {coord}")

    distances, energies = parse_tddft_scan(args.logfile, coord)

    if not distances:
        print("ERROR: No converged scan points found.\n"
              "Check that 'Optimized Parameters' blocks are present in the log.")
        sys.exit(1)

    print(f"Found {len(distances)} converged scan points.")
    print_table(distances, energies)

    if not args.no_plot:
        plot_pes(distances, energies, coord, output_file=args.save, title=args.title)


if __name__ == "__main__":
    main()
