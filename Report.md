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

**Leader Re-election (two-phase)**
When a leader dies, the surviving members of its cluster hold an election:

1. **Provisional selection** — the member with the highest remaining energy (lowest ID as tiebreak) is chosen as the provisional winner. No energy is spent at this stage, so the selection is based on the most up-to-date state.
2. **Radius partition** — survivors are split into those within radius 20 of the provisional winner (`in_radius`) and those outside (`out_of_radius`). Only `in_radius` nodes pay `MESSAGE_COST` (2 energy) for the announcement/acknowledgement exchange. Nodes outside radius become `isolated` without being penalised, since they did not participate in the new cluster's formation.
3. **Casualty check** — after the energy deduction, any `in_radius` node whose energy drops to zero becomes an election casualty. The confirmed leader is then re-elected from the surviving `in_radius` members, handling the edge case where the provisional winner itself dies from the election cost.
4. **Role assignment** — surviving `in_radius` members are assigned `cluster_id = confirmed_leader.id`. The confirmed leader's death, if it occurs, is reported by the main simulation loop (not duplicated in the election event).

**Isolated Node Re-integration**
After every tick, isolated nodes are checked against all active leaders. If a node falls within radius 20 of any leader, it joins that cluster as a member. This allows nodes that became isolated during a re-election to quickly re-join a group.

---

## 2. Messaging Strategy

To maximise system lifetime, we deliberately minimise message traffic:
- Members and isolated nodes **do not transmit**. They only pay the unavoidable idle cost.
- Leaders send exactly **one broadcast per tick** (cluster heartbeat), costing 2 energy.
- During a leader re-election, only the nodes that form the new cluster (within radius of the confirmed leader) exchange one message each. Nodes outside radius are silently made isolated with no energy penalty.

The rationale is simple: the bottleneck for system lifetime is energy. Every unnecessary message shortens a node's life. By restricting transmission to leaders only, non-leader nodes survive far longer, giving the cluster a larger pool of candidates for future re-elections.

---

## 3. Challenges and Resolutions

**Challenge 1 — Election fairness and energy deduction order**
Initially, all surviving cluster members were charged `MESSAGE_COST` before the election winner was determined. This meant a node might pay for an election it was too far from the new leader to participate in. We resolved this with the two-phase approach: select the provisional winner first (no cost), partition by radius, then charge only the participants. The confirmed leader is determined after the cost is applied, handling the case where the provisional winner dies from the election itself.

**Challenge 2 — Election casualties crashing the loop**
If a node's energy is just enough to survive the tick but not the subsequent election cost, it dies mid-tick. We handle this by collecting "election casualties" immediately after the election step and removing them from the active node list before the next tick begins.

**Challenge 3 — Logging dead nodes accurately**
When a node dies, its energy can go slightly negative (e.g., a leader with 1 energy remaining loses 3 total in a tick: 1 idle + 2 message). We clamp the logged energy to 0 in the CSV output so the records stay semantically correct. Death events are reported exactly once in `events_log.txt` by the main simulation loop, even when the death occurs during an election.

---

## 4. Output

For each run the simulator produces three files inside `outputs/outputs_of_{input_name}/`:

| File | Contents |
|---|---|
| `simulation_log.csv` | Every node's status (energy, role, cluster) at every tick |
| `events_log.txt` | Human-readable record of deaths, elections, and re-integrations |
| `energy_plot.png` | Line chart of each node's energy over time |

Console output mirrors the per-tick state for quick inspection.
