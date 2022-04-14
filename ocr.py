# create by andy at 2022/4/1
# reference:
import os

import cv2
import ddddocr


def pre_process(img, ker):
    img_gray = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    img_gray = cv2.morphologyEx(img_gray, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (ker, ker)), iterations=1)
    success, encoded_image = cv2.imencode(".png", img_gray)
    content = encoded_image.tobytes()
    return content


def ocr_local(img,ker=2):
    ocr = ddddocr.DdddOcr(show_ad=False)
    # with open(img, "rb") as f:
    #     img_bytes = f.read()
    img_bytes = pre_process(img, ker=ker)
    res = ocr.classification(img_bytes)
    return res


if __name__ == '__main__':
    for file in os.listdir("captcha"):
        print(file)
        res = ocr_local(f"captcha/{file}", 1)
        print(res)
        res = ocr_local(f"captcha/{file}", 2)
        print(res)
        res = ocr_local(f"captcha/{file}", 3)
        print(res)
        print("----------")
    # res = ocr_local("test.png")
    # print(res)
