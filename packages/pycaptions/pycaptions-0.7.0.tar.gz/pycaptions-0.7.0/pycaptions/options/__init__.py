from .fileExtension import FileExtensions
from .style import StyleOptions


save_extensions = FileExtensions()
"""
Globaly stores file extensions of implemented formats.

Example:
- Changing ttml extansion from .ttml to .xml
save_extensions.TTML = ".xml"
"""

style_options = StyleOptions()
"""
Globaly stores style options. These are default options that you can override with arguments.

Example
style_options.style = "full"
style_options.lines = -1
"""
