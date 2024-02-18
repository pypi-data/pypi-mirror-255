import os
import json
import requests
from datetime import datetime

from tqdm import tqdm
import cv2

last_alarm_time = datetime.strptime('2000-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")


class CameraHeartBeat(object):
    def __init__(self, url, header, camera_json_file_path, device_status_url):
        r"""检测相机在线心跳
        :param url: 获取token的url
        :param header: 获取token的header
        :param camera_json_file_path: 需要检测心跳的json文件。示例：{
          "lilou-jiezhi01": "rtsp://admin:bdtd123456@10.155.65.155:554/Streaming/Channels/801",
          "lilou-jiezhi02": "rtsp://admin:bdtd123456@10.155.65.155:554/Streaming/Channels/501",
          "#222222":"rtsp://admin:bdtd123456@10.155.65.155:554/Streaming/channels/701",
          "#111111":"rtsp://admin:bdtd123456@10.155.65.155:554/Streaming/channels/101"}
        :param device_status_url: 设备状态请求url
        """
        self.url = url
        self.header = header
        self.token = self.get_token()
        self.camera_json_file_path = camera_json_file_path
        self.device_status_url = device_status_url

    def get_token(self):
        response = requests.post(url=self.url, json=self.header, verify=False, timeout=10)

        if response.json()['success']:
            return response.json()['result']
        else:
            print('get token error, error code', response.text['code'])
            return None

    def detect(self):
        while True:
            now = datetime.now()
            onlineTime = now.strftime("%Y-%m-%d %H:%M:%S")
            if (datetime.strptime(onlineTime, "%Y-%m-%d %H:%M:%S") - last_alarm_time).seconds > 600:
                with open('self.camera_json_file_path', 'r') as f:
                    camera_dic = json.load(f)
                last_alarm_time = datetime.strptime(onlineTime, "%Y-%m-%d %H:%M:%S")

            else:
                for device_id, addr in tqdm(camera_dic.items()):
                    try:
                        vc = cv2.VideoCapture(addr)
                        status = 1 - int(vc.isOpened())
                        headers = {'X-Access-Token': self.token}
                        device_status_url = self.device_status_url

                        payload = {
                            "code": device_id,
                            "status": status}
                        response = requests.request("POST", device_status_url, headers=headers, json=payload, timeout=3)
                        result = response.text.encode("utf-8")
                        print('心跳接口返回结果：', device_id, result)

                    except:
                        pass
