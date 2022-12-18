from PIL import Image, ImageFile
import mcschematic
import numpy as np

ImageFile.LOAD_TRUNCATED_IMAGES = True

lit_lamp = Image.open("../assets/blocks/redstone_lamp_on.png")
# noinspection PyTypeChecker
lit_lamp_np = np.array(lit_lamp.convert("RGB"))
unlit_lamp = Image.open("../assets/blocks/redstone_lamp.png")
# noinspection PyTypeChecker
unlit_lamp_np = np.array(unlit_lamp.convert("RGB"))


def img_to_redstone_lamps(img: Image.Image, brightness: int):
    # Storing the pixels in a numpy array, as it is a bit faster than Pil
    np_arr_test = np.zeros(shape=(img.height * 16, img.width * 16, 3), dtype=np.uint8)
    for x in range(0, img.width):
        for y in range(0, img.height):
            pos = [y * 16, x * 16]
            pixel = img.getpixel((x, y))
            # Getting the average brightness. If its over threshold, we use the lit redstone lamp
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


def img_to_redstone_lamps_schem(img: Image.Image, brightness: int, place_redstone_blocks: bool):
    schem = mcschematic.MCSchematic()
    for x in range(0, img.width):
        for y in range(0, img.height):
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
