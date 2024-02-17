import math

class BaseVec3:
    """
    This is the base class for classes expressing coordinates in PB3D and supports four arithmetic operations on coordinates.
    """
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.size = (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def __add__(self, other):
        return BaseVec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return BaseVec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return BaseVec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        if scalar != 0:
            return BaseVec3(self.x / scalar, self.y / scalar, self.z / scalar)
        else:
            raise ValueError("Cannot divide by zero.")

    def __str__(self):
        return f"Vec3(x={self.x}, y={self.y}, z={self.z})"

class Vec3(BaseVec3):
    """
    This is a class that represents coordinates in PB3D and provides several mathematical functions.
    """
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        if self.size > 0:
            self.unit = BaseVec3((self.x / self.size), (self.y / self.size), (self.z / self.size))
            self.direction = BaseVec3(
                math.acos(self.unit.x),
                math.acos(self.unit.y),
                math.acos(self.unit.z)
            )
        else:
            self.unit = BaseVec3(0, 0, 0)
            self.direction = BaseVec3(0, 0, 0)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        mag = self.magnitude()
        if mag != 0:
            return Vec3(self.x / mag, self.y / mag, self.z / mag)
        else:
            return Vec3(0, 0, 0)

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def angle(self, other, in_degrees=False):
        dot_product = self.dot_product(other)
        mag_self = self.magnitude()
        mag_other = other.magnitude()

        if mag_self != 0 and mag_other != 0:
            cos_theta = dot_product / (mag_self * mag_other)
            theta_rad = math.acos(max(min(cos_theta, 1.0), -1.0))

            if in_degrees:
                return math.degrees(theta_rad)
            else:
                return theta_rad
        else:
            raise ValueError("Cannot calculate angle for zero vectors.")

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        if scalar != 0:
            return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
        else:
            raise ValueError("Cannot divide by zero.")

class Vec4:
    def __init__(self, a, b, c, d):
        self.x = a
        self.y = b
        self.z = c
        self.w = d

    def __repr__(self):
        return f"Vec4({self.x}, {self.y}, {self.z}, {self.w})"

    def __add__(self, other):
        if isinstance(other, Vec4):
            return Vec4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
        elif isinstance(other, (int, float)):
            return Vec4(self.x + other, self.y + other, self.z + other, self.w + other)
        else:
            raise TypeError("Unsupported operand type for +: Vec4 and {}".format(type(other)))

    def __sub__(self, other):
        if isinstance(other, Vec4):
            return Vec4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)
        elif isinstance(other, (int, float)):
            return Vec4(self.x - other, self.y - other, self.z - other, self.w - other)
        else:
            raise TypeError("Unsupported operand type for -: Vec4 and {}".format(type(other)))

    def __mul__(self, other):
        if isinstance(other, Vec4):
            a1, b1, c1, d1 = self.x, self.y, self.z, self.w
            a2, b2, c2, d2 = other.x, other.y, other.z, other.w

            a = a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2
            b = a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2
            c = a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2
            d = a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2

            return Vec4(a, b, c, d)
        elif isinstance(other, (int, float)):
            return Vec4(self.x * other, self.y * other, self.z * other, self.w * other)
        else:
            raise TypeError("Unsupported operand type for *: Vec4 and {}".format(type(other)))

    def conjugate(self):
        return Vec4(self.x, -self.y, -self.z, -self.w)

    def normalize(self):
        norm = (self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2) ** 0.5
        if norm == 0:
            return Vec4(0, 0, 0, 0)
        else:
            return Vec4(self.x / norm, self.y / norm, self.z / norm, self.w / norm)

    def __truediv__(self, other):
        if isinstance(other, Vec4):
            try:
                x = self.x / other.x
            except ZeroDivisionError:
                x = 0

            try:
                y = self.y / other.y
            except ZeroDivisionError:
                y = 0

            try:
                z = self.z / other.z
            except ZeroDivisionError:
                z = 0

            try:
                w = self.w / other.w
            except ZeroDivisionError:
                w = 0

            return Vec4(x, y, z, w)
        elif isinstance(other, (int, float)):
            if other != 0:
                return Vec4(self.x / other, self.y / other, self.z / other, self.w / other)
            else:
                raise ZeroDivisionError("division by zero")
        else:
            raise TypeError("Unsupported operand type for /: Vec4 and {}".format(type(other)))

    def rotate_vector(self, v):
        q_conj = Vec4(self.w, -self.x, -self.y, -self.z)
        qv = Vec4(0, v.x, v.y, v.z)
        rotated_v = (self * qv * q_conj).xyz()
        return Vec4(rotated_v.x, rotated_v.y, rotated_v.z, 0)

    def xyz(self):
        return Vec3(self.x, self.y, self.z)

i = Vec4(1, 0, 0, 0)
j = Vec4(0, 1, 0, 0)
k = Vec4(0, 0, 1, 0)
r = Vec4(0, 0, 0, 1)
