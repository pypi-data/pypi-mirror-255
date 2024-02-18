from ..development.colors import get_hexrgb

from .extras import TTML_FROM_CSS

@staticmethod
def fromTTMLunstyled(text, pattern, options):
    pass

@staticmethod
def fromTTML(text):
    pass


def getTTML(self, lines:int = -1, options: dict = None, 
            add_metadata: bool = True, **kwargs):
    self.format_lines(lines=lines, **kwargs)
    for tag in self.find_all():
        if tag.name:
            if tag.get("style"):
                inline_css = self.parseStyle(tag.get("style"))
                for prop in inline_css:
                    prop_name = prop.name.lower()
                    if prop_name in TTML_FROM_CSS:
                        ttml_property = TTML_FROM_CSS[prop_name]
                        if prop_name in ["color", "background-color"]:
                            tag["tts:"+ttml_property] = "#"+"".join(get_hexrgb(prop.value))
                        else:
                            tag["tts:"+ttml_property] = str(prop.value)
                del tag["style"]
            if tag.name == "br" and lines == 1:
                tag.insert_before(" ")
                tag.unwrap()
    return str(self)
