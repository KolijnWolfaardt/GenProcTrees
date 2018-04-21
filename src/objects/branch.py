import uuid

import numpy as np


class Branch:
    markForDeletion = False
    writeCount = 0

    @classmethod
    def grow_from(cls, parent_branch, turn_factor=0.25, branch_length=0.1):
        new_branch = Branch()
        new_branch.start_pos = np.copy(parent_branch.end_pos)

        # Determine the direction from the parent_branch's parameters. The direction is a
        # weighted sum of the influence from the leaves, and the parent's direction
        average_influence = parent_branch.sum_of_leaf * float(1.0 / parent_branch.growcount)

        old_direction = parent_branch.end_pos - parent_branch.start_pos
        old_direction_norm = old_direction / np.linalg.norm(old_direction)

        new_direction = average_influence * turn_factor + old_direction_norm * (1 - turn_factor)

        new_branch.end_pos = new_direction * branch_length + parent_branch.end_pos

        return new_branch

    def __init__(self, start_x: float=0, start_y: float=0, start_z: float=0,
                 end_x: float=0, end_y: float=0, end_z: float=0):

        self.uid = str(uuid.uuid4())

        self.start_pos = np.array([start_x, start_y, start_z])
        self.end_pos = np.array([end_x, end_y, end_z])
        self.sum_of_leaf = np.zeros(3)
        self.growcount = 0
        self.thickness = 1

        self.parent_branch = None
        self.distance_to_root = 0

        self.list_of_children = []
        self.owns_leaf = False

        self.reset_growing()

    def grow_towards(self, leaf):
        dist = np.linalg.norm(leaf.position - self.end_pos)
        self.sum_of_leaf += (leaf.position - self.end_pos) / dist
        self.growcount += 1

    def reset_growing(self):
        self.sum_of_leaf = np.zeros(3)
        self.growcount = 0

    def set_parent_branch(self, parent_branch):
        self.parent_branch = parent_branch
        self.distance_to_root = parent_branch.distance_to_root + 1

        parent_branch.add_me_as_child(self)

    def add_me_as_child(self, child):
        self.list_of_children.append(child)

    def grow_to_root(self):
        next_branch = self
        while next_branch.parent_branch is not None:
            next_branch = next_branch.parent_branch
            next_branch.thickness += 1
