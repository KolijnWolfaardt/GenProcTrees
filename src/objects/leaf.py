from .branch import Branch

import numpy as np


class Leaf(object):

    def __init__(self, x=0, y=0, z=0):

        self.position = np.array([x, y, z])

        self.closest_distance = 10000000
        self.closest_branch = -1

        self.reached = False

        self.assigned_to_branch = -1

    def set_branch(self, parent_branch: Branch):
        self.reached = True
        self.assigned_to_branch = parent_branch.uid
        parent_branch.owns_leaf = True

    def reset_closest(self):
        self.closest_distance = 10000000
        self.closest_branch = -1
