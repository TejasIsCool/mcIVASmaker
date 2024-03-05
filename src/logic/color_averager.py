from PIL import Image, ImageCms
import colorsys
import math
import numpy as np


# Everything is stored as rgb, just conversions are different
def linear_avg_rgb(image: Image.Image) -> list:
    avg_color = [0, 0, 0, 0]
    counter = 0
    for i in range(image.width):
        for j in range(image.height):
            pixel = image.getpixel((i, j))
            for k in range(4):
                avg_color[k] += pixel[k]
            counter += 1

    return [round(avg_color[i] / counter) for i in range(4)]


# sqrt((R1^2+R2^2)/2),sqrt((G1^2+G2^2)/2),sqrt((B1^2+B2^2)/2)
def rms_rgb_color(image: Image.Image) -> list:
    average_red = 0.0
    average_green = 0.0
    average_blue = 0.0
    average_alpha = 0.0
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.getpixel((x, y))
            average_red += pixel[0] * pixel[0]
            average_green += pixel[1] * pixel[1]
            average_blue += pixel[2] * pixel[2]
            average_alpha += pixel[3] * pixel[3]

    average_red = average_red / (image.width * image.height)
    average_green = average_green / (image.width * image.height)
    average_blue = average_blue / (image.width * image.height)
    average_alpha = average_alpha / (image.width * image.height)
    return [round(average_red ** 0.5), round(average_green ** 0.5), round(average_blue ** 0.5),
            round(average_alpha ** 0.5)]


def average_hsl_colour(image: Image.Image) -> list:
    average_hue_x = 0.0
    average_hue_y = 0.0
    average_sat = 0.0
    average_lightness = 0.0
    average_alpha = 0.0
    max_count = float(image.width * image.height)
    for x in range(image.width):
        for y in range(image.height):
            colour = image.getpixel((x, y))
            # Hue is cyclic, so gotta do
            # theta = [355,5,5,5,5];
            # x = cosd(theta); % cosine in terms of degrees
            # y = sind(theta); % sine with a degree argument
            # meanangle = atan2(mean(y),mean(x))*180/pi
            hsl = colorsys.rgb_to_hls(colour[0] / 255.0, colour[1] / 255.0, colour[2] / 255.0)
            # h is given from 0 to 1, to make it radians, it must be from 0 to 2pi
            average_hue_x += math.cos(hsl[0] * 2 * math.pi)
            average_hue_y += math.sin(hsl[0] * 2 * math.pi)
            average_sat += hsl[1] * 100
            average_lightness += hsl[2] * 100
            average_alpha += colour[3]

    average_hue = math.atan2(average_hue_y / max_count, average_hue_x / max_count) * 180 / math.pi
    average_sat /= max_count
    average_lightness /= max_count
    average_alpha /= max_count

    # Back to rgb
    rgb = colorsys.hls_to_rgb(average_hue / 360, average_sat / 100, average_lightness / 100)
    return [round(rgb[0] * 255), round(rgb[1] * 255), round(rgb[2] * 255), round(average_alpha)]


def average_hsv_colour(image: Image.Image) -> list:
    average_hue_x = 0.0
    average_hue_y = 0.0
    average_sat = 0.0
    average_value = 0.0
    average_alpha = 0.0
    max_count = float(image.width * image.height)
    for x in range(image.width):
        for y in range(image.height):
            colour = image.getpixel((x, y))
            # Hue is cyclic, so gotta do
            # theta = [355,5,5,5,5];
            # x = cosd(theta); % cosine in terms of degrees
            # y = sind(theta); % sine with a degree argument
            # meanangle = atan2(mean(y),mean(x))*180/pi
            hsv = colorsys.rgb_to_hsv(colour[0] / 255.0, colour[1] / 255.0, colour[2] / 255.0)
            # h is given from 0 to 1, to make it radians, it must be from 0 to 2pi
            average_hue_x += math.cos(hsv[0] * 2 * math.pi)
            average_hue_y += math.sin(hsv[0] * 2 * math.pi)
            average_sat += hsv[1] * 100
            average_value += hsv[2] * 100
            average_alpha += colour[3]

    average_hue = (math.atan2(average_hue_y / max_count, average_hue_x / max_count) * 180 / math.pi) % 360
    average_sat /= max_count
    average_value /= max_count
    average_alpha /= max_count

    # Back to rgb
    rgb = colorsys.hsv_to_rgb(average_hue / 360, average_sat / 100, average_value / 100)
    return [round(rgb[0] * 255), round(rgb[1] * 255), round(rgb[2] * 255), round(average_alpha)]


def average_lab_colour(image: Image.Image) -> list:
    rgb_image = image.convert("RGB")
    # Convert to Lab colourspace
    srgb_p = ImageCms.createProfile("sRGB")
    lab_p = ImageCms.createProfile("LAB")

    rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_p, lab_p, "RGB", "LAB")
    Lab = ImageCms.applyTransform(rgb_image, rgb2lab)

    max_count = float(image.width * image.height)
    average_l = 0.0
    average_a = 0.0
    average_b = 0.0
    for x in range(image.width):
        for y in range(image.height):
            colour = Lab.getpixel((x, y))
            average_l += colour[0]
            average_a += colour[1]
            average_b += colour[2]

    average_l /= max_count
    average_a /= max_count
    average_b /= max_count

    temp_img = Image.new("LAB", size=(image.width, image.height))
    for x in range(image.width):
        for y in range(image.height):
            temp_img.putpixel((x, y), (round(average_l), round(average_a), round(average_b)))

    lab2rgb = ImageCms.buildTransformFromOpenProfiles(lab_p, srgb_p, "LAB", "RGB")
    back_rgb = ImageCms.applyTransform(temp_img, lab2rgb)
    col = back_rgb.getpixel((0, 0))

    # Get average average alpha
    average_alpha = 0.0
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.getpixel((x, y))
            average_alpha += pixel[3] * pixel[3]

    average_alpha = average_alpha / max_count
    return [col[0], col[1], col[2], round(average_alpha ** 0.5)]


# https://stackoverflow.com/a/50900143
def dominant_colour(image: Image.Image) -> list:
    img_arr = np.asarray(image.convert('RGB'))
    a2D = img_arr.reshape(-1, img_arr.shape[-1])
    col_range = (256, 256, 256)  # generically : a2D.max(0)+1
    a1D = np.ravel_multi_index(a2D.T, col_range)
    rgb = list(np.unravel_index(np.bincount(a1D).argmax(), col_range))

    # Get average average alpha
    average_alpha = 0.0
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.getpixel((x, y))
            average_alpha += pixel[3] * pixel[3]

    average_alpha = average_alpha / (image.width * image.height)

    return [int(rgb[0]), int(rgb[1]), int(rgb[2]), round(average_alpha ** 0.5)]