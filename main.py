import sys
import math
import csv
import re
import os

RADIUS = 20
IDLE_COST = 1
MESSAGE_COST = 2

class Node:
    def __init__(self, id, x, y, energy):
        self.id = id
        self.x = x
        self.y = y
        self.energy = energy
        self.role = ""
        self.cluster_id = None
        self.energy_history = []

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
    # highest energy node picks first
    sorted_nodes = sorted(nodes, key=lambda n: (-n.energy, n.id))
    assigned = set()

    for node in sorted_nodes:
        if node.id in assigned:
            continue

        neighbours = []
        for other in nodes:
            if other.id != node.id and other.id not in assigned and distance(node, other) <= RADIUS:
                neighbours.append(other)

        if neighbours:
            node.role = "leader"
            node.cluster_id = node.id
            assigned.add(node.id)

            for member in neighbours:
                member.role = "member"
                member.cluster_id = node.id
                assigned.add(member.id)
        else:
            # isolated nodes don't transmit so they aren't marked as leaders
            node.role = "isolated"
            node.cluster_id = node.id
            assigned.add(node.id)

    return nodes


def elect_new_leader(leader, survivors, events):
    if not survivors:
        events.append(f"Cluster {leader.id} has ended")
        return []

    provisional = max(survivors, key=lambda n: (n.energy, -n.id))

    in_radius = [n for n in survivors if distance(n, provisional) <= RADIUS]
    out_of_radius = [n for n in survivors if distance(n, provisional) > RADIUS]

    for node in in_radius:
        node.energy -= MESSAGE_COST

    for node in out_of_radius:
        node.cluster_id = node.id
        node.role = "isolated"
        events.append(f"Node {node.id} fell out of radius and became isolated")

    casualties = []
    alive_in_radius = []
    for node in in_radius:
        if node.energy <= 0:
            casualties.append(node)
        else:
            alive_in_radius.append(node)

    if not alive_in_radius:
        events.append(f"Cluster {leader.id} ended during election")
        return casualties

    confirmed_leader = max(alive_in_radius, key=lambda n: (n.energy, -n.id))
    if confirmed_leader.id != provisional.id:
        events.append(
            f"Node {provisional.id} died during election; "
            f"Node {confirmed_leader.id} became new leader after Node {leader.id} died"
        )
    else:
        events.append(f"Node {confirmed_leader.id} became new leader after Node {leader.id} died")

    for node in alive_in_radius:
        node.cluster_id = confirmed_leader.id
        if node.id == confirmed_leader.id:
            node.role = "leader"
        else:
            node.role = "member"

    return casualties


def reintegrate_isolated(nodes, events):
    isolated_nodes = [n for n in nodes if n.role == "isolated"]
    leaders = [n for n in nodes if n.role == "leader"]

    for node in isolated_nodes:
        best_leader = None
        best_dist = float("inf")
        for leader in leaders:
            d = distance(node, leader)
            if d <= RADIUS and d < best_dist:
                best_dist = d
                best_leader = leader

        if best_leader is not None:
            node.role = "member"
            node.cluster_id = best_leader.id
            events.append(f"Node {node.id} re-integrated into cluster {best_leader.id}")


def run_simulation(nodes, log_path, events_path):
    tick = 0
    death_order = []

    while nodes:
        tick += 1
        events = []

        for node in nodes:
            node.energy -= IDLE_COST

        for node in nodes:
            if node.role == "leader":
                node.energy -= MESSAGE_COST

        dead = []
        alive = []
        for node in nodes:
            if node.energy <= 0:
                dead.append(node)
            else:
                alive.append(node)
        nodes = alive

        for node in dead:
            death_order.append((node.id, tick))
            events.append(f"Node {node.id} died (role={node.role})")
            node.energy_history.append((tick, node.energy))

        dead_leaders = []
        for n in dead:
            if n.role == "leader":
                dead_leaders.append(n)

        all_casualties = []
        for leader in dead_leaders:
            survivors = []
            for node in nodes:
                if node.cluster_id == leader.id:
                    survivors.append(node)
            casualties = elect_new_leader(leader, survivors, events)
            all_casualties.extend(casualties)

        casualty_ids = {node.id for node in all_casualties}
        nodes = [node for node in nodes if node.id not in casualty_ids]

        for node in all_casualties:
            death_order.append((node.id, tick))
            events.append(f"Node {node.id} died during election")
            node.energy_history.append((tick, node.energy))

        reintegrate_isolated(nodes, events)

        for node in nodes:
            node.energy_history.append((tick, node.energy))

        nodes_to_log = nodes + dead + all_casualties
        write_log(log_path, tick, nodes_to_log)
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
            logged_energy = max(node.energy, 0)
            writer.writerow([tick, node.id, node.x, node.y, logged_energy, node.role, node.cluster_id])


def plot_energy(all_nodes, output_path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping plot")
        return

    plt.figure(figsize=(10, 5))
    for node in all_nodes:
        if node.energy_history:
            ticks = []
            energies = []
            for t, e in node.energy_history:
                ticks.append(t)
                energies.append(e)
            plt.plot(ticks, energies, label=f"Node {node.id}")

    plt.xlabel("Tick")
    plt.ylabel("Energy")
    plt.title("Node energy over time")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Energy plot saved to {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py inputs/input1.txt")
        sys.exit(1)

    input_file = sys.argv[1]

    input_filename = os.path.basename(input_file)
    input_name_without_ext = os.path.splitext(input_filename)[0]
    output_dir = os.path.join("outputs", f"outputs_of_{input_name_without_ext}")
    os.makedirs(output_dir, exist_ok=True)

    log_path = os.path.join(output_dir, "simulation_log.csv")
    events_path = os.path.join(output_dir, "events_log.txt")
    plot_path = os.path.join(output_dir, "energy_plot.png")

    nodes = parse_input(input_file)
    print(f"Loaded {len(nodes)} nodes from {input_file}")

    form_clusters(nodes)

    for node in nodes:
        node.energy_history.append((0, node.energy))

    print("\nInitial cluster assignment:")
    for node in sorted(nodes, key=lambda x: x.id):
        print(f"  Node {node.id:2d} | energy={node.energy:4d} | {node.role:<9} | cluster={node.cluster_id}")

    with open(events_path, "w") as ef:
        ef.write("Simulation Events\n")
        ef.write("Tick 0: Initial clusters formed\n")

    with open(log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "node_id", "x", "y", "energy", "role", "cluster_id"])

    write_log(log_path, 0, nodes)  # log the initial state right after clustering

    all_nodes = nodes[:]  # keep a copy of everyone to plot later even if they die

    run_simulation(nodes, log_path, events_path)

    plot_energy(all_nodes, output_path=plot_path)
    print(f"\nCSV log saved to {log_path}")
    print(f"Events log saved to {events_path}")


if __name__ == "__main__":
    main()