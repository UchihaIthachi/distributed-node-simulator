import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from clustering import euclidean
from models import Node


def make(id, x, y):
    return Node(id=id, x=x, y=y, energy=100)


def test_same_point():
    a = make(1, 0, 0)
    assert euclidean(a, a) == 0

def test_known_distance():
    a = make(1, 2, 3)
    b = make(2, 4, 5)
    assert abs(euclidean(a, b) - 2.828) < 0.01

def test_radius_boundary():
    a = make(1, 0, 0)
    b = make(2, 20, 0)   # exactly 20 — should be within radius
    assert euclidean(a, b) == 20.0

def test_outside_radius():
    a = make(1, 2, 3)
    b = make(2, 12, 45)  # Node 1 and 2 from input — should be > 20
    assert euclidean(a, b) > 20


if __name__ == "__main__":
    test_same_point()
    test_known_distance()
    test_radius_boundary()
    test_outside_radius()
    print("All distance tests passed")
