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

## Outputs

Running the above command will create a new folder inside the `outputs/` directory named after the input file (eg: `outputs/outputs_of_input1/`) containing the following files:
- `simulation_log.csv`: A log of every node's status (energy, role, cluster) at every tick. Energy is clamped to 0 for dead nodes.
- `events_log.txt`: A log of all major actions, node deaths, leader elections, radius evictions, and re-integrations.
- `energy_plot.png`: A graph showing the energy drop over time for all nodes.

Actions are also printed to the console while it runs.

## Inputs

The input file should have points like this: `(x, y, energy), (x, y, energy)`. `inputs/` directory contains the inputs used for testing.

