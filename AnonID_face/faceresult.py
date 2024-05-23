from ctypes import *

class FaceResult(Structure):
    _fields_ = [("x1", c_int32), ("y1", c_int32), ("x2", c_int32), ("y2", c_int32), 
        ("liveness", c_int32), ("mask", c_int32), ("glass", c_int32), 
        ("age", c_int32), ("gender", c_int32), 
        ("feature", c_ubyte * 2056)        
        ]
    
    