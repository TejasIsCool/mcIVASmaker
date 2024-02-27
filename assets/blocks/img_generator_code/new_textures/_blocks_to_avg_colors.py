# WAIT
# THIS IS NOT THE FILE YOU ARE SUPPOSED TO RUN!
# HIS IS USED WHEN YOU WANT TO ADD NEW TEXTURES TO BE USED
# THE IDEA IS
# - To dump the textures with the correct name format
#   (like in all_blocks_textures folder, I got those from the minecraft version jars)
#   into the textures folder in this folder
# - Ig run this file after that, and you'll get a new output file outx.json
# - Do a LOT of editing in that outx file, to make the names and stuff correct
# - Paste the new djson data into the out.json (Carefully)
# Though i wouldn't recommend it. It is painful


import json
import os

from PIL import Image

import _img_to_rgb_average

if __name__ == "__main__":
    data = {}
    all_files = os.listdir("../new_textures/textures")
    all_files.sort()
    for filenamepng in all_files:
        filename, png = filenamepng.split(".")
        block_name = filename.replace("_top", "")
        block_name = block_name.replace("_bottom", "")
        block_name = block_name.replace("_front", "")
        block_name = block_name.replace("_back", "")
        block_name = block_name.replace("_side", "")

        block_img = Image.open(f"../new_textures/textures/{filenamepng}")
        block_img = block_img.convert("RGBA")
        avg_color = _img_to_rgb_average.img_to_avg_colour(block_img)
        block_img.close()

        if block_name in data:
            selection = ""
            if "top" in filename:
                selection = "top"
            elif "bottom" in filename:
                selection = "bottom"
            elif "front" in filename:
                selection = "front"
            elif "back" in filename:
                selection = "back"
            elif "side" in filename:
                selection = "side"

            if selection != "":
                data[block_name][selection] = {"file": filenamepng, "color": avg_color}
            else:
                data[block_name]['extra'].append({"file": filenamepng, "color": avg_color})
        else:
            block_data = {
                "top": {"file": filenamepng, "color": avg_color},
                "bottom": {"file": filenamepng, "color": avg_color},
                "front": {"file": filenamepng, "color": avg_color},
                "back": {"file": filenamepng, "color": avg_color},
                "side": {"file": filenamepng, "color": avg_color},
                "extra": []
            }
            data[block_name] = block_data
        print(filenamepng, " done!")

    with open("outx.json", "w") as f:
        json.dump(data, f, indent=4)
