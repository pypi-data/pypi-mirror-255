from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfImageInfo(SpireObject):
    """
    Represents the utility class to store information about Images and its location.
    """

    @property
    def Bounds(self) -> 'RectangleF':
        """
        Gets the Image Boundary location.
        """
        GetDllLibPdf().PdfImageInfo_get_Bounds.argtypes = [c_void_p]
        GetDllLibPdf().PdfImageInfo_get_Bounds.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfImageInfo_get_Bounds,self.Ptr)
        ret = None if intPtr == None else RectangleF(intPtr)
        return ret

    @property
    def Image(self) -> Stream:
        """
        Gets the Image, save to stream.
        """
        GetDllLibPdf().PdfImageInfo_get_Image.argtypes = [c_void_p]
        GetDllLibPdf().PdfImageInfo_get_Image.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfImageInfo_get_Image,self.Ptr)
        ret = None if intPtr == None else Stream(intPtr)
        return ret

    #@property
    #def Index(self) -> int:
    #    """
    #    Gets the Image index.
    #    """
    #    GetDllLibPdf().PdfImageInfo_get_Index.argtypes = [c_void_p]
    #    GetDllLibPdf().PdfImageInfo_get_Index.restype = c_int
    #    ret = CallCFunction(GetDllLibPdf().PdfImageInfo_get_Index,self.Ptr)
    #    return ret

    def Dispose(self):
        """
        Dispose the image resources.
        """
        GetDllLibPdf().PdfImageInfo_Dispose.argtypes = [c_void_p]
        CallCFunction(GetDllLibPdf().PdfImageInfo_Dispose,self.Ptr)