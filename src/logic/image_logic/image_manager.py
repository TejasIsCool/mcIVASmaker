from PIL import Image
from logic.image_logic import image_to_redstone_lamps, img_to_blocks as img_to_block_img
import os
import mcschematic
import logging

logger = logging.getLogger(__name__)


# Convert an image, to what the user specified
def manipulate_image(
        filepath: str, output: str, manipulation: str, crop: list | None, scale: str, details: dict
):
    img = Image.open(filepath)
    # Validating the cropping
    if crop is not None:
        for i in range(4):
            if len(crop[i]) > 8:
                return False

            if crop[i] == "Max":
                crop[i] = img.width if i == 2 else img.height
            else:
                crop[i] = int(crop[i])

        if not all(1000000 > crop[i] >= 0 for i in range(4)):
            return False
        # Cropping the image
        img = img.crop((crop[0], crop[1], crop[2], crop[3]))

    # Scale to numeric scale
    scale: int = round(1 / int(scale[:-1]) * 16)

    # Getting the img to a multiple of 16 so textures match up
    if img.width % scale != 0:
        new_width = img.width + (scale - (img.width % scale))
    else:
        new_width = img.width

    if img.height % scale != 0:
        new_height = img.height + (scale - (img.height % scale))
    else:
        new_height = img.height

    img = img.crop((0, 0, new_width, new_height))
    img.thumbnail((img.width // scale, img.height // scale))
    yield img.width
    if manipulation == "Image To Any Block Image":
        # converting img to rgba
        img = img.convert("RGBA")
        for value in img_to_blocks(img, output, details):
            yield value
        return
    elif manipulation == "Image To Any Block Schematic":
        img = img.convert("RGBA")
        for value in img_to_blocks_schem(img, output, details):
            yield value
        return
    elif manipulation == "Image To Redstone Lamps Image":
        # converting img to rgb, in case of transparency
        img = img.convert("RGB")
        for value in img_to_lamps(img, output, details):
            yield value
        return
    elif manipulation == "Image To Redstone Lamps Schematic":
        img = img.convert("RGB")
        for value in img_to_lamps_schem(img, output, details):
            yield value
        return
        pass
    pass


def img_to_lamps(img: Image.Image, output: str, details: dict):
    brightness = details['brightness']
    dither = details['dither']
    alternate = details['alternate']
    for value in image_to_redstone_lamps.img_to_redstone_lamps(img, brightness, dither, alternate):
        if isinstance(value, Image.Image):
            img = value
        else:
            yield value
    yield "Done Processing!"
    img.save(output)
    img.close()
    yield "Done!"
    return


def img_to_lamps_schem(img: Image.Image, output: str, details: dict):
    brightness = details['brightness']
    place_redstone_blocks = details['place_redstone_blocks']

    schem: mcschematic.MCSchematic = ...
    for value in image_to_redstone_lamps.img_to_redstone_lamps_schem(img, brightness, place_redstone_blocks):
        if isinstance(value, mcschematic.MCSchematic):
            schem: mcschematic.MCSchematic = value
        else:
            yield value
    yield "Done Processing!"
    head, tail = os.path.split(output)
    tail = tail.split(".")[0]
    schem.save(head, tail, mcschematic.Version.JE_1_19_2)
    yield "Done!"
    return


def img_to_blocks(img: Image.Image, output: str, details: dict):
    for value in img_to_block_img.img_to_blocks(
            img,
            {
                'side': details['side'],
                'blocked_list': details['blocklist'],
                'mode': details['mode'],
                'color_set': details['color_set'][0],
                'color_compare': details['color_compare'][0]
            }
    ):
        if isinstance(value, Image.Image):
            img = value
        else:
            yield value
    yield "Done Processing!"
    img.save(output)
    img.close()
    yield "Done!"
    return


def img_to_blocks_schem(img: Image.Image, output: str, details: dict):
    block_list = details['blocklist']
    mode = details['mode']
    side = details['side']
    schem: mcschematic.MCSchematic = ...
    for value in img_to_block_img.img_to_blocks_schem(img, side, block_list, mode):
        if isinstance(value, mcschematic.MCSchematic):
            schem: mcschematic.MCSchematic = value
        else:
            yield value
    yield "Done Processing!"
    head, tail = os.path.split(output)
    tail = tail.split(".")[0]
    schem.save(head, tail, mcschematic.Version.JE_1_19_2)
    yield "Done!"
    return
