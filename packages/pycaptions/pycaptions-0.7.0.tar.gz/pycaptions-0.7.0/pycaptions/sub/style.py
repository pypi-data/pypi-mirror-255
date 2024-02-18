import re

from ..development.colors import get_hexrgb


@staticmethod
def fromSUBunstyled(text, pattern, options):
    return re.sub(pattern, "", text)

@staticmethod
def fromSUB(text, pattern, options):
    start = ""
    end = ""
    font_vars = []
    _class = ""
    for control_code in re.findall(pattern, text):
        control_code = control_code.strip("{} ").split(":")
        if len(control_code) != 2:
            continue
        control_code, value = control_code[0], control_code[1]
        control_code = control_code.upper()
        if control_code == "Y":
            value = value.split(",")
            for i in value:
                if i == "i":
                    start += "<i>"
                    end += "</i>"
                elif i == "b":
                    start += "<i>"
                    end += "</i>"
                elif i == "u":
                    start += "<i>"
                    end += "</i>"
                elif i == "s":
                    start += "<i>"
                    end += "</i>"
        elif control_code == "F":
            font_vars.append("font-family:"+value)
        elif control_code == "S":
            font_vars.append("font-size:"+value)
        elif control_code == "C":
            font_vars.append("color:#"+value[-2:]+value[-4:-2]+value[-6:-4])
        elif control_code == "H":
            options["language"] = value
        else:
            # control code 'P' has mixed info of how it works, ommited for now
            # there appears to also be 'o' 
            if not _class:
                _class = f"micro_dvd_{options['counter']}"
                options["counter"] += 1
                options["control_codes"][_class] = dict()
            options["control_codes"][_class][control_code] = value
    if font_vars:
        if _class:
            _class = f"class='{_class}'"
        start += f"<p {_class}style='"+";".join(font_vars)+";'>"
        end += "</p>"

    return start+re.sub(pattern, "", text)+end

def getSUB(self, lines:int = -1, options: dict = None,
           add_metadata: bool = True, **kwargs):
    self.format_lines(lines=lines, **kwargs)
    y = {"bold":False, "italic": False, "underline":False}
    props = {"color":False, "size":False, "font":False}
    new_line = self.find(string=True)
    for tag in self.find_all():
        if tag.name:
            if tag.get("style"):
                inline_css = self.parseStyle(tag.get("style"))
                for prop in inline_css:
                    prop_name = prop.name.lower()
                    prop_value = str(prop.value)
                    if prop_name == "color" and not props["color"]:
                        props["color"] = True
                        new_line.insert_before("{C:$"+"".join(reversed(get_hexrgb(prop_value)))+"}")
                    elif prop_name == "font-size"and not props["size"]:
                        props["size"] = True
                        new_line.insert_before("{S:"+prop_value+"}")
                    elif prop_name == "font-family"and not props["font"]:
                        props["font"] = True
                        new_line.insert_before("{F:"+prop_value+"}")
                    elif prop_name == "font-weight" and prop_value == "bold":
                        y["bold"] = True
                    elif prop_name == "font-style" and prop_value == "italic":
                        y["italic"] = True
                    elif prop_name == "text-decoration" and prop_value == "underline":
                        y["underline"] = True
            if tag.get("class"):
                for i in tag.get('class'):
                    if "micro_dvd_" in i:
                        for control_code, value in options["micro_dvd"]["control_codes"][i].items():
                            new_line.insert_before("{"+control_code+":"+value+"}")
            if tag.name == "b":
                y["bold"] = True
            elif tag.name == "i":
                y["italic"] = True
            elif tag.name == "u":
                y["underline"] = True
            elif tag.name == "br":
                props = {"color":False, "size":False, "font":False}
                if sum(y.values()):
                    new_line.insert_before("{Y:"+",".join(style[0] for style, value in y.items() if value)+"}")
                    y = {"bold":False, "italic": False, "underline":False}
                new_line = tag.find_next(string=True)
                new_line.insert_before("|")
            tag.unwrap()
            
    if sum(y.values()):
        new_line.insert_before("{Y:"+",".join(style[0] for style, value in y.items() if value)+"}")


    return  str(self)