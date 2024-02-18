from ..development import CaptionsFormat

from .functions import detectUSF, readUSF, saveUSF


class USF(CaptionsFormat):
    """
    Universal Subtitle Format

    Read more about it https://en.wikipedia.org/wiki/Universal_Subtitle_Format

    Example:

    with USF("path/to/file.usf") as usf:
        usf.saveSRT("file")
    """
    detect = staticmethod(detectUSF)
    read = readUSF
    save = saveUSF

    from ..lrc.functions import saveLRC
    from ..sami.functions import saveSAMI
    from ..srt.functions import saveSRT
    from ..sub.functions import saveSUB
    from ..ttml.functions import saveTTML
    from ..vtt.functions import saveVTT   
