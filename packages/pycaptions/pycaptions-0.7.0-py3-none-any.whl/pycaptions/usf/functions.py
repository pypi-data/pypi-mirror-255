import io

from ..development import Block, BlockType, captionsDetector, captionsReader, captionsWriter
from ..microTime import MicroTime as MT


@staticmethod
@captionsDetector
def detectUSF(content: str | io.IOBase) -> bool:
    """
    Used to detect Universal Subtitle Format caption format.

    It returns True if:
     - the first line starts with <USFSubtitles
    """
    if content.readline().lstrip().startswith("<USFSubtitles"):
        return True
    return False

@captionsReader
def readUSF(self, content: str | io.IOBase, languages: list[str] = None, **kwargs):
    raise ValueError("Not Implemented")

@captionsWriter("USF", "getUSF")
def saveUSF(self, filename: str, languages: list[str] = None, generator: list = None, 
            file: io.FileIO = None, **kwargs):
    raise ValueError("Not Implemented")
