import io

from ..development import Block, BlockType, captionsDetector, captionsReader, captionsWriter
from ..microTime import MicroTime as MT
from bs4 import BeautifulSoup


@staticmethod
@captionsDetector
def detectSAMI(content: str | io.IOBase) -> bool:
    """
    Used to detect Synchronized Accessible Media Interchange caption format.

    It returns True if:
     - the first line starts with <SAMI>
    """
    if content.readline().lstrip().startswith("<SAMI>"):
        return True
    return False


@captionsReader
def readSAMI(self, content: str | io.IOBase, languages: list[str] = None, **kwargs):
    raise ValueError("Not Implemented")


@captionsWriter("SAMI", "getSAMI")
def saveSAMI(self, filename: str, languages: list[str] = None, generator: list = None, 
             file: io.FileIO = None, **kwargs):
    raise ValueError("Not Implemented")



