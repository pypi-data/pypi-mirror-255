from .development.styleFormat import StyleFormat, cssParser


class FullStyle(StyleFormat):

    from .srt.style import fromSRT, getSRT
    from .sub.style import fromSUB, getSUB
    from .ttml.style import fromTTML, getTTML
    from .vtt.style import fromVTT, getVTT


class NoStyle(StyleFormat):

    from .srt.style import fromSRTunstyled as fromSRT, getSRT
    from .sub.style import fromSUBunstyled as fromSUB, getSUB
    from .ttml.style import fromTTMLunstyled as fromTTML, getTTML
    from .vtt.style import fromVTTunstyled as fromVTT, getVTT


def changeStyleOption(style):
    if style == "full":
        Styling = FullStyle
    else:
        Styling = NoStyle


Styling = FullStyle
