# THIS IS A PICKLE GENERATOR
# SHOULD ONLY BE USED IF YOU KNOW WHAT YOU ARE DOING
# THIS IS NOT PART OF THE PROGRAM YET


import json
import math
import pickle

from typing import Tuple, List

from PIL import Image

# TODO: Allow Pickle file, to speed up the image conversion

path = "../../../assets/blocks/all_blocks_textures/"
with open("../../../assets/blocks/img_generator_code/out.json", "r") as f:
    blocks_data: List = list(json.load(f).items())

blocks_img = {}
for block in blocks_data:
    for block_side in block[1].keys():
        if block_side == "extra":
            pass
        else:
            img = Image.open(path + block[1][block_side]['file'])
            blocks_img[block[0] + block_side] = img

new_block_list = blocks_data


def value_difference(x: Tuple, y: List) -> float:
    total_diff = 0
    for val1, val2 in zip(x, y):
        total_diff += abs(val1 - val2)

    return total_diff


side = 'bottom'


def pix_to_block_name(pix):
    all_differences = [
        (value_difference(pix, block_val[1][side]['color']) if (
                side in block_val[1]
        ) else math.inf)
        for block_val in new_block_list
    ]
    block_index = all_differences.index(min(all_differences))
    return new_block_list[block_index][0]


if __name__ == "__main__":
    data = {}

    for r in range(0, 256):
        for g in range(0, 256):
            for b in range(0, 256):
                data[(r, g, b)] = pix_to_block_name([r, g, b, 255])
        print(r)

    with open('rgb_bottom.pickle', 'wb') as f:
        pickle.dump(data, f)
