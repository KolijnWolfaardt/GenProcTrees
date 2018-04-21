import copy
import math
import time

import numpy as np

    
def calculate_q(direction_vector, normal_vector):

    norm_dir = direction_vector / np.linalg.norm(direction_vector)
    dot_product = np.inner(norm_dir, normal_vector)
    rotation_angle = math.acos(dot_product / (np.linalg.norm(norm_dir) ** 2))
    cross_product = np.cross(norm_dir, normal_vector)

    a1 = cross_product[0]
    a2 = -cross_product[1]
    a3 = cross_product[2]

    a_mat = np.array([[0, -a3, a2], [a3, 0, a1], [-a2, -a1, 0]])
    a_mat_squared = np.dot(a_mat, a_mat)

    q_mat = np.identity(3) + a_mat * math.sin(rotation_angle) + a_mat_squared * (1 - math.cos(rotation_angle))

    return q_mat


def write_circle_points(branch, obj_file, circle_points, circle_dim, scale):
    """
    Write all the circle vertices for a given branch's start_position
    :param branch: Branch object
    :param obj_file: Open File pointer
    :param circle_points: Number of points in the circle
    :param circle_dim: Radius of the circle
    :param scale: Scale of the entire tree
    :return: None
    """
    q_mat = calculate_q(branch.end_pos - branch.start_pos, np.array([0, 0, 1]))

    for point in range(circle_points):
        thickness = int(math.log(branch.thickness))
        if thickness < 1:
            thickness = 1

        angle = float(point) / float(circle_points) * 2 * math.pi % (2 * math.pi)
        x_point = math.cos(angle) * circle_dim * thickness
        y_point = math.sin(angle) * circle_dim * thickness

        g = np.array([x_point, y_point, 0])
        g = np.dot(q_mat, g)
        obj_file.write("v {:.8} {:.8} {:.8}\n".format((g[0] + branch.start_pos[0]) * scale,
                                                      (g[2] + branch.start_pos[2]) * scale,
                                                      (g[1] + branch.start_pos[1]) * scale))


def write_end_point(branch, obj_file, circle_points, circle_dim, scale):
    """
    Rather than write a circle for the end, we write vertices on a point
    :param branch:
    :param obj_file:
    :param circle_points:
    :param circle_dim:
    :param scale:
    :return:
    """
    for point in range(circle_points):
        obj_file.write(
            "v {:.8} {:.8} {:.8}\n".format(branch.end_pos[0] * scale,
                                           branch.end_pos[2] * scale,
                                           branch.end_pos[1] * scale))


def write_geometry_from_tree(file_name: str, tree, texture_coords=True, leaves=True):

    if file_name is None:
        file_name = "tree_{}.obj".format(int(time.time()))
    
    obj_file = open(file_name, "w")
    obj_file.write("o tree_{}\n".format(0))
    obj_file.write("\n")

    texture_scale = 0.2
    circle_dim = 0.003
    circle_points = 32
    scale = 1

    first_branch = tree.root_branch

    write_circle_points(first_branch, obj_file, circle_points, circle_dim, scale)

    # The write counter counts the index for the branch's start point circle. The root branch
    # will have an index of 0.This number is  multiplied by the number of points in a circle to get
    # the actual index of the vertices.
    # Eg: if a branch has an index of 6, and is connected to a branch with index 2, the vertices
    # for the first branch are at 6 * circle_points to (6+1) * circle_points, and need to be
    # connected to the vertices of the second branch at 2 * circle_points to (2+1) * circle_points

    write_counter = 1
    vertex_index = {}

    # Write the vertices
    for branch_id, branch in tree.branches.items():

        vertex_index[branch_id] = write_counter
        write_counter += 1

        if len(branch.list_of_children) > 0:
            write_circle_points(branch, obj_file, circle_points, circle_dim, scale)
        else:
            write_end_point(branch, obj_file, circle_points, circle_dim, scale)

    if texture_coords:
        # Write the texture coordinates
        for point in range(circle_points):
            obj_file.write("vt {:.8} {:.8}\n".format(float(point) / float(circle_points), 0.0))

        for branch_id, branch in tree.branches.items():
            for point in range(circle_points):
                obj_file.write("vt {:.8} {:.8}\n".format(float(point) / float(circle_points),
                                                         texture_scale * (branch.distance_to_root + 1)))

    # Write the faces
    for branch_id, branch in tree.branches.items():
        w_code_one = vertex_index[branch.uid]

        if branch.parent_branch is None:
            w_code_two = 0
        else:
            w_code_two = vertex_index[branch.parent_branch.uid]

        for point in range(circle_points):
            p1 = w_code_one * circle_points + point % circle_points + 1
            p2 = w_code_one * circle_points + (1 + point) % circle_points + 1
            p3 = w_code_two * circle_points + point % circle_points + 1
            p4 = w_code_two * circle_points + (1 + point) % circle_points + 1

            obj_file.write("f {}/{} {}/{} {}/{}\n".format(p1, p1, p2, p2, p3, p3))
            obj_file.write("f {}/{} {}/{} {}/{}\n".format(p2, p2, p4, p4, p3, p3))

    # Now write the leaves. They are written as separate objects in the file. For now the leaves
    # are just squares

    if leaves:
        obj_file.write("o leaves_{}\n".format(0))

        big_offset = (len(tree.branches) + 1) * circle_points

        leaf_shape = [np.array([-1, 1, 0]),
                      np.array([1, 1, 0]),
                      np.array([1, -1, 0]),
                      np.array([-1, -1, 0])]

        # Write the vertices
        for leaf in tree.leaves:
            if leaf.reached:

                # Get the direction vector to the leaf
                branch = tree.branches[leaf.assigned_to_branch]

                dir_vector = branch.end_pos - leaf.position
                dir_vector[2] = 0

                # Calculate the vector around which the squre will be rotated, and normalise
                z_vector = branch.end_pos - leaf.position
                z_vector[0] = math.sqrt(z_vector[0] ** 2 + z_vector[1] ** 2)
                z_vector[1] = 0

                length_scale = math.sqrt((dir_vector[1]) ** 2 + (dir_vector[0]) ** 2) * 0.2

                plane_rotation = calculate_q(dir_vector, np.array([1, 0, 0]))
                z_rotation = calculate_q(z_vector, np.array([1, 0, 0]))

                # Make a copy of the leafDefinition
                copy_positions = copy.copy(leaf_shape)

                for point in copy_positions:
                    point = point * length_scale

                    rot_points = np.dot(z_rotation, point)
                    rot_points = np.dot(plane_rotation, rot_points)

                    obj_file.write(
                        "v {:.8} {:.8} {:.8}\n".format((rot_points[0] + branch.end_pos[0]) * scale,
                                                       (rot_points[2] + branch.end_pos[2]) * scale,
                                                       (rot_points[1] + branch.end_pos[1]) * scale))

        # Write the leaf's faces
        increment = 0
        for leaf in tree.leaves:
            if leaf.reached:
                offset = big_offset + increment * len(leaf_shape)
                obj_file.write("f {} {} {}\n".format(offset + 1, offset + 2, offset + 3))
                obj_file.write("f {} {} {}\n".format(offset + 1, offset + 3, offset + 4))
                increment += 1

    obj_file.close()
