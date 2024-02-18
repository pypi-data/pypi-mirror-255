# -*-coding: utf-8 -*-
"""
    @Author : PKing
    @E-mail : 
    @Date   : 2023-12-14 15:09:34
    @Brief  :
"""
import numpy as np
import cv2
import numbers
import random
import PIL.Image as Image
import numpy as np
from typing import List, Tuple


def get_reference_facial_points(out_size=(112, 112), vis=False):
    """
    获得人脸参考关键点,目前支持两种输入的参考关键点,即[96, 112]和[112, 112]
    face_size_ref = [96, 112]
    kpts_ref = [[30.29459953, 51.69630051],
                [65.53179932, 51.50139999],
                [48.02519989, 71.73660278],
                [33.54930115, 92.3655014],
                [62.72990036, 92.20410156]]
    ==================
    face_size_ref = [112, 112]
    kpts_ref = [[38.29459953 51.69630051]
                [73.53179932 51.50139999]
                [56.02519989 71.73660278]
                [41.54930115 92.3655014 ]
                [70.72990036 92.20410156]]

    ==================
    square = True, crop_size = (112, 112)
    square = False,crop_size = (96, 112),
    :param square: True is [112, 112] or False is [96, 112]
    :param isshow: True or False,是否显示
    :return:
    """
    face_size_ref = (96, 112)
    kpts_ref = [[30.29459953, 51.69630051],
                [65.53179932, 51.50139999],
                [48.02519989, 71.73660278],
                [33.54930115, 92.3655014],
                [62.72990036, 92.20410156]]
    kpts_ref = np.asarray(kpts_ref)
    if out_size[0] != face_size_ref[0] or out_size[1] != face_size_ref[1]:
        face_size_ref = np.array(face_size_ref)
        size_diff = max(face_size_ref) - face_size_ref
        kpts_ref += size_diff / 2
        face_size_ref += size_diff
        kpts_ref = kpts_ref * out_size / 112.0
        face_size_ref = face_size_ref * out_size / 112.0
    if vis:
        from pybaseutils import image_utils
        tmp = np.zeros(shape=(int(face_size_ref[1]), int(face_size_ref[0]), 3), dtype=np.uint8)
        tmp = image_utils.draw_landmark(tmp, [kpts_ref], vis_id=True)
        cv2.imshow("kpts_ref", tmp)
        cv2.waitKey(0)
    return kpts_ref


if __name__ == "__main__":
    from pybaseutils import image_utils

    # demo_for_landmarks()
    # demo_for_image_boxes()
    # demo_for_image_affine_transform()
    # demo_for_affine_transform_for_image_points()
