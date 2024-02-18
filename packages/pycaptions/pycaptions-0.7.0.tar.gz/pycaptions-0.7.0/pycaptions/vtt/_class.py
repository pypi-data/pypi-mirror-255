from ..development import CaptionsFormat

from .functions import detectVTT, readVTT, saveVTT


class WebVTT(CaptionsFormat):
    """
    Web Video Text Tracks

    Read more about it: https://www.speechpad.com/captions/webvtt
    Full specification: https://www.w3.org/TR/webvtt/

    Example:

    with WebVTT("path/to/file.vtt") as vtt:
        vtt.saveSRT("file")
    """
    detect = staticmethod(detectVTT)
    _read = readVTT
    _save = saveVTT

    from ..lrc.functions import saveLRC
    from ..sami.functions import saveSAMI
    from ..srt.functions import saveSRT
    from ..sub.functions import saveSUB
    from ..usf.functions import saveUSF
    from ..ttml.functions import saveTTML