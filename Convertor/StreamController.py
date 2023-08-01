import os
import sys
import cv2
import numpy as np
import math
from collections import defaultdict
import time

'''
将原始数据库的视频流 (彩色 、深度 、骨骼)
逐帧转换为新的视频流 (调用 frameExact 函数)
并生成训练数据
'''
class StreamController(object):
    
    def __init__(self, frameExactFunc, stack_size=24, target_size=None):
        self.frameExact = frameExactFunc    # 帧提取函数
        self.target_size = target_size      # 想分割的帧size
        self.stack_size = stack_size        # 帧数

        self.edge_cut_size = 0.15
        self.fps = 10

        self.last_time = None
        self.target_intervel = 0.1

    def frameResizeProcess(self, img):      # 重新分割帧大小
        # resize img to reduce data size
        img_Height, img_Width, _ = img.shape
        crop_start = int((img_Width-img_Height)/2)

        padding_pixel = int(img_Height*self.edge_cut_size)

        croped_img = img[padding_pixel:-padding_pixel, crop_start +
                             padding_pixel:crop_start+img_Height-padding_pixel, :]

        if self.target_size:
            croped_img = cv2.resize(croped_img,  self.target_size)

        return croped_img

    def frameAfterHandle(self, croped_img):
        # Convert to Trainng required Data Struct
        x = croped_img.astype(np.float32)
        x = x / 255.0
        x = x - 0.5
        x = x * 2.0
        return x

    def genImgStack(self, images):
        img_stack = []

        for image in images:
            img_frame = self.frameAfterHandle(image)
            img_stack.append(img_frame)

        img_stack = np.asarray(img_stack)
        return img_stack


    def Convert(self, source, target_file):     # 转换成新的视频流
        print("target file is:******************"+target_file)
        # Recorder
        flag = False    # flag设置为0
        videowriter = None
        target_frames_count = self.stack_size
        fc = source.frames
        start_frame = int(fc*0.15)      # 开始的帧数
        valid_frames = int(fc*0.7)
        split_rate = valid_frames/target_frames_count
        images = []

        index = 0
        frame_num = math.floor(start_frame+index*split_rate)    # 统计帧的数量


        # Main Convert loop , Frame by Frame
        for frame in range(source.frames):
            color_frame = source.color_data[frame]  # 彩色帧
            depth_frame = source.depth_data[frame]  # 深度帧
            skeleton_data = source.skeleton_data[frame] # 骨骼帧

            # Key Function
            disp_img, color_frame, hand_depth_img = self.frameExact(
                color_frame, depth_frame, skeleton_data)

            disp_img = self.frameResizeProcess(disp_img)
            hand_depth_img = self.frameResizeProcess(hand_depth_img)

            try:
                color_frame.shape
                cv2.imshow("Orig", disp_img)     # 显示原视频
                hand_depth_img.shape
                cv2.imshow("Depth", hand_depth_img)     # 显示深度视频
            except:
                pass
            # 按键退出
            if cv2.waitKey(3) & 0xff == ord('q'):
                exit()

            if not flag:
                flag = True
                video_frame_size = tuple(disp_img.shape[:2])    # 像素

                videowriter = cv2.VideoWriter(      # 重新生成视频函数
                    target_file+".avi",
                    cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                    self.fps,
                    video_frame_size
                    )

            else:
                #videowriter.write(disp_img)
                videowriter.write(hand_depth_img)
                pass


            if frame == frame_num:
                images.append(disp_img.copy())
                index += 1
                frame_num = math.floor(start_frame+index*split_rate)

        videowriter.release()

        if len(images) < target_frames_count:
            print("Stream Controller report : ERROR Not emough Images")
            exit(-1)

        #train_feature = self.genImgStack(images[:self.target_size])
        #np.save(target_file, train_feature)
        
