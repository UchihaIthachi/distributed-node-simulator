# Department of CSE - University of Moratuwa
## CS42623 Distributed Systems - 2021 Batch Semester 8
### Programming Assignment (Project)
**(Last Updated: 13 May 2026)**

Submission instructions are provided at the end of this document.

This is a 2-person group assignment, but you are free to do this as a single-member assignment.

**Important:** DO NOT host your code publicly on GitHub or other public places until evaluations are complete. You are free (and encouraged) to use Git or other version controlling systems privately.

---

### Goal
The goal of this programming assignment is to apply your understanding of distributed systems concepts. As this is a simulation, what is required is to show the outcome of each simulation step until the end of the simulation.

### Input
The input file has a list of triplets separated by commas. A triplet has three values separated by commas: two coordinates `x` and `y` indicating the initial position of a node, and the initial energy level of a node. 

*Eg.* `(2, 4, 560)` means the node coordinates are 2, 4 (x, y) and 560 is the energy level.

### What to do:
1. **Initiate the system** of nodes according to the input.
2. **Groups need to be formed** around a few leader nodes. A leader can group any number of nodes within a radius of 20 based on Euclidean distance. You may decide on the messaging strategy among nodes. One node cannot be in more than one group. You may also decide who is going to be the initial leaders.
3. You are required to **simulate the energy consumption** of the nodes. Just for being in the system, a node requires 1 unit of energy/unit time whereas for each message transmitted, it takes 2 units of energy from the transmitting node.
4. Nodes are **removed from the system** when their energy level becomes zero.
5. Whenever a leader dies, a **new leader has to be elected** from within the group.

At every time step, **log a record of the node system** indicating the actions taken, energy levels, leader, and group information.

You are free to make assumptions, decide on data structures and algorithms, and come up with a good visualization strategy for the system.

**The objective is to maximize the system's lifetime.** (Staying without dying)

---

### Evaluation:
You will need to submit a `.zip` archive named with the registration numbers of the team members eg: `210111X-210222Y.zip` to the Moodle submission link. The zip archive should include the following:

1. **The complete source code** with instructions to build the code and use the simulator written in a readme file.
2. **Few sample input files** (and their outputs) that you tested your code with.
3. **A small report** (max three A4 pages) about how you approached this task, the challenges you faced, and how you resolved them.

Department of CSE - University of Moratuwa

---

**Note:** You are free to use any programming language.

Good luck and have fun!

If you find any bug in the assignment or if you have any questions, please email: sunimal@cse.mrt.ac.lk