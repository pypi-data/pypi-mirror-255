import sys

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
from PB3D.math import Vec4, RGB
from PB3D.entity import entities, delete
from OpenGL.GL import glEnable, GL_DEPTH_TEST
from numba import jit, NumbaWarning
import warnings

warnings.filterwarnings("ignore", category=NumbaWarning)


def change_color(color: RGB):
    glClearColor(color.red, color.green, color.blue, 1)

class Window:
    def __init__(self, size: tuple[int, int], color: RGB):
        self.width = size[0]
        self.height = size[1]
        self.color = color


@jit
def init(size: tuple[int, int], color: RGB):
    """
    This is a function that initializes the 3d mode of PB3D. Here you can adjust the color and size.

    :param size:
    :param color:
    :return:
    """
    pygame.init()
    pygame.display.set_mode(size, DOUBLEBUF | OPENGL)

    glEnable(GL_DEPTH_TEST)

    gluPerspective(45, (size[0] / size[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)
    glClearColor(color.red, color.green, color.blue, 1)

    print("\nOpenGL Version:", glGetString(GL_VERSION))
    print("OpenGL Vendor:", glGetString(GL_VENDOR))
    print("OpenGL Renderer:", glGetString(GL_RENDERER))
    print("\nVersion 1.0.1")

    return Window(size, color)

@jit
def init_2d(size: tuple[int, int]):
    """
    This is a function that initializes the 2d mode of PB3D. Here you can adjust the color and size.
    :param size:
    :return:
    """
    pygame.init()
    pygame.display.set_mode(size, DOUBLEBUF | OPENGL)
    glOrtho(0, size[0], size[1], 0, -1, 1)

    print("\nOpenGL Version:", glGetString(GL_VERSION))
    print("OpenGL Vendor:", glGetString(GL_VENDOR))
    print("OpenGL Renderer:", glGetString(GL_RENDERER))
    print("\nVersion 0.0.3")

@jit
def update():
    pygame.display.flip()

@jit
def clean():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

@jit
def turn(vec: Vec4):
    """
    This is the function responsible for adjusting the field of view in PB3D
    :param vec
    :return:
    """
    glRotatef(vec.w, vec.x, vec.y, vec.z)

@jit
def loop(func1=None, func2=None, func3=None):
    """
    This is a function that manages loops in PB3D. Basically, you can install a model in func1 and use the keyboard in func2.
    :param func1:
    :param func2:
    :return:
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if func2 != None:
                    func2(event)

            if event.type == pygame.MOUSEMOTION:
                dx, dy = event.rel
                if func3 != None:
                    func3(dx, dy)

        clean()
        if func1 != None:
            func1()

        for entity in entities:
            entity.draw()

            if entity.position.size > round(sys.maxsize / 8):
                delete(entity)

        update()

Event = pygame.event.Event