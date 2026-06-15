import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import tempfile
from parser import parse_input


def test_basic_parse():
    content = "(2,3,345),(12,45,234),(35,45,533)"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        path = f.name

    nodes = parse_input(path)
    assert len(nodes) == 3
    assert nodes[0].x == 2 and nodes[0].y == 3 and nodes[0].energy == 345
    assert nodes[1].id == 2
    assert nodes[2].energy == 533
    os.unlink(path)

def test_spaces_in_triplets():
    content = "(2, 3, 345), (12, 45, 234)"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        path = f.name

    nodes = parse_input(path)
    assert len(nodes) == 2
    os.unlink(path)


if __name__ == "__main__":
    test_basic_parse()
    test_spaces_in_triplets()
    print("All parser tests passed")
