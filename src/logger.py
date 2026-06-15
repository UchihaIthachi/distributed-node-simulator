import csv
import os


HEADERS = ["tick", "node_id", "x", "y", "energy", "role", "cluster_id"]


def init_log(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)


def log_tick(filepath, tick, nodes):
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        for n in nodes:
            writer.writerow([tick, n.id, n.x, n.y, n.energy, n.role, n.cluster_id])


def print_tick(tick, nodes, events=None):
    print(f"\n── Tick {tick} ──────────────────────────────")
    for n in sorted(nodes, key=lambda x: x.id):
        print(f"  Node {n.id:2d} | energy={n.energy:4d} | {n.role:<9} | cluster={n.cluster_id}")
    if events:
        for e in events:
            print(f"  [event] {e}")


def print_summary(total_ticks, death_order):
    print("\n══ Simulation ended ══════════════════════════")
    print(f"  Total ticks: {total_ticks}")
    print("  Node death order:")
    for node_id, tick in death_order:
        print(f"    Node {node_id} died at tick {tick}")
