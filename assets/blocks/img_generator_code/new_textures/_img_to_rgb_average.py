# DO NOT RUN!!


from PIL import Image
from typing import List


def img_to_avg_colour(img: Image.Image) -> List[int]:
    avg_color = [0, 0, 0, 0]
    counter = 0
    for i in range(img.width):
        for j in range(img.height):
            pixel = img.getpixel((i, j))
            # print(pixel)
            for k in range(4):
                avg_color[k] += pixel[k]
            counter += 1

    return [round(avg_color[i]/counter) for i in range(4)]


if __name__ == "__main__":
    imag = Image.open("../../all_blocks_textures/blue_stained_glass.png")
    imag = imag.convert("RGBA")
    col = img_to_avg_colour(imag)
