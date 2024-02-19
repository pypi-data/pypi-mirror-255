import sys
import typing
import mathutils

GenericType = typing.TypeVar("GenericType")

def get_model_view_matrix() -> "mathutils.Matrix":
    """Return a copy of the model-view matrix.

    :rtype: 'mathutils.Matrix'
    :return: A 4x4 view matrix.
    """

    ...

def get_normal_matrix() -> "mathutils.Matrix":
    """Return a copy of the normal matrix.

    :rtype: 'mathutils.Matrix'
    :return: A 3x3 normal matrix.
    """

    ...

def get_projection_matrix() -> "mathutils.Matrix":
    """Return a copy of the projection matrix.

    :rtype: 'mathutils.Matrix'
    :return: A 4x4 projection matrix.
    """

    ...

def load_identity():
    """Load an identity matrix into the stack."""

    ...

def load_matrix(matrix: typing.Union[typing.Sequence[float], "mathutils.Matrix"]):
    """Load a matrix into the stack.

    :param matrix: A 4x4 matrix.
    :type matrix: typing.Union[typing.Sequence[float], 'mathutils.Matrix']
    """

    ...

def load_projection_matrix(
    matrix: typing.Union[typing.Sequence[float], "mathutils.Matrix"],
):
    """Load a projection matrix into the stack.

    :param matrix: A 4x4 matrix.
    :type matrix: typing.Union[typing.Sequence[float], 'mathutils.Matrix']
    """

    ...

def multiply_matrix(matrix: typing.Union[typing.Sequence[float], "mathutils.Matrix"]):
    """Multiply the current stack matrix.

    :param matrix: A 4x4 matrix.
    :type matrix: typing.Union[typing.Sequence[float], 'mathutils.Matrix']
    """

    ...

def pop():
    """Remove the last model-view matrix from the stack."""

    ...

def pop_projection():
    """Remove the last projection matrix from the stack."""

    ...

def push():
    """Add to the model-view matrix stack."""

    ...

def push_pop():
    """Context manager to ensure balanced push/pop calls, even in the case of an error."""

    ...

def push_pop_projection():
    """Context manager to ensure balanced push/pop calls, even in the case of an error."""

    ...

def push_projection():
    """Add to the projection matrix stack."""

    ...

def reset():
    """Empty stack and set to identity."""

    ...

def scale(scale: typing.List):
    """Scale the current stack matrix.

    :param scale: Scale the current stack matrix.
    :type scale: typing.List
    """

    ...

def scale_uniform(scale: float):
    """

    :param scale: Scale the current stack matrix.
    :type scale: float
    """

    ...

def translate(offset: typing.List):
    """Scale the current stack matrix.

    :param offset: Translate the current stack matrix.
    :type offset: typing.List
    """

    ...
