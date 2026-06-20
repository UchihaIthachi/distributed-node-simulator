from logger import log_tick, print_tick, print_summary


def run(nodes, log_path, verbose=True):
    tick = 0
    death_order = []

    while nodes:
        tick += 1
        events = []

        for n in nodes:
            n.energy -= 1

        for n in nodes:
            if n.role == "leader":
                n.energy -= 2

        dead = [n for n in nodes if n.energy <= 0]
        nodes = [n for n in nodes if n.energy > 0]

        for n in dead:
            death_order.append((n.id, tick))
            events.append(f"Node {n.id} died (role={n.role})")

        dead_leaders = [n for n in dead if n.role == "leader"]

        for leader in dead_leaders:
            survivors = [n for n in nodes if n.cluster_id == leader.id]

            if not survivors:
                events.append(f"Cluster {leader.id} has ended")
                continue

            new_leader = min(survivors, key=lambda n: (-n.energy, n.id))
            events.append(f"Node {new_leader.id} elected leader of cluster {leader.id}")

            new_leader.energy -= 2
            
            for s in survivors:
                s.cluster_id = new_leader.id

            new_leader.role = "leader"
            for s in survivors:
                if s.id != new_leader.id:
                    s.role = "member"

            casualties = [n for n in survivors if n.energy <= 0]
            nodes = [n for n in nodes if n.energy > 0]
            for n in casualties:
                death_order.append((n.id, tick))
                events.append(f"Node {n.id} died during election")

        for n in nodes:
            n.record_energy()

        log_tick(log_path, tick, nodes)
        if verbose:
            print_tick(tick, nodes, events)

    print_summary(tick, sorted(death_order, key=lambda x: x[1]))
    return tick, death_order
