from .tree import Tree
from .image_writer import write_image_from_tree


def generate_tree(parameters, animate=False):

    para = {'min_distance': 0.048,
            'max_distance': 0.2,
            'branch_length': 0.015,
            'leaf_start': 0.2,
            'turn_factor': 0.8,
            'number_of_leaves': 500,
            'limit_2d': False,
            'max_iterations': 50}

    # Update and overwrite any parameters
    para.update(parameters)

    tree = Tree(para)
    tree.generate_leaves(para['number_of_leaves'], para['leaf_start'], para['limit_2d'])
    tree.create_starter_branch(para['branch_length'], para['leaf_start'])

    if animate:
        write_image_from_tree(None, tree)

    counter = 0
    while counter < para['max_iterations']:

        added_branches = tree.iteratively_add_branches(para['max_distance'], para['min_distance'],
                                                       para['turn_factor'], para['branch_length'])
        counter += 1
        if animate:
            write_image_from_tree(None, tree)

        if added_branches == 0:
            break
    if counter == 50:
        print("Warning: stop loop due to excessive iterations")

    # tree.trim_short_branches()
    if animate:
        write_image_from_tree(None, tree)
    return tree
