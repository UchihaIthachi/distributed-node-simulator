# Distributed Node Simulator
CS4262 Distributed Systems — Programming Assignment

Simulates an energy-constrained distributed node network with clustering,
leader election, and tick-by-tick energy drain logging.

---

## How to run

```bash
# Install dependencies (only matplotlib, optional for plotting)
pip install -r requirements.txt

# Run the simulator
python src/main.py input/input1.txt
```

Output files are written to `output/`:
- `simulation_log.csv` — full tick-by-tick state of every node
- `energy_plot.png` — energy over time per node (requires matplotlib)

To run with a different input file:
```bash
python src/main.py input/your_input.txt
```

---

## Input format

A single line of comma-separated triplets:
```
(x,y,energy),(x,y,energy),...
```
Example:
```
(2,3,345),(12,45,234),(35,45,533)
```

---

## Running tests

```bash
python tests/test_distance.py
python tests/test_parser.py
python tests/test_clustering.py
```

---

## File structure

```
distributed-node-simulator/
  README.md
  requirements.txt
  input/
    input1.txt          # sample input (9 nodes)
  output/
    simulation_log.csv  # generated on run
    energy_plot.png     # generated on run
  src/
    main.py             # entry point
    models.py           # Node dataclass
    parser.py           # reads input file
    clustering.py       # HEED-inspired cluster formation
    simulation.py       # tick loop
    logger.py           # CSV and console output
    visualization.py    # energy plot
  tests/
    test_distance.py
    test_parser.py
    test_clustering.py
```

---

## Assumptions

- **Idle cost**: every node loses 1 energy per tick just for being alive.
- **Transmission cost**: each leader sends exactly 1 message per tick and loses 2 additional energy.
- **Members and isolated nodes** send no messages in normal operation, so they only pay the idle cost.
- **Isolated nodes** are nodes with no neighbour within radius 20. They are kept isolated (not made leaders) to avoid unnecessary transmission cost and extend system lifetime.
- **Leader re-election**: when a leader dies, the surviving cluster member with the highest energy is elected. Ties are broken by smaller node id. Each survivor pays 2 energy for the election broadcast.
- **Election casualties**: if a survivor's energy drops to 0 or below after the election cost, it is removed immediately in the same tick.
- **Node removal**: a node is removed at the end of the tick in which its energy reaches 0 or below.
- **Cluster radius**: Euclidean distance, strict `<= 20`.

---

## Sample output (first few ticks)

```
Loaded 9 nodes from input/input1.txt

Initial cluster assignment:
  Node  1 | energy= 345 | leader    | cluster=1
  Node  2 | energy= 234 | member    | cluster=9
  Node  3 | energy= 533 | leader    | cluster=3
  Node  4 | energy= 234 | member    | cluster=9
  Node  5 | energy=  50 | member    | cluster=1
  Node  6 | energy=  98 | isolated  | cluster=6
  Node  7 | energy= 144 | isolated  | cluster=7
  Node  8 | energy= 233 | member    | cluster=3
  Node  9 | energy= 235 | leader    | cluster=9

── Tick 1 ──────────────────────────────
  Node  1 | energy= 342 | leader    | cluster=1
  ...
```
