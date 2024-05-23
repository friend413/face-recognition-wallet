import argparse
import numpy as np
import ctypes
import os.path
import time
from PIL import Image

from AnonID_face.facewrapper import ttv_init, ttv_process, ttv_compare_feature
from AnonID_face.faceresult import FaceResult

FEATURE_SIZE = 2056

def InitFaceSDK():
    ret = ttv_init()
    return ret

def Convert2BGR(image):
    data = np.array(image)
    red, green, blue = data.T
    data = np.array([blue, green, red])
    data = data.transpose()
    image = Image.fromarray(data)
    return image

def GetLivenessInfo(image):
    bbox = np.zeros([4], dtype=np.int32)  
    image_np = np.asarray(Convert2BGR(image))
    faceResult = (FaceResult * 10)()
    ret = ttv_process(image_np, image_np.shape[1], image_np.shape[0], faceResult, 10, 0)    #identify mode        

    if ret > 0:
        live_score = faceResult[0].liveness
        bbox = np.array([faceResult[0].x1, faceResult[0].y1, faceResult[0].x2, faceResult[0].y2])
 
        if live_score == 1:
            result = "Genuine"
        elif live_score == -102:
            result = "Face not detected"
        elif live_score == -103:
            result = "Liveness failed"
        elif live_score == 0:
            result = "Spoof"
        elif live_score == -3:
            result = "Face is too small"
        elif live_score == -4:
            result = "Face is too large"
        else:
            result = "Error"
        return bbox, live_score, result

    return bbox, -105, None

def GetFeatureInfo(image, is_verify):
    bbox = np.zeros([4], dtype=np.int32)
    image_np = np.asarray(Convert2BGR(image))
    faceResult = (FaceResult * 10)()
    ret = ttv_process(image_np, image_np.shape[1], image_np.shape[0], faceResult, 10, 1)    #identify mode        
    if ret > 0:
        bbox = np.array([faceResult[0].x1, faceResult[0].y1, faceResult[0].x2, faceResult[0].y2])
        live_score = faceResult[0].liveness
        feature = faceResult[0].feature
        return bbox, live_score, feature
    
    return None, None, None


def GetFaceSimilarity(feat1, feat2):
    return ttv_compare_feature((ctypes.c_ubyte * 2056)(*feat1), (ctypes.c_ubyte * 2056)(*feat2))