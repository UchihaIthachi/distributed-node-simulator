# Assignment Report — Distributed Node Simulator
**CS42623 Distributed Systems | 2021 Batch Semester 8 | University of Moratuwa**

---

## 1. Approach and Architecture

We implemented the simulator as a single Python script (`main.py`) with no external dependencies beyond `matplotlib` for visualisation. The system is structured around a `Node` class that holds each node's position, energy, role (`leader`, `member`, or `isolated`), and cluster membership. The main simulation loop advances one tick at a time until no nodes remain.

**Cluster Formation (Initial)**
Nodes are sorted in descending order of energy. The highest-energy node that has not yet been assigned picks the role of leader and absorbs all unassigned nodes within Euclidean radius 20 into its cluster. This greedy strategy ensures the most capable nodes take leadership from the start, directly maximising system lifetime. Nodes with no reachable neighbours are marked `isolated` and do not pay message costs.

**Energy Model**
- Every node pays **1 energy/tick** (idle cost).
- Every leader pays an additional **2 energy/tick** (one broadcast message per tick to maintain cluster heartbeat).
- Members and isolated nodes pay no message cost.

This model means leaders die faster than members, which is intentional — it triggers re-elections that cycle the leadership burden across the cluster and extends overall system lifetime.

**Leader Re-election**
When a leader dies, the surviving members of its cluster hold an election:
1. The new leader is chosen deterministically: the member with the highest remaining energy (lowest ID as tiebreak) wins — no energy is spent on the decision.
2. Only nodes within radius 20 of the new leader pay a `MESSAGE_COST` (2 energy) for the announcement/acknowledgement exchange.
3. Nodes outside the new leader's radius become `isolated` without being penalised.

This two-step process ensures the election cost is proportional to actual participation.

**Isolated Node Re-integration**
After every tick, isolated nodes are checked against all active leaders. If a node falls within radius 20 of any leader, it joins that cluster as a member. This allows nodes that became isolated during a re-election to quickly re-join a group.

---

## 2. Messaging Strategy

To maximise system lifetime, we deliberately minimise message traffic:
- Members and isolated nodes **do not transmit**. They only pay the unavoidable idle cost.
- Leaders send exactly **one broadcast per tick** (cluster heartbeat), costing 2 energy.
- During a leader re-election, only the nodes that form the new cluster exchange one message each.

The rationale is simple: the bottleneck for system lifetime is energy. Every unnecessary message shortens a node's life. By restricting transmission to leaders only, non-leader nodes survive far longer, giving the cluster a larger pool of candidates for future re-elections.

---

## 3. Challenges and Resolutions

**Challenge 1 — Election fairness and energy deduction order**
Initially, all surviving cluster members were charged `MESSAGE_COST` before the election winner was determined. This meant a node might pay for an election it was too far from the new leader to participate in, or that the would-be leader could die from the election cost before being confirmed. We resolved this by electing the winner first (based on current energy, before any deduction), then charging only the nodes that are actually within radius of the new leader.

**Challenge 2 — Election casualties crashing the loop**
If a node's energy is just enough to survive the tick but not the subsequent election cost, it dies mid-tick. We handle this by collecting "election casualties" immediately after the election step and removing them from the active node list before the next tick begins.

**Challenge 3 — Logging dead nodes**
When a node dies, its energy can go slightly negative (e.g., a leader with 1 energy remaining loses 3 total in a tick: 1 idle + 2 message). We clamp the logged energy to 0 in the CSV output so the records stay semantically correct.

---

## 4. Output

For each run the simulator produces three files inside `outputs/outputs_of_{input_name}/`:

| File | Contents |
|---|---|
| `simulation_log.csv` | Every node's status (energy, role, cluster) at every tick |
| `events_log.txt` | Human-readable record of deaths, elections, and re-integrations |
| `energy_plot.png` | Line chart of each node's energy over time |

Console output mirrors the per-tick state for quick inspection.
