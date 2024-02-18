from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfImageHelper(SpireObject):
    """
    Helper class for working with PDF images.
    """
    def __init__(self):
        GetDllLibPdf().PdfImageHelper_CreatePdfImageHelper.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfImageHelper_CreatePdfImageHelper)
        super(PdfImageHelper, self).__init__(intPtr)

    def GetImagesInfo(self, page: 'PdfPageBase') -> List['PdfImageInfo']:
        """
        Get all image information on the page.

        Args:
            page (PdfPageBase): The PDF page.

        Returns:
            List[PdfImageInfo]: A list of image information objects.
        """
        intPtrpage: c_void_p = page.Ptr

        GetDllLibPdf().PdfImageHelper_GetImagesInfo.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfImageHelper_GetImagesInfo.restype = IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPdf().PdfImageHelper_GetImagesInfo,self.Ptr, intPtrpage)
        ret = GetObjVectorFromArray(intPtrArray, PdfImageInfo)
        return ret

    def ReplaceImage(self, imageInfo: 'PdfImageInfo', newImage: 'PdfImage'):
        """
        Replace an image.

        Args:
            imageInfo (PdfImageInfo): The original image info.
            newImage (PdfImage): The new image to replace with.
        """
        intPtrimageInfo: c_void_p = imageInfo.Ptr
        intPtrnewImage: c_void_p = newImage.Ptr

        GetDllLibPdf().PdfImageHelper_ReplaceImage.argtypes = [c_void_p, c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfImageHelper_ReplaceImage,self.Ptr, intPtrimageInfo, intPtrnewImage)