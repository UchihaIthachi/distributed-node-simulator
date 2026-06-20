import sys
import math
import csv
import re
from dataclasses import dataclass, field
from typing import Optional

RADIUS = 20
IDLE_COST = 1
MESSAGE_COST = 2


@dataclass
class Node:
    id: int
    x: float
    y: float
    energy: int
    role: str = ""
    cluster_id: Optional[int] = None
    energy_history: list = field(default_factory=list)


def parse_input(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    triplets = re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", content)
    if not triplets:
        raise ValueError(f"No valid triplets found in {filepath}")

    nodes = []
    for i, (x, y, energy) in enumerate(triplets, start=1):
        nodes.append(Node(id=i, x=float(x), y=float(y), energy=int(energy)))

    return nodes


def distance(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def form_clusters(nodes):
    # Highest energy node gets first pick of forming a cluster
    sorted_nodes = sorted(nodes, key=lambda n: (-n.energy, n.id))
    assigned = set()

    for node in sorted_nodes:
        if node.id in assigned:
            continue

        neighbours = [
            other for other in nodes
            if other.id != node.id
            and other.id not in assigned
            and distance(node, other) <= RADIUS
        ]

        if neighbours:
            node.role = "leader"
            node.cluster_id = node.id
            assigned.add(node.id)

            for member in neighbours:
                member.role = "member"
                member.cluster_id = node.id
                assigned.add(member.id)
        else:
            # Isolated nodes do not transmit, so they are not marked as leaders.
            node.role = "isolated"
            node.cluster_id = node.id
            assigned.add(node.id)

    return nodes


def elect_new_leader(leader, survivors, events):
    if not survivors:
        events.append(f"Cluster {leader.id} has ended")
        return []

    new_leader = min(survivors, key=lambda n: (-n.energy, n.id))
    events.append(f"Node {new_leader.id} became new leader (was cluster {leader.id})")

    # every survivor broadcasts its energy level as part of the election,
    # so they all pay the message cost, not just the winner
    for survivor in survivors:
        survivor.energy -= MESSAGE_COST
        survivor.cluster_id = new_leader.id

    new_leader.role = "leader"
    for survivor in survivors:
        if survivor.id != new_leader.id:
            survivor.role = "member"

    # a low energy node could win the election and still die paying for it
    casualties = [node for node in survivors if node.energy <= 0]
    return casualties


def run_simulation(nodes, log_path, events_path):
    tick = 0
    death_order = []

    with open(events_path, "w") as ef:
        ef.write("Simulation Events\n")

    while nodes:
        tick += 1
        events = []

        for node in nodes:
            node.energy -= IDLE_COST

        for node in nodes:
            if node.role == "leader":
                node.energy -= MESSAGE_COST

        dead = [node for node in nodes if node.energy <= 0]
        nodes = [node for node in nodes if node.energy > 0]

        for node in dead:
            death_order.append((node.id, tick))
            events.append(f"Node {node.id} died (role={node.role})")

        for leader in [n for n in dead if n.role == "leader"]:
            survivors = [node for node in nodes if node.cluster_id == leader.id]
            casualties = elect_new_leader(leader, survivors, events)
            nodes = [node for node in nodes if node.energy > 0]
            for node in casualties:
                death_order.append((node.id, tick))
                events.append(f"Node {node.id} died during election")

        for node in nodes:
            node.energy_history.append(node.energy)

        write_log(log_path, tick, nodes)
        with open(events_path, "a") as ef:
            for e in events:
                ef.write(f"Tick {tick}: {e}\n")

        print(f"\n── Tick {tick} ──────────────────────────────")
        for node in sorted(nodes, key=lambda x: x.id):
            print(f"  Node {node.id:2d} | energy={node.energy:4d} | {node.role:<9} | cluster={node.cluster_id}")
        for e in events:
            print(f"  [event] {e}")

    print("\n══ Simulation ended ══════════════════════════")
    print(f"  Total ticks: {tick}")
    print("  Node death order:")
    for node_id, t in sorted(death_order, key=lambda x: x[1]):
        print(f"    Node {node_id} died at tick {t}")

    return tick, death_order


def write_log(filepath, tick, nodes):
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        for node in nodes:
            writer.writerow([tick, node.id, node.x, node.y, node.energy, node.role, node.cluster_id])


def plot_energy(all_nodes, output_path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping plot")
        return

    plt.figure(figsize=(10, 5))
    for node in all_nodes:
        if node.energy_history:
            plt.plot(range(len(node.energy_history)), node.energy_history, label=f"Node {node.id}")

    plt.xlabel("Tick")
    plt.ylabel("Energy")
    plt.title("Node energy over time")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Energy plot saved to {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py input1.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    log_path = "simulation_log.csv"
    events_path = "events_log.txt"
    plot_path = "energy_plot.png"

    nodes = parse_input(input_file)
    print(f"Loaded {len(nodes)} nodes from {input_file}")

    form_clusters(nodes)

    for node in nodes:
        node.energy_history.append(node.energy)

    print("\nInitial cluster assignment:")
    for node in sorted(nodes, key=lambda x: x.id):
        print(f"  Node {node.id:2d} | energy={node.energy:4d} | {node.role:<9} | cluster={node.cluster_id}")

    with open(log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "node_id", "x", "y", "energy", "role", "cluster_id"])

    write_log(log_path, 0, nodes)  # tick 0 = state right after clustering, before any drain

    all_nodes = nodes[:]  # keep a copy so we can still plot dead nodes' history later

    run_simulation(nodes, log_path, events_path)

    plot_energy(all_nodes, output_path=plot_path)
    print(f"\nCSV log saved to {log_path}")
    print(f"Events log saved to {events_path}")


if __name__ == "__main__":
    main()