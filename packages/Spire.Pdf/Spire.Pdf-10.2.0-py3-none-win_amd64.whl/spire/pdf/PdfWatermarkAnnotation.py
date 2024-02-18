from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfWatermarkAnnotation(PdfAnnotation):
    """
    The water mark annotation.
    """

    @property
    def Appearance(self) -> 'PdfAppearance':
        """
        Get the appearance.
        """
        return None

    @Appearance.setter
    def Appearance(self, value: 'PdfAppearance'):
        """
        Set the appearance.
        <param name="value">The appearance</param>
        """
        GetDllLibPdf().PdfWatermarkAnnotation_set_Appearance.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfWatermarkAnnotation_set_Appearance,self.Ptr, value.Ptr)

    def SetMatrix(self, matrix: List[float]):
        """
        Set the matrix.
        <param name="matrix">The matrix</param>
        """
        countmatrix = len(matrix)
        ArrayTypematrix = c_float * countmatrix
        arraymatrix = ArrayTypematrix()
        for i in range(0, countmatrix):
            arraymatrix[i] = matrix[i]

        GetDllLibPdf().PdfWatermarkAnnotation_SetMatrix.argtypes = [c_void_p, ArrayTypematrix]
        CallCFunction(GetDllLibPdf().PdfWatermarkAnnotation_SetMatrix,self.Ptr, arraymatrix)

    def SetHorizontalTranslation(self, horizontal: float):
        """
        Set the horizontal translation.
        <param name="horizontal">The horizontal</param>
        """
        GetDllLibPdf().PdfWatermarkAnnotation_SetHorizontalTranslation.argtypes = [c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfWatermarkAnnotation_SetHorizontalTranslation,self.Ptr, horizontal)

    def SetVerticalTranslation(self, vertical: float):
        """
        Set the vertical translation.
        <param name="vertical">The vertical</param>
        """
        GetDllLibPdf().PdfWatermarkAnnotation_SetVerticalTranslation.argtypes = [c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfWatermarkAnnotation_SetVerticalTranslation,self.Ptr, vertical)