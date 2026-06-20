import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import Node
from clustering import form_clusters


def make(id, x, y, energy):
    return Node(id=id, x=x, y=y, energy=energy)


def test_leader_elected_for_close_nodes():
    # Two nodes within radius 20 — higher energy should be leader
    nodes = [make(1, 0, 0, 200), make(2, 5, 0, 100)]
    form_clusters(nodes)
    assert nodes[0].role == "leader"
    assert nodes[1].role == "member"
    assert nodes[1].cluster_id == nodes[0].id

def test_isolated_when_no_neighbours():
    # Two nodes far apart — both should be isolated
    nodes = [make(1, 0, 0, 100), make(2, 50, 50, 200)]
    form_clusters(nodes)
    for n in nodes:
        assert n.role == "isolated"

def test_no_double_assignment():
    # Three nodes in a line — middle should only join one cluster
    nodes = [make(1, 0, 0, 300), make(2, 15, 0, 200), make(3, 30, 0, 100)]
    form_clusters(nodes)
    roles = {n.id: n.role for n in nodes}
    cluster_ids = {n.id: n.cluster_id for n in nodes}
    # Node 2 should belong to exactly one cluster
    assert cluster_ids[2] in (cluster_ids[1], cluster_ids[3])


if __name__ == "__main__":
    test_leader_elected_for_close_nodes()
    test_isolated_when_no_neighbours()
    test_no_double_assignment()
    print("All clustering tests passed")
