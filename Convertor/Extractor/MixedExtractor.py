# encoding: utf-8

import os
import numpy as np 
import math
import cv2

from Convertor.Extractor.SkinDetector import SkinDetector

class MixedExtractor(object):   # Used to extract the content in data given
    def __init__(self):
        self.skin_detector = SkinDetector()     # 肤色检测器
        self.no_skeleton_mark = False

    def genHandDepthMask(self, depth_img, basic_mask, hand_threshold=80):   # 生成手部深度掩模
        closet_depth_img = cv2.bitwise_and(
            depth_img, depth_img, mask=basic_mask) - 1
        closet_depth = np.min(closet_depth_img)
        devide_depth = closet_depth+hand_threshold

        # generate Mask
        depth_mask = closet_depth_img
        depth_mask[depth_mask > devide_depth] = 0
        depth_mask[depth_mask > 0] = 1
        depth_mask = depth_mask.astype(np.uint8)

        # fix depth mask
        dilation_kernel = np.ones((2, 2), np.uint8)
        depth_mask = cv2.dilate(depth_mask, dilation_kernel)
        return depth_mask.astype(np.uint8)


    def extract(self, color_frame, depth_frame, skeleton_data):   # 将帧进行处理
        # Video_Save_File="video"+str(depth_frame)+".avi"    # 视频保存文件名
        # print(os.getcwd())
        # print("Video_Save_File_name is"+Video_Save_File)
        # fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 定义编解码器并创建VideoWriter
        # video_out = cv2.VideoWriter(Video_Save_File,fourcc,30,(640,480))     # 参数: 保存文件名，编码器，帧率，视频宽高

        # adjust color frame 归一化处理
        cv2.normalize(color_frame, color_frame, 255.0, 50.0, cv2.NORM_MINMAX)

        # generate spot light mask
        left_hand_point = 7
        right_hand_point = 11
        head_point = 3

        # convert skeleton data to frame
        skeleton_frame = np.zeros(shape=[480, 640, 3], dtype=np.uint8)
        if not self.no_skeleton_mark:
            for i in range(80, 120, 2):
                x, y = skeleton_data[i:i+2]
                # cv2.circle(skeleton_frame, (x, y), 3, (0, 255, 0), -1)

            x, y = skeleton_data[80+head_point*2:80+head_point*2+2]
            # cv2.circle(skeleton_frame, (x, y), 6, (255, 0, 0), -1)

        left_hand_point = 7
        left_hand_spot_light = np.zeros(shape=[480, 640, 1], dtype=np.uint8)
        x, y = skeleton_data[80+left_hand_point*2:80+left_hand_point*2+2]
        # cv2.circle(skeleton_frame, (x, y), 3, (255, 0, 0), -1)
        cv2.circle(left_hand_spot_light, (x, y), 45, (1), -1)

        right_hand_spot_light = np.zeros(shape=[480, 640, 1], dtype=np.uint8)
        x, y = skeleton_data[80+right_hand_point*2:80+right_hand_point*2+2]
        # cv2.circle(skeleton_frame, (x, y), 3, (255, 0, 0), -1)
        cv2.circle(right_hand_spot_light, (x, y), 45, (1), -1)

        
        left_hand_depth_mask = self.genHandDepthMask(depth_frame, left_hand_spot_light)
        right_hand_depth_mask = self.genHandDepthMask(depth_frame, right_hand_spot_light)
        hand_depth_mask = cv2.bitwise_or(left_hand_depth_mask, right_hand_depth_mask)

        # generate skin mask 生成皮肤掩模
        skin_mask = self.skin_detector.genSkinMask(color_frame)

        # fix skin mask
        # opening -> kill noise point
        # erode first
        erode_kernel = np.ones((2, 2), np.uint8)
        erode_skin_mask = cv2.erode(skin_mask, erode_kernel)
        # then dilation
        dilation_kernel = np.ones((8, 8), np.uint8)
        opened_skin_mask = cv2.dilate(erode_skin_mask, dilation_kernel)
        skin_mask = opened_skin_mask


        # mix two masks
        mix_mask = cv2.bitwise_and(hand_depth_mask, skin_mask)
        dilation_kernel = np.ones((8, 8), np.uint8)
        opened_mix_mask = cv2.dilate(mix_mask, dilation_kernel)
        mix_mask = opened_mix_mask

        # gen hand_img
        hand_img = cv2.bitwise_and(color_frame, color_frame, mask=mix_mask)
        #hand_img = cv2.bitwise_and(depth_img, depth_img, mask=mix_mask)
        #depth_img = cv2.applyColorMap((depth_frame / (256)).astype(np.uint8), cv2.COLORMAP_JET)
        depth_img = cv2.cvtColor((depth_frame/(256)).astype(np.uint8),cv2.COLOR_GRAY2BGR)

        #depth_img = cv2.bitwise_and(depth_img, depth_img)

        #hand_depth_img = cv2.applyColorMap((depth_frame/(256)).astype(np.uint8), cv2.COLORMAP_JET)
        # hand_depth_img = cv2.bitwise_and(hand_depth_img, hand_depth_img, mask=mix_mask)

        skeleton_frame = np.zeros(shape=[480, 640, 3], dtype=np.uint8)
        disp_img = cv2.add(hand_img, skeleton_frame)
        #disp_img = cv2.add(depth_img, skeleton_data)
       # disp_img = cv2.add(hand_img,skeleton_data)
        # return disp_img, color_frame, hand_depth_img
        return disp_img,color_frame,depth_img
