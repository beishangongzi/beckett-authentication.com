# create by andy at 2022/4/1
# reference:
import os
from io import BytesIO

import cv2
import ddddocr
import numpy as np
from scipy import ndimage
from PIL import Image


def read_img(image_data):

    stream = BytesIO(image_data)
    try:
        image = Image.open(stream).convert("L")
    finally:
        stream.close()
    return np.array(image)


class Ocr:
    ocr = ddddocr.DdddOcr(show_ad=False)

    def read_image(self, image=None, image_path=None):
        if image is None and image_path is None:
            raise Exception("image 和 image path 不能全为空")
        if image is not None:
            return read_img(image)
        else:
            return np.array(Image.open(image_path).convert("L"))

    @staticmethod
    def array_to_bytes(image_array):
        success, encoded_image = cv2.imencode(".png", image_array)
        content = encoded_image.tobytes()
        return content

    @staticmethod
    def image_morphology(image):
        image = Ocr.morphology_with_number("grey_erosion", image, 1, size=(3, 3))
        # image = Ocr.morphology_with_number("grey_closing", image, 6, size=(4, 4))
        # Image.fromarray(image).convert("L").show()
        return image

    @staticmethod
    def morphology_with_number(method, image, number=1, **kwargs):
        method = getattr(ndimage, method)
        for i in range(number):
            image = method(image, **kwargs)
        return image

    @classmethod
    def predict(self, img_bytes=None, img_base64=None, *args, **kwargs):
        return self.ocr.classification(img_bytes, img_base64)
    def my_predict(self, image=None, image_path=None):
        image = self.read_image(image, image_path)
        image = self.image_morphology(image)
        image = self.array_to_bytes(image)
        res = self.ocr.classification(image)
        return res
if __name__ == '__main__':
    path = r"C:\Users\21906\Desktop\beckett-authentication.com\captcha\572.png"
    ocr = Ocr()
    res = ocr.my_predict(image_path=path)
    print(res)
