import json

from src.logic.color_averager import *

if __name__ == "__main__":
    with open("../names_list.json", "r") as f:
        data: dict = json.load(f)

    new_structure = {}
    sides = ['top', 'bottom', 'side', 'front', 'back']
    for index, key in enumerate(data.keys()):
        new_structure[key] = {}
        for side in sides:
            if side in data[key]:
                texture = data[key][side]
                new_structure[key][side] = {'file': texture}
                img = Image.open(f"../../all_blocks_textures/{texture}")
                img = img.convert("RGBA")
                linear_avg_col = linear_avg_rgb(img)
                rms_avg_col = rms_rgb_color(img)
                avg_hsl_col = average_hsl_colour(img)
                avg_hsv_col = average_hsv_colour(img)
                avg_lab_col = average_lab_colour(img)
                dominant_col = dominant_colour(img)
                new_structure[key][side]['color'] = {
                    'Linear Average': linear_avg_col,
                    'Root Mean Square Average': rms_avg_col,
                    'HSL Average': avg_hsl_col,
                    'HSV Average': avg_hsv_col,
                    'LAB Average': avg_lab_col,
                    'Dominant Color': dominant_col
                }
                img.close()
        print(f"Done: {key}, Progress: {index}/{len(data.keys())}")

    with open("../out_all_colours.json", "w") as f:
        json.dump(new_structure, f, indent=4)
