import sys
import os

from parser import parse_input
from clustering import form_clusters
from simulation import run
from visualization import plot_energy
from logger import init_log


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py input/input1.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    log_path = "output/simulation_log.csv"

    nodes = parse_input(input_file)
    print(f"Loaded {len(nodes)} nodes from {input_file}")

    form_clusters(nodes)
    print("\nInitial cluster assignment:")
    for n in sorted(nodes, key=lambda x: x.id):
        print(f"  Node {n.id:2d} | energy={n.energy:4d} | {n.role:<9} | cluster={n.cluster_id}")

    init_log(log_path)

    all_nodes = nodes[:]

    run(nodes, log_path, verbose=True)

    plot_energy(all_nodes, output_path="output/energy_plot.png")
    print(f"\nCSV log saved to {log_path}")


if __name__ == "__main__":
    main()
