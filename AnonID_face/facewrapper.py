import ctypes, ctypes.util
from ctypes import *
from numpy.ctypeslib import ndpointer
import sys
import os
from AnonID_face.faceresult import FaceResult


dll_path = os.path.abspath(os.path.dirname(__file__)) + '/dlls/libttvrecog.dll'
dll = ctypes.WinDLL(dll_path)

face_engine = cdll.LoadLibrary(dll_path)

dll_path = os.path.abspath(os.path.dirname(__file__)) + '/dlls/libttvsdk.dll'
face_engine = cdll.LoadLibrary(dll_path)

dll_path = os.path.abspath(os.path.dirname(__file__)) + '/dlls/ttvfacewrapper.dll'
face_engine = cdll.LoadLibrary(dll_path)

ttv_init = face_engine.ttv_init
ttv_init.argtypes = []
ttv_init.restype = ctypes.c_int32

# int ttv_process(unsigned char* bgrData, int width, int height, FACE_RESULT* faceResults, int maxFaceNum, int mode), mode: 0 -> enroll, 1 -> identify
ttv_process = face_engine.ttv_process
ttv_process.argtypes = [ndpointer(ctypes.c_ubyte, flags='C_CONTIGUOUS'), ctypes.c_int32, ctypes.c_int32, POINTER(FaceResult), ctypes.c_int32]
ttv_process.restype = ctypes.c_int32

# float ttv_compare_feature(unsigned char* feat1, unsigned char* feat2)
ttv_compare_feature = face_engine.ttv_compare_feature
ttv_compare_feature.argtypes = [c_ubyte * 2056, c_ubyte * 2056]
ttv_compare_feature.restype = ctypes.c_double
