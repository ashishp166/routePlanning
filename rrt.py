import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

import env, plotting, utils


class Node:
    def __init__(self, n):
        self.x = n[0]
        self.y = n[1]
        self.parent = None


class Rrt:
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


def main():
    x_start = get_coords_from_figure(0)
    print(x_start)
    x_goal = get_coords_from_figure(1)
    print(x_goal)

    rrt = Rrt(x_start, x_goal, 0.5, 0.05, 100000)
    path = rrt.planning()

    if path:
        rrt.plotting.animation(rrt.vertex, path, "RRT", True)
    else:
        print("No Path Found or One Coordinate placed on Obstacle!")


def get_start():
    startX = int(input("What are your start x coordinate?"))
    startY = int(input("What are your start y coordinate? "))
    return startX, startY


def get_goal():
    goalX = int(input("What are your goal x coordinates?"))
    goalY = int(input("What are your goal y coordinates?"))
    return goalX, goalY

coords = []
def get_coords_from_figure(i):
    inputx = 0
    inputy = 0
    def onclick(event):
        global inputx
        global inputy
        print("hi")
        global coords
        inputx = round(event.xdata)
        inputy = round(event.ydata)
        coords.append((inputx, inputy))
    fig, ax = plt.subplots()
    ax.set_xlim([0, 50])
    ax.set_ylim([0, 30])
    # ax.axvline(x=0.5)      # Placeholder data
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show(block=True)
    
    return coords[i]
    # return (ev.x, ev.y) if ev is not None else None


if __name__ == '__main__':
    main()
