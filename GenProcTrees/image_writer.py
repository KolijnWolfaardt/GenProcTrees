import math
import time

from PIL import Image, ImageDraw


def write_image_from_tree(file_name, tree):
    # Draw the tree to a png file, to quickly check the output
    img = Image.new('RGB', (1024, 1024), (130, 179, 246))  # create a new blue image
    pixels = img.load()  # create the pixel map
    draw = ImageDraw.Draw(img)

    half_point_x = 512
    half_point_y = 768

    draw_scale = 500

    for _, branch in tree.branches.items():

        thickness = int(math.log(branch.thickness))

        if thickness < 1:
            thickness = 1
        draw.line((branch.start_pos[0] * draw_scale + half_point_x, half_point_y - branch.start_pos[2] * draw_scale,
                   branch.end_pos[0] * draw_scale + half_point_x, half_point_y - branch.end_pos[2] * draw_scale),
                  width=thickness, fill=(170, 75, 57))

    for leaf in tree.leaves:
        color = (58, 113, 19)
        if leaf.reached:
            color = (30, 30, 30)

        pixels[leaf.position[0] * draw_scale + half_point_x, half_point_y - leaf.position[2] * draw_scale] = color
        pixels[leaf.position[0] * draw_scale + half_point_x, half_point_y - leaf.position[2] * draw_scale + 1] = color
        pixels[leaf.position[0] * draw_scale + half_point_x + 1, half_point_y - leaf.position[2] * draw_scale] = color
        pixels[leaf.position[0] * draw_scale + half_point_x + 1, half_point_y - leaf.position[2] * draw_scale + 1] = color

    timestamp = int(time.time())
    if file_name is None:
        file_name = "tree_{}_{}".format(timestamp, tree.iterations)
    img.save(file_name, "PNG")
