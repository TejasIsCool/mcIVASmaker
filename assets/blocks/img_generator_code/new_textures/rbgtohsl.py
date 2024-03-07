# This is a test, idk how good hsl is compared to rgb
import json
import colorsys


def rgb_to_hsl(color: tuple[float, float, float, float]):
    r, g, b, a = color
    r = r / 255
    g = g / 255
    b = b / 255
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    d = cmax - cmin
    h = 0

    # if cmax and cmax are equal then h = 0
    if d == 0:
        h = 0

    # if cmax equal r then compute h
    elif cmax == r:
        h = (60 * ((g - b) / d) + 360) % 360

    # if cmax equal g then compute h
    elif cmax == g:
        h = (60 * ((b - r) / d) + 120) % 360

    # if cmax equal b then compute h
    elif cmax == b:
        h = (60 * ((r - g) / d) + 240) % 360

    # if cmax equal zero
    if cmax == 0:
        s = 0
    else:
        s = (d / cmax) * 100

    # compute v
    v = cmax * 100
    return [h, s, v, a]


if __name__ == "__main__":
    print(rgb_to_hsl((155.65223155322894,
                      89.33633341899588,
                      56.334034450765195,
                      255.0)))
