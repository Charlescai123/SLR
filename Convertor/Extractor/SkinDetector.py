# encoding: utf-8

# modified from Will Brennan's repo -> add otsu to enhance skin detect
import cv2
import numpy as np

class SkinDetector(object):
    def __init__(self):
        self.thresh = 0.5
    
    def genSkinMask(self, img):     # 为一张图片生成皮肤掩膜

        grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        threshold_val, otsu_img = cv2.threshold(grey_img, 0, 255, cv2.THRESH_OTSU)

        self.div = threshold_val

        img_hsv_mask = self._genHsvMask(img)
        img_rgb_mask = self._genRgbMask(img)
        img_ycrcb_mask = self._genYCrCbMask(img)

        img_mask = (img_hsv_mask+img_rgb_mask+img_ycrcb_mask)/3.0   # There we get img_mask is a data array
        img_mask[img_mask < self.thresh] = 0.0
        img_mask[img_mask >= self.thresh] = 255.0

        img_mask = img_mask.astype(np.uint8)

        img_mask = self._closingMask(img_mask)
        img_mask = self._genCutMask(img, img_mask)
        
        return img_mask


    def _genCutMask(self, img_col, mask):
        kernel = np.ones((50, 50), np.float32) / (50 * 50)
        dst = cv2.filter2D(mask, -1, kernel)
        dst[dst != 0] = 255
        free = np.array(cv2.bitwise_not(dst), dtype=np.uint8)

        grab_mask = np.zeros(mask.shape, dtype=np.uint8)
        grab_mask[:, :] = 2
        grab_mask[mask == 255] = 1
        grab_mask[free == 255] = 0

        if np.unique(grab_mask).tolist() == [0, 1]:
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)

            if img_col.size != 0:
                mask, bgdModel, fgdModel = cv2.grabCut(img_col, grab_mask, None, bgdModel, fgdModel, 5,
                                                    cv2.GC_INIT_WITH_MASK)
                mask = np.where((mask == 2) | (mask == 0), 0, 1).astype(np.uint8)
            else:
                pass

        return mask


    def _closingMask(self, mask):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)

        return mask


    def _genHsvMask(self, img):
        lower_thresh = np.array([0, 50, 0], dtype=np.uint8)
        upper_thresh = np.array([120, 150, 255], dtype=np.uint8)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        msk_hsv = cv2.inRange(img_hsv, lower_thresh, upper_thresh)

        msk_hsv[msk_hsv < self.div] = 0
        msk_hsv[msk_hsv >= self.div] = 1

        return msk_hsv.astype(float)


    def _genRgbMask(self, img):
        lower_thresh = np.array([45, 52, 108], dtype=np.uint8)
        upper_thresh = np.array([255, 255, 255], dtype=np.uint8)

        mask_a = cv2.inRange(img, lower_thresh, upper_thresh)
        mask_b = 255 * ((img[:, :, 2] - img[:, :, 1]) / 20)
        mask_c = 255 * ((np.max(img, axis=2) - np.min(img, axis=2)) / 20)
       
        mask_d = np.bitwise_and(np.uint64(mask_a), np.uint64(mask_b))
        msk_rgb = np.bitwise_and(np.uint64(mask_c), np.uint64(mask_d))

        msk_rgb[msk_rgb < self.div] = 0
        msk_rgb[msk_rgb >= self.div] = 1
        
        return msk_rgb.astype(float)


    def _genYCrCbMask(self, img):
        lower_thresh = np.array([90, 100, 130], dtype=np.uint8)
        upper_thresh = np.array([230, 120, 180], dtype=np.uint8)

        img_ycrcb = cv2.cvtColor(img, cv2.COLOR_RGB2YCR_CB)
        msk_ycrcb = cv2.inRange(img_ycrcb, lower_thresh, upper_thresh)

        msk_ycrcb[msk_ycrcb < self.div] = 0
        msk_ycrcb[msk_ycrcb >= self.div] = 1

        return msk_ycrcb.astype(float)

if __name__ == "__main__":
    source = cv2.VideoCapture(0)
    skin_detector = SkinDetector()
    while True:
        frame = source.read()[1]
        
        skin_mask = skin_detector.genSkinMask(frame)

        skin_img = cv2.bitwise_and(frame, frame, mask=skin_mask)

        cv2.imshow("Orig", frame)
        cv2.imshow("Mask", skin_mask)
        cv2.imshow("Skin", skin_img)

        if cv2.waitKey(1) & 0xff == ord('q'):
            break
