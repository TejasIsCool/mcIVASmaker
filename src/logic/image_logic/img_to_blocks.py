import math
import mcschematic
import json
from typing import List, Tuple
import functools
import numpy as np
from logic.image_logic.block_parser import block_parser
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

# Loading the pre-generated blocks color
path = "../assets/blocks/all_blocks_textures/"
with open("../assets/blocks/img_generator_code/out.json", "r") as f:
    blocks_data: List = list(json.load(f).items())

# Storing all the images in memory (as numpy arrays)
blocks_img_np = {}
for block in blocks_data:
    for block_side in block[1].keys():
        if block_side == "extra":
            pass
        else:
            img = Image.open(path + block[1][block_side]['file']).convert("RGBA")
            # noinspection PyTypeChecker
            blocks_img_np[block[0] + block_side] = np.array(img)


def img_to_blocks(image: Image.Image, side: str, blocked_list: List, mode: str):
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
    def pix_to_block(pix):
        # The below statement becomes a list, with all the differences between the current pixel, and all the blocks
        all_differences = [
            (value_difference(pix, block_val[1][side]['color']) if (
                    side in block_val[1]
            ) else math.inf)
            for block_val in new_blocks_list
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
                block_texture = pix_to_block(pixel)
                # Using numpy arrays because they are just faster
                np_new_image[pos[0]:pos[0] + 16, pos[1]:pos[1] + 16] = block_texture
        yield x
    yield Image.fromarray(np_new_image)
    return


def img_to_blocks_schem(image: Image.Image, side: str, blocked_list: List, mode: str):
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
    @functools.lru_cache(maxsize=100000)
    def pix_to_block(pix):
        all_differences = [
            (value_difference(pix, block_val[1][side]['color']) if (
                    side in block_val[1]
            ) else math.inf)
            for block_val in new_blocks_list
        ]
        block_index = all_differences.index(min(all_differences))
        block_data = block_parser(new_blocks_list[block_index][0])
        return block_data

    for x in range(0, image.width):
        for y in range(0, image.height):
            pixel = image.getpixel((x, y))
            block_name = pix_to_block(pixel)
            if side == "top" or side == "bottom":
                schem.setBlock((-x, 0, -y), block_name)
            else:
                schem.setBlock((-x, -y, 0), block_name)
        yield x

    yield schem
    return


# Finds the difference in color between a pixel, and a block average colour
def value_difference(x: Tuple, y: List) -> float:
    total_diff = 0
    for val1, val2 in zip(x, y):
        total_diff += abs(val1 - val2)

    return total_diff
