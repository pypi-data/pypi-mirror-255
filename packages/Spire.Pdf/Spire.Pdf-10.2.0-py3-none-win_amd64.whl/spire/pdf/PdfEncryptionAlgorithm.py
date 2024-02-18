from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfEncryptionAlgorithm(Enum):
    """
    Specifies the type of encryption algorithm used.
    """
    RC4 = 1
    AES = 2
