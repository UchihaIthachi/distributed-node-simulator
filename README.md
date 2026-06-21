# CS42623 Distributed Systems Project: 210167E-210339J

## How to run

First, install the requirements:
```bash
pip install -r requirements.txt
```

Then run the simulation with the input file:
```bash
python main.py [path_to_input_file]
```
eg:
```bash
python main.py inputs/input1.txt
```

This will create a new folder inside the `outputs/` directory named after the input file (eg: `outputs/outputs_of_input1/`) containing the following files:
- `simulation_log.csv`: A log of every node's status (energy, role, cluster) at every tick. Energy is clamped to 0 for dead nodes.
- `events_log.txt`: A log of all major actions, node deaths, leader elections, radius evictions, and re-integrations.
- `energy_plot.png`: A graph showing the energy drop over time for all nodes.

Actions are also printed to the console while it runs.

## Inputs

The input file should have points like this: `(x, y, energy), (x, y, energy)`. `inputs/` directory contains the inputs.

## Energy model

| Event | Cost |
|---|---|
| Being in the system | 1 energy / tick |
| Leader heartbeat broadcast | +2 energy / tick (leaders only) |
| Election message (new cluster members) | 2 energy (once, on election) |

Members and isolated nodes transmit nothing, so they only pay the idle cost of 1/tick.

## Leader election

When a leader dies, a two-phase election runs among its former cluster members:
1. The provisional winner (highest energy, lowest ID as tiebreak) is selected at no cost.
2. Only nodes within radius 20 of the provisional winner pay the election message cost (2 energy). Nodes outside radius silently become isolated.
3. The confirmed leader is re-elected from survivors after the cost is applied, in case the provisional winner itself died.
