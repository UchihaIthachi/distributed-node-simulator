from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Node:
    id: int
    x: float
    y: float
    energy: int
    role: str = "unassigned"   # "leader", "member", "isolated"
    cluster_id: Optional[int] = None
    energy_history: list = field(default_factory=list)

    def is_alive(self):
        return self.energy > 0

    def record_energy(self):
        self.energy_history.append(self.energy)

    def __repr__(self):
        return (f"Node(id={self.id}, pos=({self.x},{self.y}), "
                f"energy={self.energy}, role={self.role}, cluster={self.cluster_id})")
