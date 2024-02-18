from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class Utilities_PdfImageInfo(SpireObject):
    """
    This class represents information about a PDF image.
    """

    @property
    def Bounds(self) -> 'RectangleF':
        """
        Gets the image boundary location.

        Returns:
            RectangleF: The image boundary location.
        """
        GetDllLibPdf().Utilities_PdfImageInfo_get_Bounds.argtypes = [c_void_p]
        GetDllLibPdf().Utilities_PdfImageInfo_get_Bounds.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().Utilities_PdfImageInfo_get_Bounds,self.Ptr)
        ret = None if intPtr == None else RectangleF(intPtr)
        return ret

    @property
    def Image(self) -> 'Image':
        """
        Gets the image and saves it to a stream.

        Returns:
            Image: The image.
        """
        GetDllLibPdf().Utilities_PdfImageInfo_get_Image.argtypes = [c_void_p]
        GetDllLibPdf().Utilities_PdfImageInfo_get_Image.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().Utilities_PdfImageInfo_get_Image,self.Ptr)
        ret = None if intPtr == None else Image(intPtr)
        return ret