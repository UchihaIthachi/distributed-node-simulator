import math


RADIUS = 20


def euclidean(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def form_clusters(nodes):
    sorted_nodes = sorted(nodes, key=lambda n: (-n.energy, n.id))
    assigned = set()

    for node in sorted_nodes:
        if node.id in assigned:
            continue

        neighbours = [
            b for b in nodes
            if b.id != node.id
            and b.id not in assigned
            and euclidean(node, b) <= RADIUS
        ]

        if neighbours:
            node.role = "leader"
            node.cluster_id = node.id
            assigned.add(node.id)

            for member in neighbours:
                member.role = "member"
                member.cluster_id = node.id
                assigned.add(member.id)
        else:
            node.role = "isolated"
            node.cluster_id = node.id
            assigned.add(node.id)

    return nodes
