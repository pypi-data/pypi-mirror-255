from ..styling import changeStyleOption


class StyleOptions:
    style_option = ["full"]
    style_value = "full"
    lines_value = -1

    @property
    def lines(self):
        """
        If the value is invalid it will default to -1.
        """
        return self.lines_value

    @lines.setter
    def lines(self, value):
        if isinstance(value, int) and value >= -1:
            self.lines_value = value
        else:
            print(f"Invalid line value {value}. Expected: n >= -1")
            self.lines_value = -1

    @property
    def style(self):
        """
        Valid values "full", "none", None
        If the value is invalid it will default to None
        """
        return self.style_value

    @style.setter
    def style(self, value):
        if value == None:
            self.style_value = None
        elif isinstance(value, str):
            value = value.lower()
            if value == "none":
                self.style_value = None
            elif value in self.style_option:
                self.style_value = value
            else:
                print(f"Invalid style option {value}. Expected: none {' '.join(self.style_option)}")
                self.style_value = None
        else:      
            print(f"Invalid style option {value}. Expected: none {' '.join(self.style_option)}")
            self.style_value = None
        changeStyleOption(self.style_value)