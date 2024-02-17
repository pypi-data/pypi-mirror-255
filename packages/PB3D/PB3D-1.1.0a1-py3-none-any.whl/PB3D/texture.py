
from OpenGL.GL import *
from pygame.image import load, tostring

class Texture:
    def __init__(self, texture_path: str):
        self.texture_surface = load(texture_path)
        self.texture_data = tostring(self.texture_surface, "RGBA", 1)
        self.width, self.height = self.texture_surface.get_size()
        self.texture_id = glGenTextures(1)