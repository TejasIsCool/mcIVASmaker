# WAIT
# THIS IS NOT THE FILE YOU ARE SUPPOSED TO RUN!
# HIS IS USED WHEN YOU WANT TO ADD NEW TEXTURES TO BE USED
# THE IDEA IS
# - To dump the textures with the correct name format
#   (like in all_blocks_textures folder, I got those from the minecraft version jars)
#   into the textures folder in this folder
# - Ig run this file after that, and you'll get a new output file outx.json
# - Do a LOT of editing in that outx file, to make the names and stuff correct
# - Paste the new json data into the names_list.json (Carefully)
# - Make a backup of out_all_colour.json, and then run out_generator
# Though i wouldn't recommend it. It is painful


import json
import os

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
                data[block_name][selection] = filenamepng
            else:
                data[block_name]['extra'].append(filenamepng)
        else:
            block_data = {
                "top": filenamepng,
                "bottom": filenamepng,
                "front": filenamepng,
                "back": filenamepng,
                "side": filenamepng
            }
            data[block_name] = block_data
        print(filenamepng, " done!")

    with open("outx.json", "w") as f:
        json.dump(data, f, indent=4)
