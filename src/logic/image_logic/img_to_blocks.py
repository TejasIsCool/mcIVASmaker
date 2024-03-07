import math
import mcschematic
import json
import functools
import numpy as np
from src.logic.image_logic.block_parser import block_parser
from PIL import Image, ImageFile
from src.path_manager.pather import resource_path
import os
from typing import TypedDict


class DetailsDict(TypedDict):
    side: str
    blocked_list: list
    mode: str
    color_set: str
    color_compare: str


ImageFile.LOAD_TRUNCATED_IMAGES = True

# TODO: ALTERNATE, A BIT DIFFERENT RENDERER
# TODO: INTERBLOCK PIXEL ACCOUNTER


# Loading the pre-generated blocks color
path = resource_path("./assets/blocks/all_blocks_textures/")
with open(resource_path("./assets/blocks/img_generator_code/out_all_colours.json"), "r") as f:
    blocks_data: list = list(json.load(f).items())

# Storing all the images in memory (as numpy arrays)
blocks_img_np = {}
for block in blocks_data:
    for block_side in block[1].keys():
        if block_side == "extra":
            pass
        else:
            img = Image.open(os.path.join(path, block[1][block_side]['file'])).convert("RGBA")
            # noinspection PyTypeChecker
            blocks_img_np[block[0] + block_side] = np.array(img)


def img_to_blocks(image: Image.Image, details: DetailsDict):
    side: str = details['side']
    blocked_list: list = details['blocked_list']
    mode: str = details['mode']
    color_set: str = details['color_set']
    color_compare: str = details['color_compare']
    # Storing the pixels data in numpy array as it is faster
    np_new_image = np.zeros(shape=(image.height * 16, image.width * 16, 4), dtype=np.uint8)

    # Filtering out the blocks, depending on how the user configured the options
    new_blocks_list = []
    if mode == "Whitelist":
        new_blocks_list = [selected_block for selected_block in blocks_data if selected_block[0] in blocked_list]
    elif mode == "Blacklist":
        new_blocks_list = [selected_block for selected_block in blocks_data if selected_block[0] not in blocked_list]
    else:
        new_blocks_list = blocks_data

    # If list is empty, we return
    if not new_blocks_list:
        yield Image.fromarray(np_new_image)
        return

    # This function is cached, to increase speed
    @functools.lru_cache(maxsize=100000)
    def pix_to_block(pix, distance_function: callable, avg_color_set: str):
        # The below statement becomes a list, with all the differences between the current pixel, and all the blocks
        all_differences = [
            (
                (
                    distance_function(pix, block_val[1][side]['color'][avg_color_set])
                ) if (side in block_val[1]) else math.inf
            ) for block_val in new_blocks_list
        ]
        # Getting the lowest different block
        block_index = all_differences.index(min(all_differences))
        block_img = blocks_img_np[new_blocks_list[block_index][0] + side]
        return block_img

    for x in range(0, image.width):
        for y in range(0, image.height):
            pos = (y * 16, x * 16)
            pixel = image.getpixel((x, y))
            if pixel[3] > 10:
                block_texture = pix_to_block(pixel, color_compare_to_function(color_compare), color_set)
                # Using numpy arrays because they are just faster
                np_new_image[pos[0]:pos[0] + 16, pos[1]:pos[1] + 16] = block_texture
        yield x

    yield Image.fromarray(np_new_image)
    return


def img_to_blocks_schem(image: Image.Image, details: DetailsDict):
    side: str = details['side']
    blocked_list: list = details['blocked_list']
    mode: str = details['mode']
    color_set: str = details['color_set']
    color_compare: str = details['color_compare']
    schem = mcschematic.MCSchematic()

    # Filtering out the blocks, depending on how the user configured the options
    new_blocks_list = []
    if mode == "Whitelist":
        new_blocks_list = [selected_block for selected_block in blocks_data if selected_block[0] in blocked_list]
    elif mode == "Blacklist":
        new_blocks_list = [selected_block for selected_block in blocks_data if selected_block[0] not in blocked_list]
    else:
        new_blocks_list = blocks_data

    if not new_blocks_list:
        yield "ERROR"
        return

    # Caching, for speed
    def pix_to_block(pix, distance_function: callable, avg_color_set: str):
        # The below statement becomes a list, with all the differences between the current pixel, and all the blocks
        all_differences = [
            (
                (
                    distance_function(pix, block_val[1][side]['color'][avg_color_set])
                ) if (side in block_val[1]) else math.inf
            ) for block_val in new_blocks_list
        ]
        # Getting the lowest different block
        block_index = all_differences.index(min(all_differences))
        block_data = block_parser(new_blocks_list[block_index][0])
        return block_data

    for x in range(0, image.width):
        for y in range(0, image.height):
            pixel = image.getpixel((x, y))
            block_name = pix_to_block(pixel, color_compare_to_function(color_compare), color_set)
            if side == "top" or side == "bottom":
                schem.setBlock((-x, 0, -y), block_name)
            else:
                schem.setBlock((-x, -y, 0), block_name)
        yield x

    yield schem
    return


# This is just to find which color function and color average to use
def color_compare_to_function(color_compare: str) -> callable:
    func = abs_value_difference
    if color_compare == "Euclidean Difference":
        func = euclidean_squared_difference
    elif color_compare == "Weighted Euclidean":
        func = weighted_euclidean_difference
    elif color_compare == "Redmean Difference":
        func = redmean_difference
    elif color_compare == "CIE76 DelE":
        func = cie76_del_e_difference
    return func


# Why tuple and list input? Laziness and performance

# Finds the difference in color between a pixel, and a block average colour
def abs_value_difference(x: tuple, y: list) -> float:
    total_diff = 0
    for val1, val2 in zip(x, y):
        total_diff += abs(val1 - val2)

    return total_diff


def euclidean_squared_difference(x: tuple, y: list) -> float:
    total_diff = 0
    for val1, val2 in zip(x, y):
        total_diff += (val1 - val2) ** 2

    return total_diff


# We shall ignore alpha difference, or be creative
def weighted_euclidean_difference(x: tuple, y: list) -> float:
    del_r = x[0] - y[0]
    del_g = x[1] - y[1]
    del_b = x[2] - y[2]
    alpha_diff = x[3] - y[3]
    r_bar = (x[0] + y[0]) / 2.0
    if r_bar < 128:
        return (2 * (del_r ** 2)) + (4 * (del_g ** 2)) + (3 * (del_b ** 2)) + alpha_diff ** 2
    else:
        return (3 * (del_r ** 2)) + (4 * (del_g ** 2)) + (2 * (del_b ** 2)) + alpha_diff ** 2


def redmean_difference(x: tuple, y: list) -> float:
    del_r = x[0] - y[0]
    del_g = x[1] - y[1]
    del_b = x[2] - y[2]
    r_bar = (x[0] + y[0]) / 2.0
    alpha_diff = x[3] - y[3]
    return (((2 + r_bar / 256) * (del_r ** 2))
            + (4 * (del_g ** 2))
            + ((2 + (255 - r_bar) / 256) * (del_b ** 2))
            + alpha_diff ** 2)


# Doe not account for alpha
def cie76_del_e_difference(x: tuple, y: list) -> float:
    x_no_alpha = [x[0], x[1], x[2]]
    y_no_alpha = [y[0], y[1], y[2]]

    Lab1 = rgb2lab(x_no_alpha)
    Lab2 = rgb2lab(y_no_alpha)

    total_diff = 0
    for val1, val2 in zip(Lab1, Lab2):
        total_diff += (val1 - val2) ** 2

    alpha_diff = x[3] - y[3]

    return total_diff + alpha_diff**2


# https://stackoverflow.com/a/16020102 and or http://www.easyrgb.com/en/math.php
# Remove alpha channel first!
def rgb2lab(input_color: tuple | list) -> list[int]:
    num = 0
    RGB = [0, 0, 0]

    for value in input_color:
        value = float(value) / 255

        if value > 0.04045:
            value = ((value + 0.055) / 1.055) ** 2.4
        else:
            value = value / 12.92

        RGB[num] = value * 100
        num = num + 1

    XYZ = [0, 0, 0, ]

    X = RGB[0] * 0.4124 + RGB[1] * 0.3576 + RGB[2] * 0.1805
    Y = RGB[0] * 0.2126 + RGB[1] * 0.7152 + RGB[2] * 0.0722
    Z = RGB[0] * 0.0193 + RGB[1] * 0.1192 + RGB[2] * 0.9505
    XYZ[0] = round(X, 4)
    XYZ[1] = round(Y, 4)
    XYZ[2] = round(Z, 4)

    XYZ[0] = float(XYZ[0]) / 95.047  # ref_X =  95.047   Observer= 2°, Illuminant= D65
    XYZ[1] = float(XYZ[1]) / 100.0  # ref_Y = 100.000
    XYZ[2] = float(XYZ[2]) / 108.883  # ref_Z = 108.883

    num = 0
    for value in XYZ:

        if value > 0.008856:
            value = value ** 0.3333333333333333
        else:
            value = (7.787 * value) + (16 / 116)

        XYZ[num] = value
        num = num + 1

    Lab = [0, 0, 0]

    L = (116 * XYZ[1]) - 16
    a = 500 * (XYZ[0] - XYZ[1])
    b = 200 * (XYZ[1] - XYZ[2])

    Lab[0] = round(L, 4)
    Lab[1] = round(a, 4)
    Lab[2] = round(b, 4)

    return Lab

# Maybe TODO: When compressing the image, instead of default compression however its done,
#        compress according to the color_averager module decided by user
