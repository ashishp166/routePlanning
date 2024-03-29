import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

import env, plotting, utils

POINTS = 500 #number of initial points
NKNN = 10 # number of edges from node
MAX_EDGE_LENGTH = 35.0 # length of max edge length
MIN_X = 0 #settings in env
MIN_Y = 0 #settings in env
MAX_X = 50 #settings in env
MAX_Y = 30 #settings in env

class Node:
    def __init__(self, n):
        self.x = n[0]
        self.y = n[1]
        self.parent = None


class PRM:
    def __init__(self, s_start, s_goal, step_len, goal_sample_rate, iter_max):
        self.s_start = Node(s_start)
        self.s_goal = Node(s_goal)
        self.step_len = step_len
        self.goal_sample_rate = goal_sample_rate
        self.iter_max = iter_max
        self.vertex = [self.s_start]

        self.env = env.Env()
        self.plotting = plotting.Plotting(s_start, s_goal)
        self.utils = utils.Utils()

        self.x_range = self.env.x_range
        self.y_range = self.env.y_range
        self.obs_circle = self.env.obs_circle
        self.obs_rectangle = self.env.obs_rectangle
        self.obs_boundary = self.env.obs_boundary

    def planning(self):
        for i in range(self.iter_max):
            node_rand = self.generate_random_node(self.goal_sample_rate)
            node_near = self.nearest_neighbor(self.vertex, node_rand)
            node_new = self.new_state(node_near, node_rand)

            if node_new and not self.utils.is_collision(node_near, node_new):
                self.vertex.append(node_new)
                dist, _ = self.get_distance_and_angle(node_new, self.s_goal)

                if dist <= self.step_len and not self.utils.is_collision(node_new, self.s_goal):
                    self.new_state(node_new, self.s_goal)
                    return self.extract_path(node_new)

        return None

    def generate_random_node(self, goal_sample_rate):
        delta = self.utils.delta

        if np.random.random() > goal_sample_rate:
            return Node((np.random.uniform(self.x_range[0] + delta, self.x_range[1] - delta),
                         np.random.uniform(self.y_range[0] + delta, self.y_range[1] - delta)))

        return self.s_goal

    @staticmethod
    def nearest_neighbor(node_list, n):
        return node_list[int(np.argmin([math.hypot(nd.x - n.x, nd.y - n.y)
                                        for nd in node_list]))]

    def new_state(self, node_start, node_end):
        dist, theta = self.get_distance_and_angle(node_start, node_end)

        dist = min(self.step_len, dist)
        node_new = Node((node_start.x + dist * math.cos(theta),
                         node_start.y + dist * math.sin(theta)))
        node_new.parent = node_start

        return node_new

    def extract_path(self, node_end):
        path = [(self.s_goal.x, self.s_goal.y)]
        node_now = node_end

        while node_now.parent is not None:
            node_now = node_now.parent
            path.append((node_now.x, node_now.y))

        return path

    @staticmethod
    def get_distance_and_angle(node_start, node_end):
        dx = node_end.x - node_start.x
        dy = node_end.y - node_start.y
        return math.hypot(dx, dy), math.atan2(dy, dx)

def get_nodes(rng, x_start, x_goal):
    node_x = []
    node_y = []
    
    if rng is None:
        rng = np.random.default_rng() # set up random
    
    while len(node_x) <= POINTS:
        px = (rng.random() * (MAX_X - MIN_X)) + MIN_X
        py = (rng.random() * (MAX_Y - MIN_Y)) + MIN_Y

        #might have to add obstacle kd tree here to make sure point is not too close to obstacle
        util = utils.Utils()
        checker = [px, py]
        if not util.is_inside_obs(Node(checker)):
            node_x.append(px)
            node_y.append(py)
    node_x.append(x_start[0])
    node_y.append(x_start[1])
    node_x.append(x_goal[0])
    node_y.append(x_goal[1])

    return node_x, node_y

def find_paths(node_x, node_y):
    road = []
    num = len(node_x)
    kd = KDTree(np.vstack((node_x, node_y)).T)

    for(i, x, y) in zip(range(num), node_x, node_y):

        distance, index = kd.query([x, y], k=num)
        edges_index = []
        start = [x, y]
        for j in range(1, len(index)):
            end_x = node_x[index[j]]
            end_y = node_y[index[j]]

            util = utils.Utils()
            end = [end_x, end_y]
            if not util.is_collision(Node(start), Node(end)):
                edges_index.append(index[j])
            if len(edges_index) >= NKNN:
                break
        road.append(edges_index)
    plot(road, node_x, node_y)
    return road

def plot(road_map, sample_x, sample_y):  # pragma: no cover

    for i, _ in enumerate(road_map):
        for ii in range(len(road_map[i])):
            ind = road_map[i][ii]

            plt.plot([sample_x[i], sample_x[ind]],
                     [sample_y[i], sample_y[ind]], "-k")
    print("hi")
def main(rng = None):
    x_start = (2, 2)
    x_goal = (3, 3)
    #x_start = get_coords_from_figure()
    print(x_start)
    #x_goal = get_coords_from_figure()
    print(x_goal)
    node_x, node_y =  get_nodes(rng, x_start, x_goal)
    print(node_x)
    possible_roads = find_paths(node_x, node_y)
    print(possible_roads)
    #prm = PRM(x_start, x_goal, 0.5, 0.05, 10000)
    #path = rrt.planning()

    #if path:
        #rrt.plotting.animation(rrt.vertex, path, "RRT", True)
    #else:
        #print("No Path Found or One Coordinate placed on Obstacle!")

def get_start():
    startX = int(input("What are your start x coordinate?"))
    startY = int(input("What are your start y coordinate? "))
    return startX, startY

def get_goal():
    goalX = int(input("What are your goal x coordinates?"))
    goalY = int(input("What are your goal y coordinates?"))
    return goalX, goalY

def get_coords_from_figure():
    #ev = None
    #def onclick(event):
        #nonlocal ev
        #ev = event
    fig, ax = plt.subplots()
    ax.set_xlim([0,50])
    ax.set_ylim([0,30])
    #ax.axvline(x=0.5)      # Placeholder data
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show(block=True)
    return (ev.xdata, ev.ydata) if ev is not None else None
    # return (ev.x, ev.y) if ev is not None else None

if __name__ == '__main__':
    main()