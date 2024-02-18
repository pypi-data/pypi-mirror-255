from ..development import CaptionsFormat

from .functions import detectTTML, readTTML, saveTTML


class TTML(CaptionsFormat):
    """
    Timed Text Markup Language

    Read more about it: https://www.speechpad.com/captions/ttml
    Full specification: https://www.w3.org/TR/ttml/

    Example:

    with TTML("path/to/file.ttml") as ttml:
        ttml.saveSRT("file")
    """
    detect = staticmethod(detectTTML)
    _read = readTTML
    _save = saveTTML

    from ..lrc.functions import saveLRC
    from ..sami.functions import saveSAMI
    from ..srt.functions import saveSRT
    from ..sub.functions import saveSUB
    from ..usf.functions import saveUSF
    from ..vtt.functions import saveVTT
