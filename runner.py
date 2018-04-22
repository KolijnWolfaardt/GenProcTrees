import random

import GenProcTrees as gpt

# This file demonstrates some of the abilities of this generation script.
# It generates a few trees, saves some to images, and two to .obj files
if __name__ == "__main__":

    random.seed(1)

    # Generate trees with long, lengthy branches that don't bend much
    for i in range(0, 5):
        print("Generating lengthy tree {}".format(i))

        tree = gpt.generate_tree({'branch_length': 0.08,
                                  'turn_factor': 0.1,
                                  'leaf_start': 0.1,
                                  'number_of_leaves': 200})
        gpt.write_image_from_tree("lengthy_{}.png".format(i), tree)

        # Pick one of the iterations, write it as a object
        if i == 3:
            gpt.write_geometry_from_tree("lengthy_tree.obj", tree, leaves=False)

    # Generate some wiry trees. These short branches turn fast, and grow after each leaf
    for i in range(0, 5):
        print("Generating wiry tree {}".format(i))

        tree = gpt.generate_tree({'min_distance': 0.02,
                                  'max_distance': 0.40,
                                  'branch_length': 0.04,
                                  'turn_factor': 0.60,
                                  'leaf_start': 0.1,
                                  'number_of_leaves': 400})
        gpt.write_image_from_tree("wiry_{}.png".format(i), tree)

        if i == 0:
            gpt.write_geometry_from_tree("wiry_tree.obj", tree, leaves=False)

    # And some more weird trees
    for i in range(0, 5):
        print("Generating weird tree {}".format(i))

        # The leaves start high, the branches can turn a lot, but they are too long to go more than once
        tree = gpt.generate_tree({'min_distance': 0.02,
                                  'max_distance': 0.19,
                                  'branch_length': 0.15,
                                  'turn_factor': 0.9,
                                  'leaf_start': 0.85,
                                  'number_of_leaves': 50})
        gpt.write_image_from_tree("weird_{}.png".format(i), tree)

    # Generate a 2d tree
    tree = gpt.generate_tree({'min_distance': 0.048,
                              'max_distance': 0.4,
                              'branch_length': 0.03,
                              'turn_factor': 0.35,
                              'leaf_start': 0.30,
                              'number_of_leaves': 600,
                              'limit_2d': True})
    gpt.write_image_from_tree("2d_tree.png", tree)
    gpt.write_geometry_from_tree("2d_tree.obj", tree, leaves=False)
