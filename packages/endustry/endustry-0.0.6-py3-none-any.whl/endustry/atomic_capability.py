atomic_capabilitys_info = {
    "video classifier": "Not support in edge service mode",
    "pose estimatio": {
        "images": "/9j/4Vr2RXhpZgAASUkqAAgAAA.....",
        "output_template": {
            "result": [
                {
                    "category_id": 1,
                    "keypoints": [
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        296,
                        90,
                        2,
                        0,
                        0,
                        0,
                        297,
                        114,
                        2,
                        327,
                        112,
                        2,
                        278,
                        154,
                        2,
                        0,
                        0,
                        0,
                        268,
                        171,
                        2,
                        0,
                        0,
                        0,
                        296,
                        181,
                        2,
                        329,
                        180,
                        2,
                        299,
                        217,
                        2,
                        329,
                        214,
                        2,
                        304,
                        259,
                        2,
                        334,
                        245,
                        2
                    ],
                    "score": 7.726723895220038
                }
            ]
        }
    },
    "image classification": {
        "body_template": {
            "images": "/9j/4Vr2RXhpZgAASUkqAAgAAA....."
        },
        "output_template": {
            "img_res": [
                {
                    "label": "people",
                    "score": 0.96
                }
            ]
        }

    },
    "object detection": {
        "body_template": {
            "images": "/9j/4Vr2RXhpZgAASUkqAAgAAA....."
        },
        "output_template": {
            "result": [
                {
                    "RegisterMatrix": [
                        [
                            1,
                            0,
                            0
                        ],
                        [
                            0,
                            1,
                            0
                        ],
                        [
                            0,
                            0,
                            1
                        ]
                    ]
                },
                {
                    "Box": {
                        "Y": 0,
                        "Width": 100,
                        "Angle": 0,
                        "X": 0,
                        "Height": 100
                    },
                    "Score": 0.9,
                    "label": "person"
                }
            ]
        }
    },
    "anomaly detection": {
        "body_template": {
            "images": "/9j/4Vr2RXhpZgAASUkqAAgAAA....."
        },
        "return_template": {
            "result.jpg": [
                {
                    "RegisterMatrix": [
                        [
                            1,
                            0,
                            0
                        ],
                        [
                            0,
                            1,
                            0
                        ],
                        [
                            0,
                            0,
                            1
                        ]
                    ]
                },
                {
                    "Box": {
                        "Y": 0,
                        "Width": 0,
                        "Angle": 0,
                        "X": 0,
                        "Height": 0
                    },
                    "Score": 0.9,
                    "label": "abnormal"
                }
            ]
        }
    },
    "object tracking": {
        "body_template": {
            "images": "/9j/4Vr2RXhpZgAASUkqAAgAAA....."
        },
        "output_template": {
            "img_res": [
                {
                    "label": "people",
                    "score": 0.96,
                    "track_id": 1,
                    "box": {
                        "x": 481.37,
                        "y": 239.53,
                        "width": 71.13,
                        "height": 220.9,
                        "angle": 0
                    }
                },
                {
                    "label": "people",
                    "score": 0.93,
                    "track_id": 2,
                    "box": {
                        "x": 691.67,
                        "y": 302.4,
                        "width": 92.57,
                        "height": 267.32,
                        "angle": 0
                    }
                }
            ]

        }
    },
    "semantic segmentation": {
        "body_template": {
            "images": "/9j/4Vr2RXhpZgAASUkqAAgAAA....."
        },
        "output_template": {
            "result": "MS4wMDAwMDAwMDAwMDAwMDAwMDBlKzAwIDEuMDAwMDAwMDAwMDAwMDAwMDAwZSswMCAxLjAwMDAwMDAwM...DAwMDAwZSswMAo="}

    },
    "instance segmentation": {
        "body_template": {
            "images": "/9j/4Vr2RXhpZgAASUkqAAgAAA....."
        },
        "output_template": {
            "img_res":
                [{"label": "person", "score": 0.958,
                  "box": {"x": 131, "y": 186, "width": 128, "height": 102, "angle": 0},
                  "mask": {
                      'counts': 'PR`1h0n:0O2M5K4L4M4L6I7\\O\\NiFh1R9a0N2M3O0M301O00001O'
                                '00000000000003NO01N2O0N3O2Nd0]O1N1O0O2O1N20000O100O2O0O'
                                '101N3N1N2N2O1N1O1O1O1O010O0001O1O1O2N3M2ZFiNi8R2001O000'
                                '01O00001O001O1O1O2N1O1O2N3M7F9I5J4M3N1O3M3L3M3N1N3M2M3'
                                'MRfR3', 'size': [374, 500]}
                  }, "..."]
        }
    },
    "event detection": "Not support in edge service mode",
}
