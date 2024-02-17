import sys
import typing
from . import kdtree
from . import noise
from . import bvhtree
from . import geometry
from . import interpolate

GenericType = typing.TypeVar("GenericType")

class Color:
    """This object gives access to Colors in Blender. Most colors returned by Blender APIs are in scene linear color space, as defined by the OpenColorIO configuration. The notable exception is user interface theming colors, which are in sRGB color space. :arg rgb: (r, g, b) color values :type rgb: 3d vector"""

    b: float
    """ Blue color channel.

    :type: float
    """

    g: float
    """ Green color channel.

    :type: float
    """

    h: float
    """ HSV Hue component in [0, 1].

    :type: float
    """

    hsv: typing.Union[typing.Sequence[float], "Vector"]
    """ HSV Values in [0, 1].

    :type: typing.Union[typing.Sequence[float], 'Vector']
    """

    is_frozen: bool
    """ True when this object has been frozen (read-only).

    :type: bool
    """

    is_valid: bool
    """ True when the owner of this data is valid.

    :type: bool
    """

    is_wrapped: bool
    """ True when this object wraps external data (read-only).

    :type: bool
    """

    owner: typing.Any
    """ The item this is wrapping or None (read-only)."""

    r: float
    """ Red color channel.

    :type: float
    """

    s: float
    """ HSV Saturation component in [0, 1].

    :type: float
    """

    v: float
    """ HSV Value component in [0, 1].

    :type: float
    """

    @staticmethod
    def copy() -> "Color":
        """Returns a copy of this color.

        :rtype: 'Color'
        :return: A copy of the color.
        """
        ...

    @staticmethod
    def freeze() -> "Color":
        """Make this object immutable. After this the object can be hashed, used in dictionaries & sets.

        :rtype: 'Color'
        :return: An instance of this object.
        """
        ...

    @staticmethod
    def from_aces_to_scene_linear() -> "Color":
        """Convert from ACES2065-1 linear to scene linear color space.

        :rtype: 'Color'
        :return: A color in scene linear color space.
        """
        ...

    @staticmethod
    def from_rec709_linear_to_scene_linear() -> "Color":
        """Convert from Rec.709 linear color space to scene linear color space.

        :rtype: 'Color'
        :return: A color in scene linear color space.
        """
        ...

    @staticmethod
    def from_scene_linear_to_aces() -> "Color":
        """Convert from scene linear to ACES2065-1 linear color space.

        :rtype: 'Color'
        :return: A color in ACES2065-1 linear color space.
        """
        ...

    @staticmethod
    def from_scene_linear_to_rec709_linear() -> "Color":
        """Convert from scene linear to Rec.709 linear color space.

        :rtype: 'Color'
        :return: A color in Rec.709 linear color space.
        """
        ...

    @staticmethod
    def from_scene_linear_to_srgb() -> "Color":
        """Convert from scene linear to sRGB color space.

        :rtype: 'Color'
        :return: A color in sRGB color space.
        """
        ...

    @staticmethod
    def from_scene_linear_to_xyz_d65() -> "Color":
        """Convert from scene linear to CIE XYZ (Illuminant D65) color space.

        :rtype: 'Color'
        :return: A color in XYZ color space.
        """
        ...

    @staticmethod
    def from_srgb_to_scene_linear() -> "Color":
        """Convert from sRGB to scene linear color space.

        :rtype: 'Color'
        :return: A color in scene linear color space.
        """
        ...

    @staticmethod
    def from_xyz_d65_to_scene_linear() -> "Color":
        """Convert from CIE XYZ (Illuminant D65) to scene linear color space.

        :rtype: 'Color'
        :return: A color in scene linear color space.
        """
        ...

    def __init__(self, rgb=(0.0, 0.0, 0.0)) -> typing.Any:
        """

        :rtype: typing.Any
        """
        ...

    def __add__(self, other: typing.Union[typing.Sequence[float], "Color"]) -> "Color":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Color']
        :rtype: 'Color'
        """
        ...

    def __sub__(self, other: typing.Union[typing.Sequence[float], "Color"]) -> "Color":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Color']
        :rtype: 'Color'
        """
        ...

    def __mul__(self, other: typing.Union[int, float]) -> "Color":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Color'
        """
        ...

    def __truediv__(self, other: typing.Union[int, float]) -> "Color":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Color'
        """
        ...

    def __radd__(self, other: typing.Union[typing.Sequence[float], "Color"]) -> "Color":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Color']
        :rtype: 'Color'
        """
        ...

    def __rsub__(self, other: typing.Union[typing.Sequence[float], "Color"]) -> "Color":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Color']
        :rtype: 'Color'
        """
        ...

    def __rmul__(self, other: typing.Union[int, float]) -> "Color":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Color'
        """
        ...

    def __rtruediv__(self, other: typing.Union[int, float]) -> "Color":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Color'
        """
        ...

    def __iadd__(self, other: typing.Union[typing.Sequence[float], "Color"]) -> "Color":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Color']
        :rtype: 'Color'
        """
        ...

    def __isub__(self, other: typing.Union[typing.Sequence[float], "Color"]) -> "Color":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Color']
        :rtype: 'Color'
        """
        ...

    def __imul__(self, other: typing.Union[int, float]) -> "Color":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Color'
        """
        ...

    def __itruediv__(self, other: typing.Union[int, float]) -> "Color":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Color'
        """
        ...

class Euler:
    """This object gives access to Eulers in Blender. :arg angles: Three angles, in radians. :type angles: 3d vector :arg order: Optional order of the angles, a permutation of ``XYZ``. :type order: str"""

    is_frozen: bool
    """ True when this object has been frozen (read-only).

    :type: bool
    """

    is_valid: bool
    """ True when the owner of this data is valid.

    :type: bool
    """

    is_wrapped: bool
    """ True when this object wraps external data (read-only).

    :type: bool
    """

    order: str
    """ Euler rotation order.

    :type: str
    """

    owner: typing.Any
    """ The item this is wrapping or None (read-only)."""

    x: float
    """ Euler axis angle in radians.

    :type: float
    """

    y: float
    """ Euler axis angle in radians.

    :type: float
    """

    z: float
    """ Euler axis angle in radians.

    :type: float
    """

    @staticmethod
    def copy() -> "Euler":
        """Returns a copy of this euler.

        :rtype: 'Euler'
        :return: A copy of the euler.
        """
        ...

    @staticmethod
    def freeze() -> "Euler":
        """Make this object immutable. After this the object can be hashed, used in dictionaries & sets.

        :rtype: 'Euler'
        :return: An instance of this object.
        """
        ...

    def make_compatible(self, other):
        """Make this euler compatible with another, so interpolating between them works as intended."""
        ...

    def rotate(
        self,
        other: typing.Union[
            typing.Sequence[float],
            "Euler",
            typing.Sequence[float],
            "Quaternion",
            typing.Sequence[float],
            "Matrix",
        ],
    ):
        """Rotates the euler by another mathutils value.

        :param other: rotation component of mathutils value
        :type other: typing.Union[typing.Sequence[float], 'Euler', typing.Sequence[float], 'Quaternion', typing.Sequence[float], 'Matrix']
        """
        ...

    def rotate_axis(self, axis: str, angle: float):
        """Rotates the euler a certain amount and returning a unique euler rotation (no 720 degree pitches).

        :param axis: single character in ['X, 'Y', 'Z'].
        :type axis: str
        :param angle: angle in radians.
        :type angle: float
        """
        ...

    def to_matrix(self) -> "Matrix":
        """Return a matrix representation of the euler.

        :rtype: 'Matrix'
        :return: A 3x3 rotation matrix representation of the euler.
        """
        ...

    def to_quaternion(self) -> "Quaternion":
        """Return a quaternion representation of the euler.

        :rtype: 'Quaternion'
        :return: Quaternion representation of the euler.
        """
        ...

    def zero(self):
        """Set all values to zero."""
        ...

    def __init__(self, angles=(0.0, 0.0, 0.0), order="XYZ") -> typing.Any:
        """

        :rtype: typing.Any
        """
        ...

class Matrix:
    """This object gives access to Matrices in Blender, supporting square and rectangular matrices from 2x2 up to 4x4. :arg rows: Sequence of rows. When omitted, a 4x4 identity matrix is constructed. :type rows: 2d number sequence"""

    col: "Matrix"
    """ Access the matrix by columns, 3x3 and 4x4 only, (read-only).

    :type: 'Matrix'
    """

    is_frozen: bool
    """ True when this object has been frozen (read-only).

    :type: bool
    """

    is_identity: bool
    """ True if this is an identity matrix (read-only).

    :type: bool
    """

    is_negative: bool
    """ True if this matrix results in a negative scale, 3x3 and 4x4 only, (read-only).

    :type: bool
    """

    is_orthogonal: bool
    """ True if this matrix is orthogonal, 3x3 and 4x4 only, (read-only).

    :type: bool
    """

    is_orthogonal_axis_vectors: bool
    """ True if this matrix has got orthogonal axis vectors, 3x3 and 4x4 only, (read-only).

    :type: bool
    """

    is_valid: bool
    """ True when the owner of this data is valid.

    :type: bool
    """

    is_wrapped: bool
    """ True when this object wraps external data (read-only).

    :type: bool
    """

    median_scale: float
    """ The average scale applied to each axis (read-only).

    :type: float
    """

    owner: typing.Any
    """ The item this is wrapping or None (read-only)."""

    row: "Matrix"
    """ Access the matrix by rows (default), (read-only).

    :type: 'Matrix'
    """

    translation: "Vector"
    """ The translation component of the matrix.

    :type: 'Vector'
    """

    @classmethod
    def Diagonal(
        cls, vector: typing.Union[typing.Sequence[float], "Vector"]
    ) -> "Matrix":
        """Create a diagonal (scaling) matrix using the values from the vector.

        :param vector: The vector of values for the diagonal.
        :type vector: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Matrix'
        :return: A diagonal matrix.
        """
        ...

    @classmethod
    def Identity(cls, size: int) -> "Matrix":
        """Create an identity matrix.

        :param size: The size of the identity matrix to construct [2, 4].
        :type size: int
        :rtype: 'Matrix'
        :return: A new identity matrix.
        """
        ...

    @classmethod
    def LocRotScale(
        cls,
        location: typing.Optional["Vector"],
        rotation: typing.Optional[
            typing.Union[
                typing.Sequence[float], "Quaternion", typing.Sequence[float], "Euler"
            ]
        ],
        scale: typing.Optional["Vector"],
    ) -> "Matrix":
        """Create a matrix combining translation, rotation and scale, acting as the inverse of the decompose() method. Any of the inputs may be replaced with None if not needed.

        :param location: The translation component.
        :type location: typing.Optional['Vector']
        :param rotation: The rotation component.
        :type rotation: typing.Optional[typing.Union[typing.Sequence[float], 'Quaternion', typing.Sequence[float], 'Euler']]
        :param scale: The scale component.
        :type scale: typing.Optional['Vector']
        :rtype: 'Matrix'
        :return: Combined transformation matrix.
        """
        ...

    @classmethod
    def OrthoProjection(
        cls, axis: typing.Union[str, typing.Sequence[float], "Vector"], size: int
    ) -> "Matrix":
        """Create a matrix to represent an orthographic projection.

        :param axis: ['X', 'Y', 'XY', 'XZ', 'YZ'], where a single axis is for a 2D matrix. Or a vector for an arbitrary axis
        :type axis: typing.Union[str, typing.Sequence[float], 'Vector']
        :param size: The size of the projection matrix to construct [2, 4].
        :type size: int
        :rtype: 'Matrix'
        :return: A new projection matrix.
        """
        ...

    @classmethod
    def Rotation(
        cls,
        angle: float,
        size: int,
        axis: typing.Union[str, typing.Sequence[float], "Vector"],
    ) -> "Matrix":
        """Create a matrix representing a rotation.

        :param angle: The angle of rotation desired, in radians.
        :type angle: float
        :param size: The size of the rotation matrix to construct [2, 4].
        :type size: int
        :param axis: a string in ['X', 'Y', 'Z'] or a 3D Vector Object (optional when size is 2).
        :type axis: typing.Union[str, typing.Sequence[float], 'Vector']
        :rtype: 'Matrix'
        :return: A new rotation matrix.
        """
        ...

    @classmethod
    def Scale(
        cls,
        factor: float,
        size: int,
        axis: typing.Union[typing.Sequence[float], "Vector"],
    ) -> "Matrix":
        """Create a matrix representing a scaling.

        :param factor: The factor of scaling to apply.
        :type factor: float
        :param size: The size of the scale matrix to construct [2, 4].
        :type size: int
        :param axis: Direction to influence scale. (optional).
        :type axis: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Matrix'
        :return: A new scale matrix.
        """
        ...

    @classmethod
    def Shear(cls, plane: str, size: int, factor: float) -> "Matrix":
        """Create a matrix to represent an shear transformation.

        :param plane: ['X', 'Y', 'XY', 'XZ', 'YZ'], where a single axis is for a 2D matrix only.
        :type plane: str
        :param size: The size of the shear matrix to construct [2, 4].
        :type size: int
        :param factor: The factor of shear to apply. For a 3 or 4 *size* matrix pass a pair of floats corresponding with the *plane* axis.
        :type factor: float
        :rtype: 'Matrix'
        :return: A new shear matrix.
        """
        ...

    @classmethod
    def Translation(
        cls, vector: typing.Union[typing.Sequence[float], "Vector"]
    ) -> "Matrix":
        """Create a matrix representing a translation.

        :param vector: The translation vector.
        :type vector: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Matrix'
        :return: An identity matrix with a translation.
        """
        ...

    def adjugate(self):
        """Set the matrix to its adjugate. :raises ValueError: if the matrix cannot be adjugate."""
        ...

    def adjugated(self) -> "Matrix":
        """Return an adjugated copy of the matrix. :raises ValueError: if the matrix cannot be adjugated

        :rtype: 'Matrix'
        :return: the adjugated matrix.
        """
        ...

    def copy(self) -> "Matrix":
        """Returns a copy of this matrix.

        :rtype: 'Matrix'
        :return: an instance of itself
        """
        ...

    def decompose(self) -> "Quaternion":
        """Return the translation, rotation, and scale components of this matrix.

        :rtype: 'Quaternion'
        :return: tuple of translation, rotation, and scale
        """
        ...

    def determinant(self) -> float:
        """Return the determinant of a matrix.

        :rtype: float
        :return: Return the determinant of a matrix.
        """
        ...

    @staticmethod
    def freeze() -> "Matrix":
        """Make this object immutable. After this the object can be hashed, used in dictionaries & sets.

        :rtype: 'Matrix'
        :return: An instance of this object.
        """
        ...

    def identity(self):
        """Set the matrix to the identity matrix."""
        ...

    def invert(self, fallback: typing.Union[typing.Sequence[float], "Matrix"] = None):
        """Set the matrix to its inverse.

        :param fallback: Set the matrix to this value when the inverse cannot be calculated (instead of raising a :exc:`ValueError` exception).
        :type fallback: typing.Union[typing.Sequence[float], 'Matrix']
        """
        ...

    def invert_safe(self):
        """Set the matrix to its inverse, will never error. If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one. If tweaked matrix is still degenerated, set to the identity matrix instead."""
        ...

    def inverted(self, fallback: typing.Any = None) -> "Matrix":
        """Return an inverted copy of the matrix.

        :param fallback: return this when the inverse can't be calculated (instead of raising a :exc:`ValueError`).
        :type fallback: typing.Any
        :rtype: 'Matrix'
        :return: the inverted matrix or fallback when given.
        """
        ...

    def inverted_safe(self) -> "Matrix":
        """Return an inverted copy of the matrix, will never error. If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one. If tweaked matrix is still degenerated, return the identity matrix instead.

        :rtype: 'Matrix'
        :return: the inverted matrix.
        """
        ...

    @staticmethod
    def lerp(
        other: typing.Union[typing.Sequence[float], "Matrix"], factor: float
    ) -> "Matrix":
        """Returns the interpolation of two matrices. Uses polar decomposition, see "Matrix Animation and Polar Decomposition", Shoemake and Duff, 1992.

        :param other: value to interpolate with.
        :type other: typing.Union[typing.Sequence[float], 'Matrix']
        :param factor: The interpolation value in [0.0, 1.0].
        :type factor: float
        :rtype: 'Matrix'
        :return: The interpolated matrix.
        """
        ...

    def normalize(self):
        """Normalize each of the matrix columns."""
        ...

    def normalized(self) -> "Matrix":
        """Return a column normalized matrix

        :rtype: 'Matrix'
        :return: a column normalized matrix
        """
        ...

    def resize_4x4(self):
        """Resize the matrix to 4x4."""
        ...

    def rotate(
        self,
        other: typing.Union[
            typing.Sequence[float],
            "Euler",
            typing.Sequence[float],
            "Quaternion",
            typing.Sequence[float],
            "Matrix",
        ],
    ):
        """Rotates the matrix by another mathutils value.

        :param other: rotation component of mathutils value
        :type other: typing.Union[typing.Sequence[float], 'Euler', typing.Sequence[float], 'Quaternion', typing.Sequence[float], 'Matrix']
        """
        ...

    def to_2x2(self) -> "Matrix":
        """Return a 2x2 copy of this matrix.

        :rtype: 'Matrix'
        :return: a new matrix.
        """
        ...

    def to_3x3(self) -> "Matrix":
        """Return a 3x3 copy of this matrix.

        :rtype: 'Matrix'
        :return: a new matrix.
        """
        ...

    def to_4x4(self) -> "Matrix":
        """Return a 4x4 copy of this matrix.

        :rtype: 'Matrix'
        :return: a new matrix.
        """
        ...

    def to_euler(
        self, order: str, euler_compat: typing.Union[typing.Sequence[float], "Euler"]
    ) -> "Euler":
        """Return an Euler representation of the rotation matrix (3x3 or 4x4 matrix only).

        :param order: Optional rotation order argument in ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'].
        :type order: str
        :param euler_compat: Optional euler argument the new euler will be made compatible with (no axis flipping between them). Useful for converting a series of matrices to animation curves.
        :type euler_compat: typing.Union[typing.Sequence[float], 'Euler']
        :rtype: 'Euler'
        :return: Euler representation of the matrix.
        """
        ...

    def to_quaternion(self) -> "Quaternion":
        """Return a quaternion representation of the rotation matrix.

        :rtype: 'Quaternion'
        :return: Quaternion representation of the rotation matrix.
        """
        ...

    def to_scale(self) -> "Vector":
        """Return the scale part of a 3x3 or 4x4 matrix.

        :rtype: 'Vector'
        :return: Return the scale of a matrix.
        """
        ...

    def to_translation(self) -> "Vector":
        """Return the translation part of a 4 row matrix.

        :rtype: 'Vector'
        :return: Return the translation of a matrix.
        """
        ...

    def transpose(self):
        """Set the matrix to its transpose."""
        ...

    def transposed(self) -> "Matrix":
        """Return a new, transposed matrix.

        :rtype: 'Matrix'
        :return: a transposed matrix
        """
        ...

    def zero(self) -> "Matrix":
        """Set all the matrix values to zero.

        :rtype: 'Matrix'
        """
        ...

    def __init__(
        self,
        rows=(
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ),
    ) -> typing.Any:
        """

        :rtype: typing.Any
        """
        ...

    def __getitem__(self, key: int) -> "Vector":
        """

        :param key:
        :type key: int
        :rtype: 'Vector'
        """
        ...

    def __len__(self) -> int:
        """

        :rtype: int
        """
        ...

    def __add__(
        self, other: typing.Union[typing.Sequence[float], "Matrix"]
    ) -> "Matrix":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Matrix']
        :rtype: 'Matrix'
        """
        ...

    def __sub__(
        self, other: typing.Union[typing.Sequence[float], "Matrix"]
    ) -> "Matrix":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Matrix']
        :rtype: 'Matrix'
        """
        ...

    def __mul__(self, other: typing.Union[int, float]) -> "Matrix":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Matrix'
        """
        ...

    def __matmul__(
        self,
        other: typing.Union[
            typing.Sequence[float], "Matrix", typing.Sequence[float], "Vector"
        ],
    ) -> typing.Union["Matrix", "Vector"]:
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Matrix', typing.Sequence[float], 'Vector']
        :rtype: typing.Union['Matrix', 'Vector']
        """
        ...

    def __radd__(
        self, other: typing.Union[typing.Sequence[float], "Matrix"]
    ) -> "Matrix":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Matrix']
        :rtype: 'Matrix'
        """
        ...

    def __rsub__(
        self, other: typing.Union[typing.Sequence[float], "Matrix"]
    ) -> "Matrix":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Matrix']
        :rtype: 'Matrix'
        """
        ...

    def __rmul__(self, other: typing.Union[int, float]) -> "Matrix":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Matrix'
        """
        ...

    def __rmatmul__(
        self, other: typing.Union[typing.Sequence[float], "Matrix"]
    ) -> "Matrix":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Matrix']
        :rtype: 'Matrix'
        """
        ...

    def __imul__(self, other: typing.Union[int, float]) -> "Matrix":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Matrix'
        """
        ...

    def __imatmul__(
        self, other: typing.Union[typing.Sequence[float], "Matrix"]
    ) -> "Matrix":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Matrix']
        :rtype: 'Matrix'
        """
        ...

class Quaternion:
    """This object gives access to Quaternions in Blender. :arg seq: size 3 or 4 :type seq: `Vector` :arg angle: rotation angle, in radians :type angle: float The constructor takes arguments in various forms: (), *no args* Create an identity quaternion (*wxyz*) Create a quaternion from a ``(w, x, y, z)`` vector. (*exponential_map*) Create a quaternion from a 3d exponential map vector. .. seealso:: :meth:`to_exponential_map` (*axis, angle*) Create a quaternion representing a rotation of *angle* radians over *axis*. .. seealso:: :meth:`to_axis_angle`"""

    angle: float
    """ Angle of the quaternion.

    :type: float
    """

    axis: typing.Union[typing.Sequence[float], "Vector"]
    """ Quaternion axis as a vector.

    :type: typing.Union[typing.Sequence[float], 'Vector']
    """

    is_frozen: bool
    """ True when this object has been frozen (read-only).

    :type: bool
    """

    is_valid: bool
    """ True when the owner of this data is valid.

    :type: bool
    """

    is_wrapped: bool
    """ True when this object wraps external data (read-only).

    :type: bool
    """

    magnitude: float
    """ Size of the quaternion (read-only).

    :type: float
    """

    owner: typing.Any
    """ The item this is wrapping or None (read-only)."""

    w: float
    """ Quaternion axis value.

    :type: float
    """

    x: float
    """ Quaternion axis value.

    :type: float
    """

    y: float
    """ Quaternion axis value.

    :type: float
    """

    z: float
    """ Quaternion axis value.

    :type: float
    """

    @staticmethod
    def conjugate():
        """Set the quaternion to its conjugate (negate x, y, z)."""
        ...

    @staticmethod
    def conjugated() -> "Quaternion":
        """Return a new conjugated quaternion.

        :rtype: 'Quaternion'
        :return: a new quaternion.
        """
        ...

    @staticmethod
    def copy() -> "Quaternion":
        """Returns a copy of this quaternion.

        :rtype: 'Quaternion'
        :return: A copy of the quaternion.
        """
        ...

    def cross(
        self, other: typing.Union[typing.Sequence[float], "Quaternion"]
    ) -> "Quaternion":
        """Return the cross product of this quaternion and another.

        :param other: The other quaternion to perform the cross product with.
        :type other: typing.Union[typing.Sequence[float], 'Quaternion']
        :rtype: 'Quaternion'
        :return: The cross product.
        """
        ...

    def dot(self, other: typing.Union[typing.Sequence[float], "Quaternion"]) -> float:
        """Return the dot product of this quaternion and another.

        :param other: The other quaternion to perform the dot product with.
        :type other: typing.Union[typing.Sequence[float], 'Quaternion']
        :rtype: float
        :return: The dot product.
        """
        ...

    @staticmethod
    def freeze() -> "Quaternion":
        """Make this object immutable. After this the object can be hashed, used in dictionaries & sets.

        :rtype: 'Quaternion'
        :return: An instance of this object.
        """
        ...

    @staticmethod
    def identity() -> "Quaternion":
        """Set the quaternion to an identity quaternion.

        :rtype: 'Quaternion'
        """
        ...

    @staticmethod
    def invert():
        """Set the quaternion to its inverse."""
        ...

    @staticmethod
    def inverted() -> "Quaternion":
        """Return a new, inverted quaternion.

        :rtype: 'Quaternion'
        :return: the inverted value.
        """
        ...

    def make_compatible(self, other):
        """Make this quaternion compatible with another, so interpolating between them works as intended."""
        ...

    @staticmethod
    def negate() -> "Quaternion":
        """Set the quaternion to its negative.

        :rtype: 'Quaternion'
        """
        ...

    @staticmethod
    def normalize():
        """Normalize the quaternion."""
        ...

    @staticmethod
    def normalized() -> "Quaternion":
        """Return a new normalized quaternion.

        :rtype: 'Quaternion'
        :return: a normalized copy.
        """
        ...

    def rotate(
        self,
        other: typing.Union[
            typing.Sequence[float],
            "Euler",
            typing.Sequence[float],
            "Quaternion",
            typing.Sequence[float],
            "Matrix",
        ],
    ):
        """Rotates the quaternion by another mathutils value.

        :param other: rotation component of mathutils value
        :type other: typing.Union[typing.Sequence[float], 'Euler', typing.Sequence[float], 'Quaternion', typing.Sequence[float], 'Matrix']
        """
        ...

    @staticmethod
    def rotation_difference(
        other: typing.Union[typing.Sequence[float], "Quaternion"],
    ) -> "Quaternion":
        """Returns a quaternion representing the rotational difference.

        :param other: second quaternion.
        :type other: typing.Union[typing.Sequence[float], 'Quaternion']
        :rtype: 'Quaternion'
        :return: the rotational difference between the two quat rotations.
        """
        ...

    @staticmethod
    def slerp(
        other: typing.Union[typing.Sequence[float], "Quaternion"], factor: float
    ) -> "Quaternion":
        """Returns the interpolation of two quaternions.

        :param other: value to interpolate with.
        :type other: typing.Union[typing.Sequence[float], 'Quaternion']
        :param factor: The interpolation value in [0.0, 1.0].
        :type factor: float
        :rtype: 'Quaternion'
        :return: The interpolated rotation.
        """
        ...

    def to_axis_angle(self) -> typing.Tuple["Vector", "float"]:
        """Return the axis, angle representation of the quaternion.

        :rtype: typing.Tuple['Vector', 'float']
        :return: axis, angle.
        """
        ...

    def to_euler(
        self, order: str, euler_compat: typing.Union[typing.Sequence[float], "Euler"]
    ) -> "Euler":
        """Return Euler representation of the quaternion.

        :param order: Optional rotation order argument in ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'].
        :type order: str
        :param euler_compat: Optional euler argument the new euler will be made compatible with (no axis flipping between them). Useful for converting a series of matrices to animation curves.
        :type euler_compat: typing.Union[typing.Sequence[float], 'Euler']
        :rtype: 'Euler'
        :return: Euler representation of the quaternion.
        """
        ...

    def to_exponential_map(self) -> "Vector":
        """Return the exponential map representation of the quaternion. This representation consist of the rotation axis multiplied by the rotation angle. Such a representation is useful for interpolation between multiple orientations. To convert back to a quaternion, pass it to the `Quaternion` constructor.

        :rtype: 'Vector'
        :return: exponential map.
        """
        ...

    def to_matrix(self) -> "Matrix":
        """Return a matrix representation of the quaternion.

        :rtype: 'Matrix'
        :return: A 3x3 rotation matrix representation of the quaternion.
        """
        ...

    def to_swing_twist(self, axis: typing.Any) -> typing.Tuple["Quaternion", "float"]:
        """Split the rotation into a swing quaternion with the specified axis fixed at zero, and the remaining twist rotation angle.

        :param axis:  twist axis as a string in ['X', 'Y', 'Z']
        :type axis: typing.Any
        :rtype: typing.Tuple['Quaternion', 'float']
        :return: swing, twist angle.
        """
        ...

    def __init__(self, seq=(1.0, 0.0, 0.0, 0.0)) -> typing.Any:
        """

        :rtype: typing.Any
        """
        ...

    def __len__(self) -> int:
        """

        :rtype: int
        """
        ...

    def __getitem__(self, key: int) -> float:
        """

        :param key:
        :type key: int
        :rtype: float
        """
        ...

    def __setitem__(self, key: int, value: float) -> float:
        """

        :param key:
        :type key: int
        :param value:
        :type value: float
        :rtype: float
        """
        ...

    def __add__(
        self, other: typing.Union[typing.Sequence[float], "Quaternion"]
    ) -> "Quaternion":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Quaternion']
        :rtype: 'Quaternion'
        """
        ...

    def __sub__(
        self, other: typing.Union[typing.Sequence[float], "Quaternion"]
    ) -> "Quaternion":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Quaternion']
        :rtype: 'Quaternion'
        """
        ...

    def __mul__(
        self, other: typing.Union[int, float, typing.Sequence[float], "Quaternion"]
    ) -> "Quaternion":
        """

        :param other:
        :type other: typing.Union[int, float, typing.Sequence[float], 'Quaternion']
        :rtype: 'Quaternion'
        """
        ...

    def __matmul__(
        self,
        other: typing.Union[
            typing.Sequence[float], "Vector", typing.Sequence[float], "Quaternion"
        ],
    ) -> typing.Union["Vector", "Quaternion"]:
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Vector', typing.Sequence[float], 'Quaternion']
        :rtype: typing.Union['Vector', 'Quaternion']
        """
        ...

    def __radd__(
        self, other: typing.Union[typing.Sequence[float], "Quaternion"]
    ) -> "Quaternion":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Quaternion']
        :rtype: 'Quaternion'
        """
        ...

    def __rsub__(
        self, other: typing.Union[typing.Sequence[float], "Quaternion"]
    ) -> "Quaternion":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Quaternion']
        :rtype: 'Quaternion'
        """
        ...

    def __rmul__(
        self, other: typing.Union[int, float, typing.Sequence[float], "Quaternion"]
    ) -> "Quaternion":
        """

        :param other:
        :type other: typing.Union[int, float, typing.Sequence[float], 'Quaternion']
        :rtype: 'Quaternion'
        """
        ...

    def __rmatmul__(
        self, other: typing.Union[typing.Sequence[float], "Vector"]
    ) -> "Vector":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Vector'
        """
        ...

    def __imul__(
        self, other: typing.Union[int, float, typing.Sequence[float], "Quaternion"]
    ) -> "Quaternion":
        """

        :param other:
        :type other: typing.Union[int, float, typing.Sequence[float], 'Quaternion']
        :rtype: 'Quaternion'
        """
        ...

    def __imatmul__(
        self, other: typing.Union[typing.Sequence[float], "Vector"]
    ) -> "Vector":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Vector'
        """
        ...

class Vector:
    """This object gives access to Vectors in Blender. :arg seq: Components of the vector, must be a sequence of at least two :type seq: sequence of numbers"""

    is_frozen: bool
    """ True when this object has been frozen (read-only).

    :type: bool
    """

    is_valid: bool
    """ True when the owner of this data is valid.

    :type: bool
    """

    is_wrapped: bool
    """ True when this object wraps external data (read-only).

    :type: bool
    """

    length: float
    """ Vector Length.

    :type: float
    """

    length_squared: float
    """ Vector length squared (v.dot(v)).

    :type: float
    """

    magnitude: float
    """ Vector Length.

    :type: float
    """

    owner: typing.Any
    """ The item this is wrapping or None (read-only)."""

    w: float
    """ Vector W axis (4D Vectors only).

    :type: float
    """

    ww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    www: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wwzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wxzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wywx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wywy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wywz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wyzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    wzzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    x: float
    """ Vector X axis.

    :type: float
    """

    xw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xwzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xxzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xywx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xywy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xywz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xyzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    xzzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    y: float
    """ Vector Y axis.

    :type: float
    """

    yw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    ywzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yxzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yywx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yywy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yywz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yyzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    yzzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    z: float
    """ Vector Z axis (3D Vectors only).

    :type: float
    """

    zw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zwzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zxzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zywx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zywy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zywz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zyzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzww: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzwx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzwy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzwz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzxw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzxx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzxy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzxz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzyw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzyx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzyy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzyz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzzw: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzzx: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzzy: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    zzzz: typing.Any
    """ Undocumented, consider `contributing <https://developer.blender.org/>`__."""

    @classmethod
    def Fill(cls, size: int, fill: float = 0.0):
        """Create a vector of length size with all values set to fill.

        :param size: The length of the vector to be created.
        :type size: int
        :param fill: The value used to fill the vector.
        :type fill: float
        """
        ...

    @classmethod
    def Linspace(cls, start: int, stop: int, size: int):
        """Create a vector of the specified size which is filled with linearly spaced values between start and stop values.

        :param start: The start of the range used to fill the vector.
        :type start: int
        :param stop: The end of the range used to fill the vector.
        :type stop: int
        :param size: The size of the vector to be created.
        :type size: int
        """
        ...

    @classmethod
    def Range(cls, start: int, stop: int, step: int = 1):
        """Create a filled with a range of values.

        :param start: The start of the range used to fill the vector.
        :type start: int
        :param stop: The end of the range used to fill the vector.
        :type stop: int
        :param step: The step between successive values in the vector.
        :type step: int
        """
        ...

    @classmethod
    def Repeat(cls, vector, size: int):
        """Create a vector by repeating the values in vector until the required size is reached.

        :param tuple: The vector to draw values from.
        :type tuple: typing.Union[typing.Sequence[float], 'Vector']
        :param size: The size of the vector to be created.
        :type size: int
        """
        ...

    @staticmethod
    def angle(
        other: typing.Union[typing.Sequence[float], "Vector"],
        fallback: typing.Any = None,
    ) -> float:
        """Return the angle between two vectors.

        :param other: another vector to compare the angle with
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :param fallback: return this when the angle can't be calculated (zero length vector), (instead of raising a :exc:`ValueError`).
        :type fallback: typing.Any
        :rtype: float
        :return: angle in radians or fallback when given
        """
        ...

    @staticmethod
    def angle_signed(
        other: typing.Union[typing.Sequence[float], "Vector"], fallback: typing.Any
    ) -> float:
        """Return the signed angle between two 2D vectors (clockwise is positive).

        :param other: another vector to compare the angle with
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :param fallback: return this when the angle can't be calculated (zero length vector), (instead of raising a :exc:`ValueError`).
        :type fallback: typing.Any
        :rtype: float
        :return: angle in radians or fallback when given
        """
        ...

    @staticmethod
    def copy() -> "Vector":
        """Returns a copy of this vector.

        :rtype: 'Vector'
        :return: A copy of the vector.
        """
        ...

    def cross(self, other: typing.Union[typing.Sequence[float], "Vector"]) -> "Vector":
        """Return the cross product of this vector and another.

        :param other: The other vector to perform the cross product with.
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Vector'
        :return: The cross product.
        """
        ...

    def dot(self, other: typing.Union[typing.Sequence[float], "Vector"]) -> float:
        """Return the dot product of this vector and another.

        :param other: The other vector to perform the dot product with.
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: float
        :return: The dot product.
        """
        ...

    @staticmethod
    def freeze() -> "Vector":
        """Make this object immutable. After this the object can be hashed, used in dictionaries & sets.

        :rtype: 'Vector'
        :return: An instance of this object.
        """
        ...

    @staticmethod
    def lerp(
        other: typing.Union[typing.Sequence[float], "Vector"], factor: float
    ) -> "Vector":
        """Returns the interpolation of two vectors.

        :param other: value to interpolate with.
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :param factor: The interpolation value in [0.0, 1.0].
        :type factor: float
        :rtype: 'Vector'
        :return: The interpolated vector.
        """
        ...

    def negate(self):
        """Set all values to their negative."""
        ...

    def normalize(self):
        """Normalize the vector, making the length of the vector always 1.0."""
        ...

    def normalized(self) -> "Vector":
        """Return a new, normalized vector.

        :rtype: 'Vector'
        :return: a normalized copy of the vector
        """
        ...

    def orthogonal(self) -> "Vector":
        """Return a perpendicular vector.

        :rtype: 'Vector'
        :return: a new vector 90 degrees from this vector.
        """
        ...

    @staticmethod
    def project(other: typing.Union[typing.Sequence[float], "Vector"]) -> "Vector":
        """Return the projection of this vector onto the *other*.

        :param other: second vector.
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Vector'
        :return: the parallel projection vector
        """
        ...

    def reflect(
        self, mirror: typing.Union[typing.Sequence[float], "Vector"]
    ) -> "Vector":
        """Return the reflection vector from the *mirror* argument.

        :param mirror: This vector could be a normal from the reflecting surface.
        :type mirror: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Vector'
        :return: The reflected vector matching the size of this vector.
        """
        ...

    def resize(self, size=3):
        """Resize the vector to have size number of elements."""
        ...

    def resize_2d(self):
        """Resize the vector to 2D (x, y)."""
        ...

    def resize_3d(self):
        """Resize the vector to 3D (x, y, z)."""
        ...

    def resize_4d(self):
        """Resize the vector to 4D (x, y, z, w)."""
        ...

    def resized(self, size=3) -> "Vector":
        """Return a resized copy of the vector with size number of elements.

        :rtype: 'Vector'
        :return: a new vector
        """
        ...

    @staticmethod
    def rotate(
        other: typing.Union[
            typing.Sequence[float],
            "Euler",
            typing.Sequence[float],
            "Quaternion",
            typing.Sequence[float],
            "Matrix",
        ],
    ):
        """Rotate the vector by a rotation value.

        :param other: rotation component of mathutils value
        :type other: typing.Union[typing.Sequence[float], 'Euler', typing.Sequence[float], 'Quaternion', typing.Sequence[float], 'Matrix']
        """
        ...

    @staticmethod
    def rotation_difference(
        other: typing.Union[typing.Sequence[float], "Vector"],
    ) -> "Quaternion":
        """Returns a quaternion representing the rotational difference between this vector and another.

        :param other: second vector.
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Quaternion'
        :return: the rotational difference between the two vectors.
        """
        ...

    @staticmethod
    def slerp(
        other: typing.Union[typing.Sequence[float], "Vector"],
        factor: float,
        fallback: typing.Any = None,
    ) -> "Vector":
        """Returns the interpolation of two non-zero vectors (spherical coordinates).

        :param other: value to interpolate with.
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :param factor: The interpolation value typically in [0.0, 1.0].
        :type factor: float
        :param fallback: return this when the vector can't be calculated (zero length vector or direct opposites), (instead of raising a :exc:`ValueError`).
        :type fallback: typing.Any
        :rtype: 'Vector'
        :return: The interpolated vector.
        """
        ...

    def to_2d(self) -> "Vector":
        """Return a 2d copy of the vector.

        :rtype: 'Vector'
        :return: a new vector
        """
        ...

    def to_3d(self) -> "Vector":
        """Return a 3d copy of the vector.

        :rtype: 'Vector'
        :return: a new vector
        """
        ...

    def to_4d(self) -> "Vector":
        """Return a 4d copy of the vector.

        :rtype: 'Vector'
        :return: a new vector
        """
        ...

    def to_track_quat(self, track: str, up: str) -> "Quaternion":
        """Return a quaternion rotation from the vector and the track and up axis.

        :param track: Track axis in ['X', 'Y', 'Z', '-X', '-Y', '-Z'].
        :type track: str
        :param up: Up axis in ['X', 'Y', 'Z'].
        :type up: str
        :rtype: 'Quaternion'
        :return: rotation from the vector and the track and up axis.
        """
        ...

    def to_tuple(self, precision: int = -1) -> typing.Tuple:
        """Return this vector as a tuple with.

        :param precision: The number to round the value to in [-1, 21].
        :type precision: int
        :rtype: typing.Tuple
        :return: the values of the vector rounded by *precision*
        """
        ...

    def zero(self):
        """Set all values to zero."""
        ...

    def __init__(self, seq=(0.0, 0.0, 0.0)) -> typing.Any:
        """

        :rtype: typing.Any
        """
        ...

    def __len__(self) -> int:
        """

        :rtype: int
        """
        ...

    def __getitem__(self, key: int) -> float:
        """

        :param key:
        :type key: int
        :rtype: float
        """
        ...

    def __setitem__(self, key: int, value: float) -> float:
        """

        :param key:
        :type key: int
        :param value:
        :type value: float
        :rtype: float
        """
        ...

    def __neg__(self) -> "Vector":
        """

        :rtype: 'Vector'
        """
        ...

    def __add__(
        self, other: typing.Union[typing.Sequence[float], "Vector"]
    ) -> "Vector":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Vector'
        """
        ...

    def __sub__(
        self, other: typing.Union[typing.Sequence[float], "Vector"]
    ) -> "Vector":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Vector'
        """
        ...

    def __mul__(self, other: typing.Union[int, float]) -> "Vector":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Vector'
        """
        ...

    def __truediv__(self, other: typing.Union[int, float]) -> "Vector":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Vector'
        """
        ...

    def __matmul__(
        self, other: typing.Union[typing.Sequence[float], "Matrix"]
    ) -> "Vector":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Matrix']
        :rtype: 'Vector'
        """
        ...

    def __radd__(
        self, other: typing.Union[typing.Sequence[float], "Vector"]
    ) -> "Vector":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Vector'
        """
        ...

    def __rsub__(
        self, other: typing.Union[typing.Sequence[float], "Vector"]
    ) -> "Vector":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Vector'
        """
        ...

    def __rmul__(self, other: typing.Union[int, float]) -> "Vector":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Vector'
        """
        ...

    def __rtruediv__(self, other: typing.Union[int, float]) -> "Vector":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Vector'
        """
        ...

    def __rmatmul__(
        self, other: typing.Union[typing.Sequence[float], "Matrix"]
    ) -> "Vector":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Matrix']
        :rtype: 'Vector'
        """
        ...

    def __iadd__(
        self, other: typing.Union[typing.Sequence[float], "Vector"]
    ) -> "Vector":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Vector'
        """
        ...

    def __isub__(
        self, other: typing.Union[typing.Sequence[float], "Vector"]
    ) -> "Vector":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Vector']
        :rtype: 'Vector'
        """
        ...

    def __imul__(self, other: typing.Union[int, float]) -> "Vector":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Vector'
        """
        ...

    def __itruediv__(self, other: typing.Union[int, float]) -> "Vector":
        """

        :param other:
        :type other: typing.Union[int, float]
        :rtype: 'Vector'
        """
        ...

    def __imatmul__(
        self, other: typing.Union[typing.Sequence[float], "Matrix"]
    ) -> "Vector":
        """

        :param other:
        :type other: typing.Union[typing.Sequence[float], 'Matrix']
        :rtype: 'Vector'
        """
        ...
