from ..development import CaptionsFormat

from .functions import detectSAMI, readSAMI, saveSAMI


class SAMI(CaptionsFormat):
    """
    Synchronized Accessible Media Interchange

    Read more about it https://learn.microsoft.com/en-us/previous-versions/windows/desktop/dnacc/understanding-sami-1.0

    Example:

    with SAMI("path/to/file.sami") as sami:
        sami.saveSRT("file")
    """
    detect = staticmethod(detectSAMI)
    read = readSAMI
    save = saveSAMI

    from ..lrc.functions import saveLRC
    from ..srt.functions import saveSRT
    from ..sub.functions import saveSUB
    from ..ttml.functions import saveTTML
    from ..usf.functions import saveUSF
    from ..vtt.functions import saveVTT
