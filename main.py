import sys
import math
import csv
import re
import os

RADIUS = 20
IDLE_COST = 1
MESSAGE_COST = 2


class Node:
    def __init__(self, node_id, x, y, energy):
        self.id = node_id
        self.x = x
        self.y = y
        self.energy = energy
        self.role = ""          # "leader", "member", or "isolated"
        self.cluster_id = None  # matches the leader's id for that cluster
        self.energy_history = []  # list of (tick, energy) snapshots


def load_nodes(filepath):
    with open(filepath, "r") as f:
        raw = f.read()

    # expecting triplets like (x, y, energy) anywhere in the file
    triplets = re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", raw)
    if not triplets:
        raise ValueError(f"Couldn't find any (x, y, energy) triplets in: {filepath}")

    node_list = []
    for idx, (x, y, energy) in enumerate(triplets, start=1):
        node_list.append(Node(node_id=idx, x=float(x), y=float(y), energy=int(energy)))

    return node_list


def euclidean(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def build_clusters(nodes):
    # highest-energy node gets to claim its neighbours first
    sorted_nodes = sorted(nodes, key=lambda n: (-n.energy, n.id))
    taken = set()

    for nd in sorted_nodes:
        if nd.id in taken:
            continue

        nearby = [
            other for other in nodes
            if other.id != nd.id and other.id not in taken and euclidean(nd, other) <= RADIUS
        ]

        if nearby:
            nd.role = "leader"
            nd.cluster_id = nd.id
            taken.add(nd.id)
            for nb in nearby:
                nb.role = "member"
                nb.cluster_id = nd.id
                taken.add(nb.id)
        else:
            # no reachable neighbours
            nd.role = "isolated"
            nd.cluster_id = nd.id
            taken.add(nd.id)

    return nodes


def handle_leader_death(dead_leader, cluster_members, events):
    """
    When a leader dies we need to pick a replacement from whoever is left.
    The election costs a round of messaging, so every node in range pays MESSAGE_COST.
    Nodes too far from the new candidate get dropped to isolated.
    """
    if not cluster_members:
        events.append(f"Cluster {dead_leader.id} has ended")
        return []

    # pick the candidate with most energy
    candidate = max(cluster_members, key=lambda n: (n.energy, -n.id))

    reachable   = [n for n in cluster_members if euclidean(n, candidate) <= RADIUS]
    unreachable = [n for n in cluster_members if euclidean(n, candidate) >  RADIUS]

    # election broadcast drains everyone in range
    for n in reachable:
        n.energy -= MESSAGE_COST

    # nodes out of range can't participate
    for n in unreachable:
        n.cluster_id = n.id
        n.role = "isolated"
        events.append(f"Node {n.id} fell out of radius and became isolated")

    # some nodes might have drained to 0 just from the election messages
    died_in_election = [n for n in reachable if n.energy <= 0]
    survived = [n for n in reachable if n.energy > 0]

    if not survived:
        events.append(f"Cluster {dead_leader.id} ended during election")
        return died_in_election

    new_leader = max(survived, key=lambda n: (n.energy, -n.id))
    events.append(f"Node {new_leader.id} became new leader after Node {dead_leader.id} died")

    for n in survived:
        n.cluster_id = new_leader.id
        n.role = "leader" if n.id == new_leader.id else "member"

    return died_in_election


def try_reintegrate(nodes, events):
    """
    After elections settle, give isolated nodes a chance to join a nearby cluster.
    Only the closest leader within RADIUS is considered.
    """
    isolated = [n for n in nodes if n.role == "isolated"]
    leaders  = [n for n in nodes if n.role == "leader"]

    for nd in isolated:
        closest_leader = None
        closest_dist = float("inf")
        for ldr in leaders:
            d = euclidean(nd, ldr)
            if d <= RADIUS and d < closest_dist:
                closest_dist = d
                closest_leader = ldr

        if closest_leader is not None:
            nd.role = "member"
            nd.cluster_id = closest_leader.id
            events.append(f"Node {nd.id} re-integrated into cluster {closest_leader.id}")


def run_simulation(nodes, log_path, events_path):
    tick = 0
    death_log = []  # (node_id, tick) pairs

    while nodes:
        tick += 1
        tick_events = []

        # energy drain phase
        for nd in nodes:
            nd.energy -= IDLE_COST
        for nd in nodes:
            if nd.role == "leader":
                nd.energy -= MESSAGE_COST

        # figure out who died this tick
        dead_this_tick = [nd for nd in nodes if nd.energy <= 0]
        nodes = [nd for nd in nodes if nd.energy > 0]

        for nd in dead_this_tick:
            death_log.append((nd.id, tick))
            tick_events.append(f"Node {nd.id} died (role={nd.role})")
            nd.energy_history.append((tick, nd.energy))

        # re-elect leaders where needed
        dead_leaders = [nd for nd in dead_this_tick if nd.role == "leader"]
        election_casualties = []

        for ldr in dead_leaders:
            orphans = [nd for nd in nodes if nd.cluster_id == ldr.id]
            extra_dead = handle_leader_death(ldr, orphans, tick_events)
            election_casualties.extend(extra_dead)

        casualty_ids = {nd.id for nd in election_casualties}
        nodes = [nd for nd in nodes if nd.id not in casualty_ids]

        for nd in election_casualties:
            death_log.append((nd.id, tick))
            tick_events.append(f"Node {nd.id} died during election")
            nd.energy_history.append((tick, nd.energy))

        # isolated nodes check if they can rejoin
        try_reintegrate(nodes, tick_events)

        # snapshot energy for everyone still alive
        for nd in nodes:
            nd.energy_history.append((tick, nd.energy))

        write_tick_to_csv(log_path, tick, nodes + dead_this_tick + election_casualties)
        with open(events_path, "a") as ef:
            for evt in tick_events:
                ef.write(f"Tick {tick}: {evt}\n")

        print(f"\n── Tick {tick} ──────────────────────────────")
        for nd in sorted(nodes, key=lambda x: x.id):
            print(f"  Node {nd.id:2d} | energy={nd.energy:4d} | {nd.role:<9} | cluster={nd.cluster_id}")
        for evt in tick_events:
            print(f"  [event] {evt}")

    print("\n══ Simulation ended ══════════════════════════")
    print(f"  Total ticks: {tick}")
    print("  Node death order:")
    for nid, t in sorted(death_log, key=lambda x: x[1]):
        print(f"    Node {nid} died at tick {t}")

    return tick, death_log


def write_tick_to_csv(filepath, tick, nodes):
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        for nd in nodes:
            # clamp to 0 so we don't write negative energy into the CSV
            logged_energy = max(nd.energy, 0)
            writer.writerow([tick, nd.id, nd.x, nd.y, logged_energy, nd.role, nd.cluster_id])


def save_energy_plot(all_nodes, out_path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping plot")
        return

    plt.figure(figsize=(10, 5))
    for nd in all_nodes:
        if not nd.energy_history:
            continue
        ticks    = [t for t, _ in nd.energy_history]
        energies = [e for _, e in nd.energy_history]
        plt.plot(ticks, energies, label=f"Node {nd.id}")

    plt.xlabel("Tick")
    plt.ylabel("Energy")
    plt.title("Node energy over time")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(out_path)
    print(f"Energy plot saved to {out_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py inputs/input1.txt")
        sys.exit(1)

    input_file = sys.argv[1]

    # mirror the input filename in the output folder name so results are easy to find
    base_name  = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join("outputs", f"outputs_of_{base_name}")
    os.makedirs(output_dir, exist_ok=True)

    log_path    = os.path.join(output_dir, "simulation_log.csv")
    events_path = os.path.join(output_dir, "events_log.txt")
    plot_path   = os.path.join(output_dir, "energy_plot.png")

    nodes = load_nodes(input_file)
    print(f"Loaded {len(nodes)} nodes from {input_file}")

    build_clusters(nodes)

    # tick 0 snapshot before any energy is consumed
    for nd in nodes:
        nd.energy_history.append((0, nd.energy))

    print("\nInitial cluster assignment:")
    for nd in sorted(nodes, key=lambda x: x.id):
        print(f"  Node {nd.id:2d} | energy={nd.energy:4d} | {nd.role:<9} | cluster={nd.cluster_id}")

    # initialise output files
    with open(events_path, "w") as ef:
        ef.write("Simulation Events\n")
        ef.write("Tick 0: Initial clusters formed\n")

    with open(log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "node_id", "x", "y", "energy", "role", "cluster_id"])

    write_tick_to_csv(log_path, 0, nodes)

    # keep a full roster for the energy plot
    all_nodes = nodes[:]

    run_simulation(nodes, log_path, events_path)

    save_energy_plot(all_nodes, out_path=plot_path)
    print(f"\nCSV log saved to {log_path}")
    print(f"Events log saved to {events_path}")


if __name__ == "__main__":
    main()