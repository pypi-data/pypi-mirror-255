import colorsys

class RGB:
    """
    This is a class that implements the RBG system, one of PB3D's color systems. Colors are easy to use because they take three arguments with a maximum value of 255.
    """
    def __init__(self, red, green, blue):
        self.red = red/255
        self.green = green/255
        self.blue = blue/255

    def hsv(self):
        rgb = colorsys.rgb_to_hsv(self.red, self.green, self.blue)
        return HSV(rgb[0]*360, rgb[1], rgb[2])

class HSV:
    """
    This is the HSV system, one of PB3D's color systems. Takes color, saturation, and brightness parameters
    """
    def __init__(self, hue, saturation, value):
        self.hue = hue
        self.saturation = saturation
        self.value = value


    def rgb(self):
        rgb = colorsys.hsv_to_rgb(self.hue / 360, self.saturation, self.value)
        return RGB(rgb[0] * 255, rgb[1] * 255, rgb[2] * 255)