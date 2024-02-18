from ..development import CaptionsFormat
from .functions import detectSUB, readSUB, saveSUB


class MicroDVD(CaptionsFormat):
    """
    MicroDVD

    Read more about it https://en.wikipedia.org/wiki/MicroDVD

    Example:

    with MicroDVD("path/to/file.sub") as sub:
        sub.saveSRT("file")
    """
    detect = staticmethod(detectSUB)
    _read = readSUB
    _save = saveSUB

    from ..lrc.functions import saveLRC
    from ..sami.functions import saveSAMI
    from ..srt.functions import saveSRT
    from ..ttml.functions import saveTTML
    from ..usf.functions import saveUSF
    from ..vtt.functions import saveVTT