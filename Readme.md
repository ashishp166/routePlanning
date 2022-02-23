PRM(Probabalistic Road Map):
    Algo:
        -Get start and goal Node
        -Randomly find nodes on the map
        -check for collision and call new nodes milestone
        -use kd tree on milestones to find the closest 5 nodes
            -only keep the paths which don't cause a collision
        -Find path from start to goal with all possible subpaths with djikstra
    



RRT:
    Cons of RRT:
    -Bias towards largest
    http://lavalle.pl/papers/LinLav04.pdf

RRT Extension:

bi-directional RRT:

multidirectional RRT:

RC-RRT:
