import cv2
import base64
import json
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt


def arr2base64(img):
    """transform image to base64 style"""
    _, buffer = cv2.imencode('.jpg', img)
    jpg_as_text = base64.b64encode(buffer)

    return jpg_as_text.decode('utf-8')


def base642arr(post_rst):
    """transform base64str to image style"""
    base64str = json.loads(post_rst.text).get('result')
    base64decode = base64.urlsafe_b64decode(base64str)
    arr = np.loadtxt(BytesIO(base64decode))

    return arr


def plot_cfg():
    """cfg for mat.plt"""
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 显示负号
    # 下面两行为plt.show()显示图片时，设置为黑色背景，是为了在我设置的Notebook黑色背景下，图片好看！
    plt.style.use('dark_background')
    # plt.style.use('seaborn-notebook')


if __name__ == "__main__":
    plot_cfg()
    img = cv2.imread("../../test/apitest.jpg")
    figure = plt.figure(figsize=(10, 10))
    ax = figure.add_subplot(1, 1, 1)
    ax.imshow(img)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    plt.show()









