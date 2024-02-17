from OpenGL.GLU import *
from pywavefront import Wavefront
from PB3D.math import Vec3, RGB
from PB3D.math.vector import BaseVec3
from OpenGL.GL import *

entities = []
GRAVITY = Vec3(9.8, 9.8, 9.8)

def mouse_pos(x, y):
    """
    This is a function that obtains the mouse click entity in PB3D.
    :param x:
    :param y:
    :return:
    """
    global selected_shape
    viewport = glGetIntegerv(GL_VIEWPORT)
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)

    y = viewport[3] - y
    click_pos = gluUnProject(x, y, 0.0, modelview, projection, viewport)

    return click_pos



class PositionEntity:
    def __init__(self, position=BaseVec3(0, 0, 0)):
        self.position = position

    def __str__(self):
        return f"Position {self.position}"

class Scale:
    def __init__(self, num):
        self.scale = num

class MathEntity(PositionEntity, Scale):
    def __init__(self, position=BaseVec3(0, 0, 0), num=1):
        PositionEntity.__init__(self, position)
        Scale.__init__(self, num)


class Entity(MathEntity):
    """
    This is a class that displays the basic shapes of PB3D. This class supports color, position, etc. and also has an obj file loading function.
    """
    def __init__(self, file_path="cube", color=RGB(1, 1, 1), position=BaseVec3(0, 0, 0), scale=1, mass=Vec3(1, 1, 1)):
        super().__init__(
            position=position,
            num=scale
        )
        self.file_path = file_path
        self.color = color
        self.selected = False
        self.velocity = Vec3(0, 0, 0)
        self.mass = Vec3(self.scale, self.scale, self.scale)

        if file_path and file_path.endswith(".obj"):
            try:
                self.load_obj(file_path)
            except FileNotFoundError:
                self.obj_mesh = None
                self.vertices = [
                    (1 * self.scale + self.position.x, -1 * self.scale + self.position.y,
                     -1 * self.scale + self.position.z),
                    (1 * self.scale + self.position.x, 1 * self.scale + self.position.y,
                     -1 * self.scale + self.position.z),
                    (-1 * self.scale + self.position.x, 1 * self.scale + self.position.y,
                     -1 * self.scale + self.position.z),
                    (-1 * self.scale + self.position.x, -1 * self.scale + self.position.y,
                     -1 * self.scale + self.position.z),
                    (1 * self.scale + self.position.x, -1 * self.scale + self.position.y,
                     1 * self.scale + self.position.z),
                    (1 * self.scale + self.position.x, 1 * self.scale + self.position.y,
                     1 * self.scale + self.position.z),
                    (-1 * self.scale + self.position.x, -1 * self.scale + self.position.y,
                     1 * self.scale + self.position.z),
                    (-1 * self.scale + self.position.x, 1 * self.scale + self.position.y,
                     1 * self.scale + self.position.z)
                ]

        elif file_path == "cube":
            self.obj_mesh = None

        self.draw()
        entities.append(self)

    def load_obj(self, file_path):
        self.obj_mesh = Wavefront(file_path)

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)

        try:
            if self.obj_mesh:
                self.draw_obj()
            else:
                self.vertices = [
                    (1 * self.scale + self.position.x, -1 * self.scale + self.position.y,
                     -1 * self.scale + self.position.z),
                    (1 * self.scale + self.position.x, 1 * self.scale + self.position.y,
                     -1 * self.scale + self.position.z),
                    (-1 * self.scale + self.position.x, 1 * self.scale + self.position.y,
                     -1 * self.scale + self.position.z),
                    (-1 * self.scale + self.position.x, -1 * self.scale + self.position.y,
                     -1 * self.scale + self.position.z),
                    (1 * self.scale + self.position.x, -1 * self.scale + self.position.y,
                     1 * self.scale + self.position.z),
                    (1 * self.scale + self.position.x, 1 * self.scale + self.position.y,
                     1 * self.scale + self.position.z),
                    (-1 * self.scale + self.position.x, -1 * self.scale + self.position.y,
                     1 * self.scale + self.position.z),
                    (-1 * self.scale + self.position.x, 1 * self.scale + self.position.y,
                     1 * self.scale + self.position.z)
                ]
                self.draw_cube()
        except AttributeError:
            self.vertices = [
                (1 * self.scale + self.position.x, -1 * self.scale + self.position.y, -1 * self.scale + self.position.z),
                (1 * self.scale + self.position.x, 1 * self.scale + self.position.y, -1 * self.scale + self.position.z),
                (-1 * self.scale + self.position.x, 1 * self.scale + self.position.y, -1 * self.scale + self.position.z),
                (-1 * self.scale + self.position.x, -1 * self.scale + self.position.y, -1 * self.scale + self.position.z),
                (1 * self.scale + self.position.x, -1 * self.scale + self.position.y, 1 * self.scale + self.position.z),
                (1 * self.scale + self.position.x, 1 * self.scale + self.position.y, 1 * self.scale + self.position.z),
                (-1 * self.scale + self.position.x, -1 * self.scale + self.position.y, 1 * self.scale + self.position.z),
                (-1 * self.scale + self.position.x, 1 * self.scale + self.position.y, 1 * self.scale + self.position.z)
            ]
            self.draw_cube()

        glPopMatrix()

    def draw_cube(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)

        if self.color:
            glColor3fv((self.color.red, self.color.green, self.color.blue))

        glBegin(GL_QUADS)
        for surface in ((0, 1, 2, 3), (3, 2, 7, 6), (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6)):
            for vertex_i in surface:
                try:
                    vertex = self.vertices[vertex_i]
                    glVertex3fv(vertex)
                except:
                    pass
        glEnd()

        glPopMatrix()

    def draw_obj(self):
        if self.selected:
            glColor3fv((1, 0, 0))
        elif self.color:
            glColor3fv((self.color.red, self.color.green, self.color.blue))

        glBegin(GL_TRIANGLES)
        for face in self.obj_mesh.mesh_list[0].faces:
            for vertex_i in face:
                vertex = self.obj_mesh.mesh_list[0].vertices[vertex_i]
                glVertex3fv(vertex)
        glEnd()

    def is_clicked(self, click_pos):
        if self.obj_mesh:
            min_x = min(v[0] for v in self.obj_mesh.mesh_list[0].vertices) + self.position.x
            max_x = max(v[0] for v in self.obj_mesh.mesh_list[0].vertices) + self.position.x
            min_y = min(v[1] for v in self.obj_mesh.mesh_list[0].vertices) + self.position.y
            max_y = max(v[1] for v in self.obj_mesh.mesh_list[0].vertices) + self.position.y
            min_z = min(v[2] for v in self.obj_mesh.mesh_list[0].vertices) + self.position.z
            max_z = max(v[2] for v in self.obj_mesh.mesh_list[0].vertices) + self.position.z
        else:
            min_x = min(v[0] for v in self.vertices) + self.position.x
            max_x = max(v[0] for v in self.vertices) + self.position.x
            min_y = min(v[1] for v in self.vertices) + self.position.y
            max_y = max(v[1] for v in self.vertices) + self.position.y
            min_z = min(v[2] for v in self.vertices) + self.position.z
            max_z = max(v[2] for v in self.vertices) + self.position.z

        return min_x <= click_pos[0] <= max_x and min_y <= click_pos[1] <= max_y and min_z <= click_pos[2] <= max_z

    def get_position(self):
        return self.position

    def set_position(self, position):
        if isinstance(position, tuple):
            self.position = Vec3(position[0], position[1], position[2])
        elif isinstance(position, Vec3):
            self.position = position

    def move(self):
        """
        This is the method responsible for the position movement function of the Shape.

        :return:
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        displacement = self.velocity * 1/60

        self.position += displacement

        if self.file_path and self.file_path.endswith(".obj"):
            self.load_obj(self.file_path)
        elif self.file_path == "cube":
            self.vertices = [
                (1 * self.scale + self.position.x, -1 * self.scale + self.position.y, -1 * self.scale + self.position.z),
                (1 * self.scale + self.position.x, 1 * self.scale + self.position.y, -1 * self.scale + self.position.z),
                (-1 * self.scale + self.position.x, 1 * self.scale + self.position.y, -1 * self.scale + self.position.z),
                (-1 * self.scale + self.position.x, -1 * self.scale + self.position.y, -1 * self.scale + self.position.z),
                (1 * self.scale + self.position.x, -1 * self.scale + self.position.y, 1 * self.scale + self.position.z),
                (1 * self.scale + self.position.x, 1 * self.scale + self.position.y, 1 * self.scale + self.position.z),
                (-1 * self.scale + self.position.x, -1 * self.scale + self.position.y, 1 * self.scale + self.position.z),
                (-1 * self.scale + self.position.x, 1 * self.scale + self.position.y, 1 * self.scale + self.position.z)
            ]
            self.draw_cube()

    def gravity(self):
        for entity in entities:
            if isinstance(entity, Entity) and entity != self:
                displacement = entity.position - self.position
                distance_squared = displacement.dot_product(displacement)
                force_direction = displacement.normalize()
                force_magnitude = GRAVITY * ((self.mass * entity.mass) / distance_squared)
                force = force_direction * force_magnitude
                acceleration = force / self.mass
                self.velocity += acceleration * (1 / 60)
        self.move()


def delete(entity: Entity):
    entity.position = Vec3(0, 0, 0)
    entity.scale = 0
    entity.vertices = []
    del entity

class Shape2d:
    """
    *** caution! This does not add any new features in version 0.0.3. ***
    This is a class that represents 2d entities in PB3D.
    """
    def __init__(self, file_path="square", color=None, position=(0, 0)):
        self.file_path = file_path
        self.color = color
        self.position = position
        self.selected = False

        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], 0.0)

        if self.selected:
            glColor3fv((1, 0, 0))
        elif self.color:
            glColor3fv(self.color)

        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(50, 0)
        glVertex2f(50, 50)
        glVertex2f(0, 50)
        glEnd()

        glPopMatrix()

    def is_clicked(self, click_pos):
        min_x = self.position[0]
        max_x = self.position[0] + 50
        min_y = self.position[1]
        max_y = self.position[1] + 50

        return min_x <= click_pos[0] <= max_x and min_y <= click_pos[1] <= max_y

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    def move(self, x, y):
        self.position = (self.position[0] + x, self.position[1] + y)


class Light:
    """
    *** caution! This is not a complete feature yet. ***
    This is a class that represents light in PB3D.
    """
    def __init__(self, position=(0, 0, 0), ambient=1, diffuse=1, specular=1):
        self.position = position
        self.ambient = [ambient, ambient, ambient, 1.0]
        self.diffuse = [diffuse, diffuse, diffuse, 1.0]
        self.specular = [specular, specular, specular, 1.0]

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        self.update()

    def update(self):
        glLightfv(GL_LIGHT0, GL_POSITION, self.position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular)

    def set_position(self, position):
        self.position = position
        self.update()

    def set_ambient(self, ambient):
        self.ambient = [ambient, ambient, ambient, 1.0]
        self.update()

    def set_diffuse(self, diffuse):
        self.diffuse = [diffuse, diffuse, diffuse, 1.0]
        self.update()

    def set_specular(self, specular):
        self.specular = [specular, specular, specular, 1.0]
        self.update()
