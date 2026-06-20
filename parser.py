import re
from models import Node


def parse_input(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    triplets = re.findall(r"\((\d+),\s*(\d+),\s*(\d+)\)", content)
    if not triplets:
        raise ValueError(f"No valid triplets found in {filepath}")

    nodes = []
    for i, (x, y, energy) in enumerate(triplets, start=1):
        nodes.append(Node(id=i, x=float(x), y=float(y), energy=int(energy)))

    return nodes
