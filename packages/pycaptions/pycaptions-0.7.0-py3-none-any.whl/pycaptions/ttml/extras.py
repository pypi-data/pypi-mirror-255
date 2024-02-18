# this structure is subject to change
TTML_PROPERTIES = {
    "backgroundClip": {
        "css": "background-clip",
        "values": ["border", "content", "padding"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "backgrounColor": {
        "css": "background-color",
        "values-map": {
            "fuchsia": "magenta",
            "aqua": "cyan"
        },
        "values": ["<color>"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "backgroundExtent": {
        "css": "background-size",
        "values": ["<extent>"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "backgroundImage": {
        "css": "background-image",
        "values": ["none", "<image>"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "backgroundOrigin": {
        "css": "background-origin",
        "values": ["border", "content", "padding"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "backgroundPosition": {
        "css": "background-position",
        "values": ["<position>"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "backgroundRepeat": {
        "css": "background-repeat",
        "values-map": {
            "repeatX": "repeat-x",
            "repeatY": "repeat-y",
            "noRepeat": "no-repeat"
        },
        "values": ["repeat", "repeatX", "repeatY", "noRepeat"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "border": {
        "css": "border",
        "values": ["<border>"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "bpd": {
        "css": None,
        "values": ["<measures>"],
        "tags": ["body", "div", "p", "span"]
    },
    "color": {
        "css": "color",
        "values-map": {
            "fuchsia": "magenta",
            "aqua": "cyan"
        },
        "values": ["<color>"],
        "tags": ["span"]
    },
    "direction": {
        "css": "direction",
        "values": ["ltr", "rtl"],
        "tags": ["p", "span"]
    },
    "disparity": {
        "css": None,
        "values": ["<length>"],
        "tags": ["div", "p", "region"]
    },
    "display": {
        "css": "display",
        "values-map": {
            "inlineBlock": "inline-block"
        },
        "values": ["auto", "none", "inlineBlock"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "displayAlign": {
        "css": "display-align",
        "values-map": {
            "before": "flex-start",
            "after": "flex-end",
            "justify": "space-between"
        },
        "values": ["before", "center", "after", "justify"],
        "tags": ["body", "div", "p", "region"]
    },
    "extent": {
        "css": None,
        "values": ["<extent>"],
        "tags": ["tt", "div", "image", "p", "region"]
    },
    "fontFamily": {
        "css": "font-family",
        "values": ["<font-families>"],
        "tags": ["span"]
    },
    "fontKerning": {
        "css": "font-kerning",
        "values": ["none", "normal"],
        "tags": ["span"]
    },
    "fontSelectionStrategy": {
        "css": None,
        "values": ["auto", "character"],
        "tags": ["span"]
    },
    "fontShear": {
        "css": None, #skewX skewY
        "values": ["<percentage>"],
        "tags": ["span"]
    },
    "fontSize": {
        "css": "font-size",
        "values": ["<font-size>"],
        "tags": ["span"]
    },
    "fontStyle": {
        "css": "font-style",
        "values": ["normal", "italic", "oblique"],
        "tags": ["span"]
    },
    "fontVariant": {
        "css": None,
        "values": ["<font-variant>"],
        #font-variant-east-asian: Only full-width, rubyfont-variant-position: normal, sub, superfont-feature-settings: Only hwid
        "tags": ["span"]
    },
    "fontWeight": {
        "css": "font-weight",
        "values": ["normal", "bold"],
        "tags": ["span"]
    },
    "ipd": {
        "css": None,
        "values": ["<measure>"],
        "tags": ["body", "div", "p", "span"]
    },
    "letterSpacing": {
        "css": "letter-spacing",
        "values": ["normal", "<length>"],
        "tags": ["span"]
    },
    "lineHeight": {
        "css": "line-height",
        "values": ["normal", "<length>"],
        "tags": ["p"]
    },
    "lineShear": {
        "css": None, #skewX skewY
        "values": ["<percentage>"],
        "tags": ["p"]
    },
    "luminanceGain": {
        "css": None,
        "values": ["<non-negative-number>"],
        "tags": ["region"]
    },
    "opacity": {
        "css": "opacity",
        "values": ["<alpha>"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "origin": {
        "css": None,
        "values": ["<origin>"],
        "tags": ["div", "p", "region"]
    },
    "overflow": {
        "css": "overflow",
        "values": ["visible", "hidden"],
        "tags": ["region"]
    },
    "padding": {
        "css": "padding",
        "values": ["<padding>"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "position": {
        "css": "background-position",
        "values": ["<position>"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "ruby": {
        "css": "ruby",
        "values": ["none", "container", "base", "baseContainer", "text", "textContainer", "delimiter"],
        "tags": ["span"]
    },
    "rubyAlign": {
        "css": "ruby-align",
        "values": ["start", "center", "end", "spaceAround", "spaceBetween", "withBase"],
        "tags": ["span"]
    },
    "rubyPosition": {
        "css": None,
        "values": ["before", "after", "outside"],
        "tags": ["span"]
    },
    "rubyReserve": {
        "css": None,
        "values": ["<ruby-reserve>"],
        "tags": ["p"]
    },
    "shear": {
        "css": None, #skewX skewY
        "values": ["<percentage>"],
        "tags": ["p"]
    },
    "showBackground": {
        "css": None,
        "values": ["always", "whenActive"],
        "tags": ["region"]
    },
    "textAlign": {
        "css": "text-align",
        "values": ["left", "center", "right", "start", "end", "justify"],
        "tags": ["p"]
    },
    "textCombine": {
        "css": "text-combine-upright",
        "values": ["<text-combine>"],
        "tags": ["span"]
    },
    "textDecoration": {
        "css": "text-decoration",
        "values-map": {
            "line-through": "lineThrough",
            "noUnderline": None,
            "noLineThrough": None,
            "noOverline": None
        },
        "values": ["<text-decoration>"],
        "tags": ["span"]
    },
    "textEmphasis": {
        "css": "text-emphasis-position",
        #emphasis-style maps to text-emphasis-style; emphasis-color maps to text-emphasis-color; emphasis-position maps to text-emphasis-position
        "values": ["<text-emphasis>"],
        "tags": ["span"]
    },
    "textOrientation": {
        "css": "text-orientation",
        "values": ["mixed", "sideways", "upright"],
        "tags": ["span"]
    },
    "textOutline": {
        "css": None,
        "values": ["<text-outline>"],
        "tags": ["span"]
    },
    "textShadow": {
        "css": "text-shadow",
        "values": ["<text-shadow>"],
        "tags": ["span"]
    },
    "unicodeBidi": {
        "css": "unicode-bidi",
        "values-map": {
            "isolate": None
        },
        "values": ["normal", "embed", "bidiOverride", "isolate"],
        "tags": ["p", "span"]
    },
    "visibility": {
        "css": "visibility",
        "values": ["visible", "hidden"],
        "tags": ["body", "div", "image", "p", "region", "span"]
    },
    "wrapOption": {
        "css": None,
        "values": ["wrap", "noWrap"],
        "tags": ["span"]
    },
    "writingMode": {
        "css": None,
        "values": ["lrtb", "rltb", "tbrl", "tblr", "lr", "rl", "tb"],
        "tags": ["region"]
    },
    "zIndex": {
        "css": "z-index",
        "values": ["auto", "<integer>"],
        "tags": ["region"]
    }
}

TTML_FROM_CSS = {
    "background-clip": "backgroundClip",
    "background-color": "backgrounColor",
    "background-size": "backgroundExtent",
    "background-image": "backgroundImage",
    "background-origin": "backgroundOrigin",
    "background-position": "position",
    "background-repeat": "backgroundRepeat",
    "border": "border",
    "color": "color",
    "direction": "direction",
    "display": "display",
    "display-align": "displayAlign",
    "font-family": "fontFamily",
    "font-kerning": "fontKerning",
    "font-size": "fontSize",
    "font-style": "fontStyle",
    "font-weight": "fontWeight",
    "letter-spacing": "letterSpacing",
    "line-height": "lineHeight",
    "opacity": "opacity",
    "overflow": "overflow",
    "padding": "padding",
    "ruby": "ruby",
    "ruby-align": "rubyAlign",
    "text-align": "textAlign",
    "text-combine-upright": "textCombine",
    "text-decoration": "textDecoration",
    "text-emphasis-position": "textEmphasis",
    "text-orientation": "textOrientation",
    "text-shadow": "textShadow",
    "unicode-bidi": "unicodeBidi",
    "visibility": "visibility",
    "z-index": "zIndex"
}

def tryparse(func):
    def wrapper(value):
        try:
            return func(value=value)
        except:
            return False
    return wrapper

@tryparse
def checkAlpha(value):
    if not value or value == "NaN" or value == "none":
        return 0
    else:
        return max(min(1, float(value)), 0)
    
def checkBorder(value):
    #<border-thickness> || <border-style> || <border-color> || <border-radii>
    pass

def checkColor(value):
    """
    : "#" rrggbb
  | "#" rrggbbaa
  | "rgb(" r-value "," g-value "," b-value ")"
  | "rgba(" r-value "," g-value "," b-value "," a-value ")"
  | <named-color>
    """

def checkExtent(value):
    """
    : "auto"
  | "contain"
  | "cover"
  | <measure> <lwsp> <measure>
    """

def checkFontFamilies(value):
    """
    <font-families>
  : font-family (<lwsp>? "," <lwsp>? font-family)*

font-family
  : <family-name>
  | <generic-family-name>
    """

def checkFontSize(value):
    """
    <font-size>
  : <length> (<lwsp> <length>)?
    """

def checkFontVariant(value):
    """
    <font-variant>
  : "normal"
  | ("super" | "sub") || ("full" | "half") || "ruby"
    """

def checkImage(value):
    """
    <image>
  : <uri>
    """

@tryparse
def checkInteger(value):
    return str(int(value)) == value

def checkLength(value):
    """
    <length>
  : scalar
  | <percentage>

scalar
  : <number> units

units
  : "px"
  | "em"
  | "c"                                     // abbreviation of "cell"
  | "rw"
  | "rh"
    """

def checkMeasure(value):
    """
    : "auto"
  | "fitContent"
  | "maxContent"
  | "minContent"
  | <length>
    """

@tryparse
def checkPositiveInteger(value):
    return int(value) > 0

def checkOrigin(value):
    """
    <origin>
  : "auto"
  | <length> <lwsp> <length>
    """

def checkPadding(value):
    """
    <padding>
  : <length> <lwsp> <length> <lwsp> <length> <lwsp> <length>
  | <length> <lwsp> <length> <lwsp> <length>
  | <length> <lwsp> <length>
  | <length>
    """

def checkPercentage(value):
    """
    <percentage>
  : <number> "%"
    """

def checkPosition(value):
    """
    <position>
  : offset-position-h                             // single component value
  | edge-keyword-v                                // single component value
  | offset-position-h <lwsp> offset-position-v    // two component value
  | position-keyword-v <lwsp> position-keyword-h  // two component value
  | position-keyword-h <lwsp> edge-offset-v       // three component value
  | position-keyword-v <lwsp> edge-offset-h       // three component value
  | edge-offset-h <lwsp> position-keyword-v       // three component value
  | edge-offset-v <lwsp> position-keyword-h       // three component value
  | edge-offset-h <lwsp> edge-offset-v            // four component value
  | edge-offset-v <lwsp> edge-offset-h            // four component value

offset-position-h
  : position-keyword-h
  | <length>

offset-position-v
  : position-keyword-v
  | <length>

edge-offset-h
  : edge-keyword-h <lwsp> <length>

edge-offset-v
  : edge-keyword-v <lwsp> <length>

position-keyword-h
  : "center"
  | edge-keyword-h

position-keyword-v
  : "center"
  | edge-keyword-v

edge-keyword-h
  : "left"
  | "right"

edge-keyword-v
  : "top"
  | "bottom"
    """

def checkRubyReserve(value):
    """
    <ruby-reserve>
  : "none"
  | ("both" | <annotation-position>) (<lwsp> <length>)?
    """

def checkTextCombine(value):
    """
    <text-combine>
  : "none"
  | "all"
    """

def checkTextDecoration(value):
    """
    <text-decoration>
  : "none"
  | (("underline" | "noUnderline") || ("lineThrough" | "noLineThrough") || ("overline" | "noOverline"))
    """

def checkTextEmphasis():
    """
    <text-emphasis>
  : <emphasis-style> || <emphasis-color> || <emphasis-position>
    """

def checkTextOutline(value):
    """
    <text-outline>
  : "none"
  | (<color> <lwsp>)? <length> (<lwsp> <length>)?
    """

def checkTextShadow(value):
    """
    <text-shadow>
  : "none"
  | <shadow> (<lwsp>? "," <lwsp>? <shadow>)*
    """


TTML_VALUE_GROUPS = {
    "<alpha>": checkAlpha,
    "<border>": checkBorder,
    "<color>": checkColor,
    "<extent>": checkExtent,
    "<font-families>": checkFontFamilies,
    "<font-size>": checkFontSize,
    "<font-variant>": checkFontVariant,
    "<image>": checkImage,
    "<integer>": checkInteger,
    "<length>": checkLength,
    "<measures>": checkMeasure,
    "<non-negative-number>": checkPositiveInteger,
    "<origin>": checkOrigin,
    "<padding>": checkPadding,
    "<percentage>": checkPercentage,
    "<position>": checkPosition,
    "<ruby-reserve>": checkRubyReserve,
    "<text-combine>": checkTextCombine,
    "<text-decoration>": checkTextDecoration,
    "<text-emphasis>": checkTextEmphasis,
    "<text-outline>": checkTextOutline,
    "<text-shadow>": checkTextShadow,
}