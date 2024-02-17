import math
from PB3D import Vec4, Vec3, button_dict
from OpenGL.GLU import *

class Camera:
    """
    *** caution! This is not fully functional!***
    This is the class responsible for the camera in PB3D
    """
    def __init__(self, position=Vec3(0, 0, 0), rotation=Vec4(0, 0, 0, 1)):
        self.position = position
        self.rotation = rotation
        self.move_speed = 0.1
        self.mouse_sensitivity = 0.1

    def update(self, direction, speed):
        if direction == button_dict["w"]:
            self.move_forward(speed)
        elif direction == button_dict["s"]:
            self.move_backward(speed)

        self.set_view(self.position + self.rotation)

    def move_forward(self, speed):
        self.position += self.get_forward_vector() * speed

    def move_backward(self, speed):
        self.position -= self.get_forward_vector() * speed

    def rotate(self, dx, dy):
        dx *= self.mouse_sensitivity
        dy *= self.mouse_sensitivity

        rotation_quaternion = Vec4(
            -math.sin(math.radians(dx / 2)),
            math.sin(math.radians(dy / 2)),
            math.cos(math.radians(dx / 2)),
            math.cos(math.radians(dy / 2))
        )

        self.rotation = rotation_quaternion

        forward_vector = self.get_forward_vector()
        target_position = self.position + forward_vector
        self.set_view(target_position)

    def get_forward_vector(self):
        rotated_forward = self.rotation
        return Vec3(rotated_forward.x, rotated_forward.y, rotated_forward.z)

    def set_view(self, target_position):
        target = target_position
        direction = (self.position - target).normalize()

        up = Vec3(self.position.x, self.position.y + 1, self.position.z)
        right = (up.cross(direction)).normalize()

        camera_up = direction.cross(right)

        gluLookAt(self.position.x, self.position.y, self.position.z,
                  direction.x, direction.y, direction.z,
                  camera_up.x, camera_up.y, camera_up.z
                  )
