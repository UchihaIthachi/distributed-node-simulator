# Distributed Node Simulator

This program simulates a group of nodes with limited energy. Nodes are grouped around leaders, and the simulation runs tick by tick until all nodes die. 

## How to run

First, install the requirements (for the plot graph):
```bash
pip install -r requirements.txt
```

Then run the simulation with the input file:
```bash
python main.py [path_to_input_file]
```
eg :
```bash
python main.py input/input1.txt
```

This will create a new folder inside the `output/` directory named after your input file (for example, `output/outputs_of_input1/`) containing the following files:
- `simulation_log.csv`: A log of every node's status at every tick.
- `energy_plot.png`: A graph showing the energy drop over time.
- `events_log.txt`: A log of all major actions (like nodes dying or new leaders being elected).

Actions are also printed to the console while it runs.

## Inputs
The input file should have points like this: `(x, y, energy), (x, y, energy)`. 
