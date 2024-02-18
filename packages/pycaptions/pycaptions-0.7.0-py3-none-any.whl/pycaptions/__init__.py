__version__ = "0.7.0"

import pycaptions.srt as srt
import pycaptions.sub as sub
import pycaptions.ttml as ttml
import pycaptions.vtt as vtt
# import pycaptions.lrc as lrc
# import pycaptions.sami as sami
# import pycaptions.usf as usf

from pycaptions.microTime import MicroTime
from pycaptions.captions import Captions
from pycaptions.srt._class import detectSRT, SubRip
from pycaptions.sub._class import detectSUB, MicroDVD
from pycaptions.ttml._class import detectTTML, TTML
from pycaptions.vtt._class import detectVTT, WebVTT
# from pycaptions.lrc._class import detectLRC, LyRiCs
# from pycaptions.sami._class import detectSAMI, SAMI
# from pycaptions.usf._class import detectUSF, USF

supported_readers = srt.EXTENSIONS + sub.EXTENSIONS + ttml.EXTENSIONS + vtt.EXTENSIONS
                    # + lrc.EXTENSIONS + sami.EXTENSIONS + usf.EXTENSIONS
supported_extensions = srt.EXTENSIONS + sub.EXTENSIONS + ttml.EXTENSIONS + vtt.EXTENSIONS
                       # + lrc.EXTENSIONS + sami.EXTENSIONS + usf.EXTENSIONS

from pycaptions.options import save_extensions, style_options
