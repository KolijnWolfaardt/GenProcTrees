import random

from .leaf import Leaf
from .branch import Branch

import numpy as np
from scipy import spatial


def branch_is_unique(new_branch, old_branch):
    is_unique = True
    for child_branch in old_branch.list_of_children:
        is_unique = is_unique and not np.allclose(new_branch.end_pos, child_branch.end_pos, rtol=1e-07)

    return is_unique


class Tree(object):

    def __init__(self, parameters=None):
        if parameters is None:
            self.parameters = {}
        else:
            self.parameters = parameters

        self.branches = {}
        self.leaves = []

        self.root_branch = None

        self.iterations = 0

    def to_geometry(self, method):
        """Convert the tree structure to geometry"""
        pass

    def generate_leaves(self, number_of_leaves: int, leaf_start: float, limit_2d: bool=False):
        """

        :param number_of_leaves: The number of leaves to generate
        :param leaf_start: The x height from which leaves can start
        :param limit_2d: True if leaves should only be generated on a 2d plane
        :return: A List of leaf objects
        """
        self.leaves = []
        for i in range(number_of_leaves):
            x = random.gauss(0.0, 0.2)
            if limit_2d:
                y = 0
            else:
                y = random.gauss(0.0, 0.2)
            z = ((1.0 - leaf_start) * random.random() + leaf_start)

            self.leaves.append(Leaf(x, y, z))

    def create_starter_branch(self, branch_length: float, leaf_start: float):
        """
        Manually add branches from the bottom to where the leaves start

        :param branch_length:
        :param leaf_start:
        :return:
        """

        dict_of_branches = {}

        # The root branch always starts at 0,0,0
        root_branch = Branch(end_z=leaf_start)
        dict_of_branches[root_branch.uid] = root_branch
        previous_branch = root_branch

        # The first branch (trunk of the tree) may need to be split into multiple segments
        # to make texture mapping easier

        # num_to_add = int((leaf_start - 0.0005) / branch_length)
        #
        # for num in range(num_to_add):
        #     new_branch = Branch(start_z=num * branch_length, end_z=(num + 1) * branch_length)
        #     new_branch.set_parent_branch(previous_branch)
        #     dict_of_branches[new_branch.uid] = new_branch
        #     previous_branch = new_branch

        self.root_branch = root_branch
        self.branches = dict_of_branches

    def iteratively_add_branches(self, max_distance, min_distance, turn_factor, branch_length):

        added_branches = 0

        # Convert all branch end points to a kd tree, so that we can quickly
        # search through them
        branch_end_tree = np.zeros((3, len(self.branches)))

        # Make a copy of all the branches, convert their positions to an array, put it in the kd tree.
        # When the kd tree returns the index, look it up in the copy of all branches
        temp_branches_copy = list(self.branches.values())

        for num, branch in enumerate(temp_branches_copy):
            branch_end_tree[:, num] = branch.end_pos

        branch_end_tree = spatial.KDTree(branch_end_tree.T, leafsize=5)

        # Update the distances to all the leaves
        for leaf in self.leaves:
            if not leaf.reached:
                distance, branch_number = branch_end_tree.query(leaf.position, k=1)
                branch_index = temp_branches_copy[branch_number].uid

                # This leaf is too far away
                if distance > max_distance:
                    continue

                # The leaf is very close
                if distance < min_distance:
                    leaf.set_branch(self.branches[branch_index])
                    continue

                # The leaf is close enough
                if distance < leaf.closest_distance:
                    leaf.closest_distance = distance
                    leaf.closest_branch = branch_index

        # For all the branches that are close to leaves, update how much the leaves "pull" them
        for leaf in self.leaves:
            # calculate the angle
            if leaf.closest_branch != -1:
                self.branches[leaf.closest_branch].grow_towards(leaf)

        # For all the branches that were updated, grow them
        for old_branch in list(self.branches.values()):

            if old_branch.growcount > 0:
                new_branch = Branch.grow_from(old_branch, turn_factor, branch_length)

                if branch_is_unique(new_branch, old_branch):
                    # If the branch is new, add it to our structure

                    new_branch.set_parent_branch(old_branch)
                    self.branches[new_branch.uid] = new_branch
                    new_branch.grow_to_root()
                    added_branches += 1

            old_branch.reset_growing()

        for leaf in self.leaves:
            leaf.reset_closest()

        self.iterations += 1

        return added_branches

    def trim_short_branches(self):

        dead_end_branches = []

        for branch_id, branch in self.branches.items():
            if len(branch.list_of_children) == 0 and branch.owns_leaf is False:
                dead_end_branches.append(branch_id)
        counts = {}

        # For each dead end branch, count the number of steps to the root branch
        for branch_id in dead_end_branches:
            branch = self.branches[branch_id]
            reached_end = False
            counts[branch_id] = 0

            while not reached_end:

                if branch.uid not in counts:
                    counts[branch.uid] = 0
                counts[branch.uid] = counts[branch.uid] + 1

                if branch.parent_branch is None:
                    reached_end = True
                else:
                    branch = branch.parent_branch

        list_of_deletions = []

        # for each of the dead end branches, iterate back up until a sibling branch with higher count is found
        for branch_id in dead_end_branches:

            current_branch = self.branches[branch_id]
            reached_join = False

            # Special case for accidentally having the parent branch
            if current_branch.parent_branch is None:
                continue

            # three hard things in programming....
            the_list = []
            while not reached_join:
                next_branch = current_branch.parent_branch
                the_list.append(current_branch.uid)

                # If there is a large difference between branch counts
                if counts[next_branch.uid] - counts[current_branch.uid] > 4:
                    # We have reached where this branch joins the next one.
                    reached_join = True

                    # If the branch we came from is too short, delete all of them
                    if counts[current_branch.uid] <= 2:
                        # mark all the currentBranches for deletion
                        for a in the_list:
                            list_of_deletions.append(a)

                # We have accidentally reached the root node?
                if self.branches[next_branch.uid].parent_branch is None:
                    reached_join = True

                current_branch = next_branch

        # print("Deleting {} branches, because they are too short".format(len(list_of_deletions)))
        for branch_id in set(list_of_deletions):
            del self.branches[branch_id]
