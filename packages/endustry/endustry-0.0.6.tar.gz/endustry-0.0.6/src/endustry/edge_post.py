import requests
import cv2
import logging
import base64

from tools.general_tools import arr2base64, base642arr
from endustry.atomic_capability import atomic_capabilitys_info as info


class EdgePost(object):
    """The class is used for api post in EI_Endustry platform.
    Args:
        img(bytearray): the picture u need to be inferred, which should be read form cv2.imreadd().
        url(str)      : the api url exposed for infer, like "http://172.27.254.2:32465". make sure your ip is connectned to the api url!
        mode(str)     :  mode should be str in {"OD"->"objection detection, "PE"->"pose estimatio", "IC"->"image classification","AD"->anomaly detection, "OT"->"object tracking", "SS"->"semantic segmentation", "IS"->"instance segmentation"}

    Example:
            >>> img = cv2.imread("../img/apitest.jpg")
            >>> url = 'http://172.27.254.2:32465'
            >>> EPOSD = EdgePost(img, url, mode="OD")
            >>> output = EPOSD.post()
            "This is an example method"
    """
    def __init__(self, img, url, mode):
        """The class is used for api post in EI_Endustry platform.
        Args:
            img(bytearray): the picture u need to be inferred
            url(str)      : the api url exposed for infer
            mode(str)     :  mode should be str in {"OD"->"objection detection, "PE"->"pose estimatio", "IC"->"image classification","AD"->anomaly detection, "OT"->"object tracking", "SS"->"semantic segmentation", "IS"->"instance segmentation"}
        """
        self.img = arr2base64(img)
        self.url = url
        self.mode = mode

        self.headers = self.get_headers()
        self.json = self.get_body()
        self.return_template = self.get_return_template()

    def get_headers(self) -> dict:
        """
        :param img the picture u need to be inferred
        :param url the api url exposed for infer
        :param
        """
        headers = {"Content-Type": "application/json"}

        return headers

    def get_body(self) -> dict:
        body = {
            "images": self.img
        }

        return body

    def get_return_template(self) -> str:
        if self.mode == "OD":
            return_template = info["object detection"].get("output_template")
        elif self.mode == "PE":
            return_template = info["pose estimatio"].get("output_template")
        elif self.mode == "IC":
            return_template = info["image classification"].get("output_template")
        elif self.mode == "AD":
            return_template = info["anomaly detection"].get("output_template")
        elif self.mode == "OT":
            return_template = info["object tracking"].get("output_template")
        elif self.mode == "SS":
            return_template = info["semantic segmentation"].get("output_template")
        elif self.mode == "IS":
            return_template = info["instance segmentation"].get("output_template")
        else:
            raise logging.warning("your given type is not supported")

        return return_template

    def post(self):
        """
        Example:
            >>> img = cv2.imread("../img/apitest.jpg")
            >>> url = 'http://172.27.254.2:32465'
            >>> EPOSD = EdgePost(img, url, mode="OD")
            >>> output = EPOSD.post()
            "This is an example method"
        """
        response = requests.post(url=self.url, headers=self.headers, json=self.json)

        return response


if __name__ == "__main__":
    import json
    import numpy as np
    from io import BytesIO
    import time
    from PIL import Image
    from src.tools.ss_tools import get_color_pallete



    img = cv2.imread("../../test/3.jpg")

    # url = "http://172.27.254.6:34430"
    url = "http://172.27.254.6:34056"
    EPOD = EdgePost(img, url, mode="SS")
    t1 = time.time()
    output = EPOD.post()
    print("posttime cost{}".format(time.time() - t1))

    arr = base642arr(output)
    mask = get_color_pallete(arr)
    mask.save('output.png')





