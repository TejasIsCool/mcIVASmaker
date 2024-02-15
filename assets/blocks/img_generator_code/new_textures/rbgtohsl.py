# This is a test, idk how good hsl is compared to rgb
import json

if __name__ == "__main__":
    with open("../out.json", "r") as f:
        blocks_data = json.load(f)
    for block in blocks_data.keys():
        for sides in blocks_data[block].keys():
            if sides != "extra":
                r, g, b, a = blocks_data[block][sides]['color']
                r = r/255
                g = g/255
                b = b/255
                cmax = max(r,g,b)
                cmin = min(r,g,b)
                d = cmax-cmin

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
                blocks_data[block][sides]['color'] = [h,s,v,a]


    with open("out2.json", "w") as f:
        json.dump(blocks_data,f,indent=4)