import webcolors
import colorsys
import re


def to_hex2(value):
    return '{:02X}'.format(value)


def get_hexrgb(color):
    if color.startswith("#"):
        if len(color) == 5:
            color = color[:-1]
        if len(color) == 9:
            color = color[:-2]
        return [to_hex2(i) for i in webcolors.hex_to_rgb(color)]
    elif color.endswith(")"):
        if color.startswith("rgb"):
            return [to_hex2(int(i)) for i in color[4:-1].split(",")]
        colors = [re.sub(r'[^0-9.]', '', i)
                  for i in color[:-1].split("(")[1].split(",")]
        if color.startswith("hsl"):
            hue = float(colors[0])
            saturation = float(colors[1])
            light = float(colors[2])
            if hue > 1:
                hue /= 360
            if saturation > 1:
                saturation /= 100
            if light > 1:
                light /= 100
            return [to_hex2(min(int(i*255), 255)) for i in
                    colorsys.hls_to_rgb(hue, light, saturation)]
        print(f"No color parser for {color}")
        return ["00", "00", "00"]
    else:
        return [to_hex2(i) for i in webcolors.name_to_rgb(color)]
