from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfCertificate(SpireObject):
    """
    Represents the Certificate object.
    """

    @staticmethod
    def GetCertificates() -> List['PdfCertificate']:
        """
        Gets the certificates in all storages.

        Returns:
            PdfCertificate array.
        """
        GetDllLibPdf().PdfCertificate_GetCertificates.restype = IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPdf().PdfCertificate_GetCertificates)
        ret = GetVectorFromArray(intPtrArray, PdfCertificate)
        return ret

    @staticmethod
    def FindBySubject(storeName: 'StoreType', subject: str) -> 'PdfCertificate':
        """
        Finds the certificate by subject.

        Args:
            storeName: The store name.
            subject: The certificate subject.

        Returns:
            The certificate.
        """
        enumstoreName: c_int = storeName.value

        GetDllLibPdf().PdfCertificate_FindBySubject.argtypes = [c_int, c_wchar_p]
        GetDllLibPdf().PdfCertificate_FindBySubject.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfCertificate_FindBySubject,enumstoreName, subject)
        ret = None if intPtr == None else PdfCertificate(intPtr)
        return ret

    @staticmethod
    def FindByIssuer(storeName: 'StoreType', issuer: str) -> 'PdfCertificate':
        """
        Finds the certificate by issuer.

        Args:
            storeName: The store name.
            issuer: The certificate issuer.

        Returns:
            The certificate.
        """
        enumstoreName: c_int = storeName.value

        GetDllLibPdf().PdfCertificate_FindByIssuer.argtypes = [c_int, c_wchar_p]
        GetDllLibPdf().PdfCertificate_FindByIssuer.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfCertificate_FindByIssuer,enumstoreName, issuer)
        ret = None if intPtr == None else PdfCertificate(intPtr)
        return ret

    @staticmethod
    def FindBySerialId(storeName: 'StoreType', certId: 'Byte[]') -> 'PdfCertificate':
        """
        Finds the certificate by serial number.

        Args:
            storeName: The certification system store type.
            certId: The certificate id.

        Returns:
            The certificate.
        """
        enumstoreName: c_int = storeName.value
        countcertId = len(certId)
        ArrayTypecertId = c_void_p * countcertId
        arraycertId = ArrayTypecertId()
        for i in range(0, countcertId):
            arraycertId[i] = certId[i].Ptr

        GetDllLibPdf().PdfCertificate_FindBySerialId.argtypes = [c_int, ArrayTypecertId]
        GetDllLibPdf().PdfCertificate_FindBySerialId.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfCertificate_FindBySerialId,enumstoreName, arraycertId)
        ret = None if intPtr == None else PdfCertificate(intPtr)
        return ret