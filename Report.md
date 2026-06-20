# Assignment Report

**Approach and Architecture**
We wrote a basic python simulation for the distributed nodes problem. We used a simple python class to store node properties like x, y, energy, and cluster id. The main simulation runs in a while loop that ticks forward as long as there are nodes alive.

For the grouping part, we used euclidean distance. The highest energy nodes are picked first, and any node within radius 20 becomes a member of that leader's group. If no one is within 20, the node stays isolated.

**Challenges Faced**
The biggest challenge was handling the re-election when a leader dies. The instructions say a new leader has to be elected from within the group. We made it so the surviving member with the highest energy takes over. However, initially the new leader would sometimes die instantly because the cost of sending the new leader message (2 energy) would drop their energy to 0. We resolved this by checking for these "election casualties" right after the election step in the same tick so the loop wouldn't crash.

**Messaging Strategy**
We kept the messaging strategy simple to maximize lifetime. Leaders send out 1 message per tick (costing 2 energy). Members and isolated nodes do not send messages, so they only lose the 1 idle energy per tick. This ensures they survive as long as possible. 
