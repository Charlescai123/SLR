import cv2
import struct
import numpy as np
import os
import sys


class RecordSource(object):
	def __init__(self, path):
		self.path = path
		self.video_path = os.path.join(self.path, "color.avi")
		self.depth_path = os.path.join(self.path, "depth.dat")
		self.skeleton_path = os.path.join(self.path, "skeleton.dat")

		self._loadVideo()
		print('Color Info : ', self.video_param)
		self._loadDepth()
		print('Depth Info : ', self.depth_param)
		self._loadSkeleton()
		print('Skeleton Info : ', self.skeleton_param)

		self.frames = min(self.video_param["FRAMES"], self.depth_param["FRAMES"], self.skeleton_param["FRAMES"])

	def _loadVideo(self):
		self.video_param = dict()
		self.video_data = list()
		self._raw_video = cv2.VideoCapture(self.video_path)
		self.video_param["FRAMES"] = int(self._raw_video.get(cv2.CAP_PROP_FRAME_COUNT))
		self.video_param["FPS"] = int(self._raw_video.get(cv2.CAP_PROP_FPS))
		self.video_param["WIDTH"] = int(self._raw_video.get(cv2.CAP_PROP_FRAME_WIDTH))
		self.video_param["HEIGHT"] = int(self._raw_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
		while True:
			try:
				_frame = self._raw_video.read()[1]
				self.video_data.append(_frame)
				if not len(_frame):
					break
			except:
				break
		self.color_data = self.video_data
		self._raw_video.release()

	def _loadDepth(self):
		self.depth_param = dict()
		self.depth_data = list()
		#set depth data format
		pixel_size = 2
		depth_frame_width = 640
		depth_frame_height = 480
		depth_frame_size = depth_frame_height*depth_frame_width
		with open(self.depth_path, "rb") as depth_file:
			while True:
				try:
					test_frame = depth_file.read(depth_frame_size*2)
					test_frame = struct.unpack('307200H', test_frame)
					depth_frame = np.array(test_frame, dtype=np.uint16).reshape(depth_frame_height, depth_frame_width)
					self.depth_data.append(depth_frame)
				except:
					break
			self.depth_param["FRAMES"] = len(self.depth_data)
			depth_file.close()
	
	def _loadSkeleton(self):
		self.skeleton_param = dict()
		self.skeleton_data = list()
		#set skeleton data format
		with open(self.skeleton_path, "rb") as skeleton_file:
			skeleton_frames = list()
			count = 0
			while True:
				try:
					test_frame = skeleton_file.read(struct.calcsize("80f40i"))
					test_frame = struct.unpack('80f40i', test_frame)
					self.skeleton_data.append(test_frame)
				except:
					break
			self.skeleton_param["FRAMES"] = len(self.skeleton_data)
			skeleton_file.close()
	
	def viewVideo(self):
		cv2.namedWindow("Video")
		for frame in self.video_data:
			try:
				cv2.imshow("Video", frame)
				if cv2.waitKey(3) & 0xFF == ord('q'):
					break
			except:
				break

	def viewDepth(self):
		cv2.namedWindow("Depth")
		#video_frame_size = tuple(disp_img.shape[:2])
		videowriter = cv2.VideoWriter(  # 重新生成视频函数
			 "depth_r.avi",
			cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
			10,
			(640,480)
		)
		for frame in self.depth_data:
			#try:
			print(type(frame))
			print("frame shape is "+str(frame.shape[:2]))
			cv2.imwrite("a.jpg",frame)
			cv2.imshow("Depth", frame/(256*16))
			cv2.waitKey(0)
			videowriter.write(frame)
			# 	if cv2.waitKey(3) & 0xFF == ord('q'):
			# 		break
			# except:
			# 	break
		videowriter.release()

	def viewSkeleton(self):
		cv2.namedWindow("Skeleton")
		for skeleton in self.skeleton_data:
			frame = np.zeros([480, 640], dtype=np.uint8)
			i = 4
			for i in range(80, 120, 2):
				x, y = skeleton[i:i+2]
				frame[y, x] = 255
			cv2.imshow("Skeleton", frame)
			if cv2.waitKey(3) & 0xff == ord('q'):
				break

if __name__ == "__main__":
#	source_param=dict()
#	source_param["folder"]=".\data\P01_0000_1_0_20121117.oni"

	print(os.getcwd())
	source=RecordSource("..\\Data\\DEVISIGN_D\\P01_1\\P01_0000_1_0_20121117.oni")
	source.viewVideo()
	source.viewDepth()
	source.viewSkeleton()
