from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfOrdinarySignatureMaker(PdfSignatureMaker):
    """
    Pdf ordinary signature maker.

    A document can contain one or more ordinary signatures.
    """
    pass