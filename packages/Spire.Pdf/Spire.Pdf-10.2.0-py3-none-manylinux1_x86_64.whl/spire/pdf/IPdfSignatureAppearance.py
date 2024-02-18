from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class IPdfSignatureAppearance(abc.ABC):
    """
    Provide a custom signature appearance interface
    """

    @abc.abstractmethod
    def Generate(self, g: 'PdfCanvas'):
        """
        Generate custom signature appearance by a graphics context.

        Parameters:
        - g: A graphics context of signature appearance.
        """
        pass