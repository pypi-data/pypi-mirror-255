# tools for semantic segmentation

import cv2
import base64
import json
import numpy as np
from io import BytesIO
from PIL import Image


# semantic segmentation plot
cityspallete = [
    128, 64, 128,
    244, 35, 232,
    70, 70, 70,
    102, 102, 156,
    190, 153, 153,
    153, 153, 153,
    250, 170, 30,
    220, 220, 0,
    107, 142, 35,
    152, 251, 152,
    0, 130, 180,
    220, 20, 60,
    255, 0, 0,
    0, 0, 142,
    0, 0, 70,
    0, 60, 100,
    0, 80, 100,
    0, 0, 230,
    119, 11, 32,
]


def get_color_pallete(npimg):
    out_img = Image.fromarray(npimg.astype('uint8'))
    out_img.putpalette(cityspallete)
    return out_img



