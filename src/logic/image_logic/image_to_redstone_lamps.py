from PIL import Image, ImageFile
import mcschematic
import numpy as np
from path_manager.pather import resource_path

ImageFile.LOAD_TRUNCATED_IMAGES = True

# TODO: Allow all textures as binary options

lit_lamp = Image.open(resource_path("./assets/blocks/redstone_lamp_on.png"))
# noinspection PyTypeChecker
lit_lamp_np = np.array(lit_lamp.convert("RGB"))
unlit_lamp = Image.open(resource_path("./assets/blocks/redstone_lamp.png"))
# noinspection PyTypeChecker
unlit_lamp_np = np.array(unlit_lamp.convert("RGB"))


def img_to_redstone_lamps(
        img: Image.Image,
        brightness: int,
        dither: bool = False,
        alternate_mode: bool = False
):
    bw = [[]]
    if dither:
        bw = img.convert('1')
    if alternate_mode and not dither:
        gray = img.convert('L')
        # Let numpy do the heavy lifting for converting pixels to pure black or white
        bw = np.asarray(gray).copy()

        bw[bw < brightness] = 0  # Black
        bw[bw >= brightness] = 255  # White

    # Storing the new pixels in a numpy array, as it is a bit faster than Pil
    np_arr_test = np.zeros(shape=(img.height * 16, img.width * 16, 3), dtype=np.uint8)
    for x in range(0, img.width):
        for y in range(0, img.height):
            pos = [y * 16, x * 16]
            if dither:
                pixel = bw.getpixel((x, y))
                if pixel == 255:
                    np_arr_test[pos[0]:pos[0] + 16, pos[1]:pos[1] + 16] = lit_lamp_np
                else:
                    np_arr_test[pos[0]:pos[0] + 16, pos[1]:pos[1] + 16] = unlit_lamp_np
            else:
                # Getting the average brightness. If its over threshold, we use the lit redstone lamp
                if alternate_mode:
                    pixel = bw[y][x]
                    if pixel == 255:
                        np_arr_test[pos[0]:pos[0] + 16, pos[1]:pos[1] + 16] = lit_lamp_np
                    else:
                        np_arr_test[pos[0]:pos[0] + 16, pos[1]:pos[1] + 16] = unlit_lamp_np
                else:
                    pixel = img.getpixel((x, y))
                    avg_brightness = (pixel[0] + pixel[1] + pixel[2]) / 3
                    # Use lit redstone lap
                    if avg_brightness >= brightness:
                        np_arr_test[pos[0]:pos[0] + 16, pos[1]:pos[1] + 16] = lit_lamp_np
                    # Use unlit redstone lamp
                    else:
                        np_arr_test[pos[0]:pos[0] + 16, pos[1]:pos[1] + 16] = unlit_lamp_np
        yield x
    yield Image.fromarray(np_arr_test)
    return


def img_to_redstone_lamps_schem(
        img: Image.Image, brightness: int, place_redstone_blocks: bool,
        dither: bool = False, alternate_mode: bool = False
):
    schem = mcschematic.MCSchematic()
    bw = [[]]
    if dither:
        bw = img.convert('1')
    if alternate_mode and not dither:
        gray = img.convert('L')
        # Let numpy do the heavy lifting for converting pixels to pure black or white
        bw = np.asarray(gray).copy()

        bw[bw < brightness] = 0  # Black
        bw[bw >= brightness] = 255  # White

    for x in range(0, img.width):
        for y in range(0, img.height):
            if dither:
                pixel = bw.getpixel((x, y))
                if pixel == 255:
                    if place_redstone_blocks:
                        schem.setBlock((-x, 0, -y), "minecraft:redstone_lamp")
                        schem.setBlock((-x, -1, -y), "minecraft:redstone_block")
                    else:
                        schem.setBlock((-x, 0, -y), "minecraft:redstone_lamp[lit=true]")
                else:
                    schem.setBlock((-x, 0, -y), "minecraft:redstone_lamp")
            else:
                if alternate_mode:
                    pixel = bw[y][x]
                    if pixel == 255:
                        if place_redstone_blocks:
                            schem.setBlock((-x, 0, -y), "minecraft:redstone_lamp")
                            schem.setBlock((-x, -1, -y), "minecraft:redstone_block")
                        else:
                            schem.setBlock((-x, 0, -y), "minecraft:redstone_lamp[lit=true]")
                    else:
                        schem.setBlock((-x, 0, -y), "minecraft:redstone_lamp")
                else:
                    pixel = img.getpixel((x, y))
                    avg_brightness = (pixel[0] + pixel[1] + pixel[2]) / 3

                    # Use lit redstone lap
                    if avg_brightness >= brightness:
                        # new_img.paste(lit_lamp, (x * 16, y * 16))
                        if place_redstone_blocks:
                            schem.setBlock((-x, 0, -y), "minecraft:redstone_lamp")
                            schem.setBlock((-x, -1, -y), "minecraft:redstone_block")
                        else:
                            schem.setBlock((-x, 0, -y), "minecraft:redstone_lamp[lit=true]")
                    # Use unlit redstone lamp
                    else:
                        schem.setBlock((-x, 0, -y), "minecraft:redstone_lamp")
        yield x

    yield schem
    return
