# encoding: utf-8

import os
import numpy as np 
import math
import cv2

class RoundExtractor(object):
    def __init__(self):
        self.circle_size=40

    def extract(self, color_frame,depth_frame,skeleton_data):
        # adjust color frame
        cv2.normalize(color_frame,color_frame,255.0,50.0,cv2.NORM_MINMAX)

        #generate spot light mask
        left_hand_point=7
        right_hand_point=11
        head_point=3

        left_hand_spot_light = np.zeros(shape=[480, 640, 1], dtype=np.uint8)
        x,y=skeleton_data[80+left_hand_point*2:80+left_hand_point*2+2]
        cv2.circle(left_hand_spot_light, (x, y), self.circle_size, (1), -1)

        right_hand_spot_light = np.zeros(shape=[480, 640, 1], dtype=np.uint8)
        x,y=skeleton_data[80+right_hand_point*2:80+right_hand_point*2+2]
        cv2.circle(right_hand_spot_light, (x, y), self.circle_size, (1), -1)

        mix_mask=cv2.bitwise_or(left_hand_spot_light,right_hand_spot_light)

        disp_img=cv2.bitwise_and(color_frame,color_frame,mask=mix_mask)

        disp_img=disp_img
        color_frame=None  # 如果不提供， = None
        hand_depth_img = None  # 如果不提供， = None
        
        return disp_img, color_frame, hand_depth_img
