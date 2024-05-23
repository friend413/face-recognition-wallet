# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import numpy as np
import sys
import os
from PIL import Image

from facewrapper import ttv_init
from facewrapper import ttv_process
from facewrapper import ttv_compare_feature
from faceresult import FaceResult

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ret = ttv_init()
    print("ttv init ret: ", ret)

    try:
        image1 = Image.open('C:\\Users\\Administrator\\Documents\\WinFaceSDKDemo_240331_python\\Python\\test_images/image1.jpg')
    except:
        exit
    
    try:
        image2 = Image.open('C:\\Users\\Administrator\\Documents\\WinFaceSDKDemo_240331_python\\Python\\test_images/image2.jpg')
    except:
        exit

    image_np1 = np.asarray(image1)
    image_np2 = np.asarray(image2)

    faceResult1 = (FaceResult * 10)()
    faceResult2 = (FaceResult * 10)()

    ret1 = ttv_process(image_np1, image_np1.shape[1], image_np1.shape[0], faceResult1, 10, 0)    #enroll mode    
    print("\n>>>>>>>>>ttv_process: image1 results")
    if ret1 > 0:
        print("        facebox: ", faceResult1[0].x1, " ", faceResult1[0].y1, " ", faceResult1[0].x2, " ", faceResult1[0].y2)
        print(f"        liveness: {faceResult1[0].liveness}")
        print(f"        mask: {faceResult1[0].mask}, glass: {faceResult1[0].glass}")
        print(f"        age: {faceResult1[0].age}, gender: {faceResult1[0].gender}")
    else:
        print("\n>>>>>>>>>ttv_process: image1 no detected face!!!")

    ret2 = ttv_process(image_np2, image_np2.shape[1], image_np2.shape[0], faceResult2, 10, 1)    #identify mode    
    print("\n>>>>>>>>>ttv_process: image1 results")
    if ret2 > 0:
        print("        facebox: ", faceResult2[0].x1, " ", faceResult2[0].y1, " ", faceResult2[0].x2, " ", faceResult2[0].y2)
        print(f"        liveness: {faceResult2[0].liveness}")
        print(f"        mask: {faceResult2[0].mask}, glass: {faceResult2[0].glass}")
        print(f"        age: {faceResult2[0].age}, gender: {faceResult2[0].gender}")
    else:
        print("\n>>>>>>>>>ttv_process: image2 no detected face!!!")

    if ret1 > 0 and ret2 > 0:
        confidence = ttv_compare_feature(faceResult1[0].feature, faceResult2[0].feature)
        print(f"\n>>>>>>>>>ttv_compare_feature: confidence = {confidence}")


