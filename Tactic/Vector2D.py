import math

class Vector2D:
    """A two-dimensional vector with Cartesian coordinates."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        """Human-readable string representation of the vector."""
        return '{:g}i + {:g}j'.format(self.x, self.y)

    def __repr__(self):
        """Unambiguous string representation of the vector."""
        return repr((self.x, self.y))

    def dot(self, other):
        """The scalar (dot) product of self and other. Both must be vectors."""

        if not isinstance(other, Vector2D):
            raise TypeError('Can only take dot product of two Vector2D objects')
        return self.x * other.x + self.y * other.y
    # Alias the __matmul__ method to dot so we can use a @ b as well as a.dot(b).
    __matmul__ = dot

    def __sub__(self, other):
        """Vector subtraction."""
        return Vector2D(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        """Vector addition."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        """Multiplication of a vector by a scalar."""

        if isinstance(scalar, int) or isinstance(scalar, float):
            return Vector2D(self.x*scalar, self.y*scalar)
        raise NotImplementedError('Can only multiply Vector2D by a scalar')

    def __rmul__(self, scalar):
        """Reflected multiplication so vector * scalar also works."""
        return self.__mul__(scalar)

    def __neg__(self):
        """Negation of the vector (invert through origin.)"""
        return Vector2D(-self.x, -self.y)

    def __truediv__(self, scalar):
        """True division of the vector by a scalar."""
        return Vector2D(self.x / scalar, self.y / scalar)

    def __mod__(self, scalar):
        """One way to implement modulus operation: for each component."""
        return Vector2D(self.x % scalar, self.y % scalar)

    def __abs__(self):
        """Absolute value (magnitude) of the vector."""
        return math.sqrt(self.x**2 + self.y**2)

    def distance_to(self, other):
        """The distance between vectors self and other."""
        return abs(self - other)

    def to_polar(self):
        """Return the vector's components in polar coordinates."""
        return self.__abs__(), math.atan2(self.y, self.x)

    def rotate(self, angle):
        """Rotate this vector by an angle in degrees."""
        radians = math.radians(angle)
        cos = math.cos(radians)
        sin = math.sin(radians)
        
        x = self.x * cos - self.y * sin
        y = self.x * sin + self.y * cos
        
        self.x = x
        self.y = y
        
        return self

    def hypot2(self, other):
        """Calculate the square of the distance between two vectors."""
        dx = self.x - other.x
        dy = self.y - other.y
        return dx ** 2 + dy ** 2
    
    def proj(self, onto):
        """Calculate the projection of self onto the vector 'onto'."""
        dot_product = self.dot(onto)
        onto_magnitude_squared = onto.dot(onto)
        
        # Handle the zero vector case
        if onto_magnitude_squared == 0:
            raise ValueError("Cannot project onto the zero vector")
            
        scaling_factor = dot_product / onto_magnitude_squared
        return onto * scaling_factor
    
    def perpendicular(self):
        return Vector2D(-self.y, self.x)    

    def normalize(self):
        """Converts the vector to a unit vector."""
        magnitude = self.__abs__()
        if magnitude == 0:
            raise ValueError("Cannot normalize a zero vector.")
        return Vector2D(self.x / magnitude, self.y / magnitude)
    
    def reflect(self, normal):
        """Reflects the vector about a given normal."""
        # First, make sure the normal vector is actually normalized
        if abs(abs(normal) - 1) > 1e-9:
            raise ValueError("The normal vector must be normalized.")
        
        # Calculate the reflection vector using the formula
        dot_product = self.dot(normal)
        return self - 2 * dot_product * normal
    
if __name__ == '__main__':
    v1 = Vector2D(2, 5/3)
    v2 = Vector2D(3, -1.5)
    print('v1 = ', v1)
    print('repr(v2) = ', repr(v2))
    print('v1 + v2 = ', v1 + v2)
    print('v1 - v2 = ', v1 - v2)
    print('abs(v2 - v1) = ', abs(v2 - v1))
    print('-v2 = ', -v2)
    print('v1 * 3 = ', v1 * 3)
    print('7 * v2 = ', 7 * v1)
    print('v2 / 2.5 = ', v2 / 2.5)
    print('v1 % 1 = ', v1 % 1)
    print('v1.dot(v2) = v1 @ v2 = ', v1 @ v2)
    print('v1.distance_to(v2) = ',v1.distance_to(v2))
    print('v1 as polar vector, (r, theta) =', v1.to_polar())