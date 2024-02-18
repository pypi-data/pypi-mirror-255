import sys
import typing

GenericType = typing.TypeVar("GenericType")

class Buffer:
    """The Buffer object is simply a block of memory that is delineated and initialized by the user. Many OpenGL functions return data to a C-style pointer, however, because this is not possible in python the Buffer object can be used to this end. Wherever pointer notation is used in the OpenGL functions the Buffer object can be used in it's bgl wrapper. In some instances the Buffer object will need to be initialized with the template parameter, while in other instances the user will want to create just a blank buffer which will be zeroed by default."""

    dimensions: typing.Any
    """ The number of dimensions of the Buffer."""

    def to_list(self):
        """The contents of the Buffer as a python list."""
        ...

    def __init__(
        self, type: int, dimensions: typing.List[int], template=" None"
    ) -> "Buffer":
        """This will create a new Buffer object for use with other bgl OpenGL commands. Only the type of argument to store in the buffer and the dimensions of the buffer are necessary. Buffers are zeroed by default unless a template is supplied, in which case the buffer is initialized to the template.

        :param type: The format to store data in. The type should be one of GL_BYTE, GL_SHORT, GL_INT, or GL_FLOAT.
        :type type: int
        :param dimensions: If the dimensions are specified as an int a linear array will be created for the buffer. If a sequence is passed for the dimensions, the buffer becomes n-Dimensional, where n is equal to the number of parameters passed in the sequence. Example: [256,2] is a two- dimensional buffer while [256,256,4] creates a three- dimensional buffer. You can think of each additional dimension as a sub-item of the dimension to the left. i.e. [10,2] is a 10 element array each with 2 sub-items. [(0,0), (0,1), (1,0), (1,1), (2,0), ...] etc.
        :type dimensions: typing.List[int]
        :param template: A sequence of matching dimensions which will be used to initialize the Buffer. If a template is not passed in all fields will be initialized to 0.
        :type template: typing.List
        :rtype: 'Buffer'
        :return: The newly created buffer as a PyObject.
        """
        ...

def glActiveTexture(texture: int):
    """Select active texture unit.

    :param texture: Constant in ``GL_TEXTURE0`` 0 - 8
    :type texture: int
    """

    ...

def glAttachShader(program: int, shader: int):
    """Attaches a shader object to a program object.

    :param program: Specifies the program object to which a shader object will be attached.
    :type program: int
    :param shader: Specifies the shader object that is to be attached.
    :type shader: int
    """

    ...

def glBeginQuery(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glBindAttribLocation(p0: int, p1: int, p2: str) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: str
    :rtype: typing.Any
    """

    ...

def glBindBuffer(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glBindBufferBase(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glBindBufferRange(p0: int, p1: int, p2: int, p3: int, p4: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :rtype: typing.Any
    """

    ...

def glBindFramebuffer(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glBindRenderbuffer(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glBindTexture(target: typing.Union[typing.Set[str], typing.Set[int]], texture: int):
    """Bind a named texture to a texturing target

    :param target: Specifies the target to which the texture is bound.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param texture: Specifies the name of a texture.
    :type texture: int
    """

    ...

def glBindVertexArray(p0: int) -> typing.Any:
    """

    :type p0: int
    :rtype: typing.Any
    """

    ...

def glBlendColor(p0: float, p1: float, p2: float, p3: float) -> typing.Any:
    """

    :type p0: float
    :type p1: float
    :type p2: float
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glBlendEquation(p0: int) -> typing.Any:
    """

    :type p0: int
    :rtype: typing.Any
    """

    ...

def glBlendEquationSeparate(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glBlendFunc(
    sfactor: typing.Union[typing.Set[str], typing.Set[int]],
    dfactor: typing.Union[typing.Set[str], typing.Set[int]],
):
    """Specify pixel arithmetic

    :param sfactor: Specifies how the red, green, blue, and alpha source blending factors are computed.
    :type sfactor: typing.Union[typing.Set[str], typing.Set[int]]
    :param dfactor: Specifies how the red, green, blue, and alpha destination blending factors are computed.
    :type dfactor: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glBlitFramebuffer(
    p0: int,
    p1: int,
    p2: int,
    p3: int,
    p4: int,
    p5: int,
    p6: int,
    p7: int,
    p8: int,
    p9: int,
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :type p7: int
    :type p8: int
    :type p9: int
    :rtype: typing.Any
    """

    ...

def glBufferData(p0: int, p1: int, p2: typing.Any, p3: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: typing.Any
    :type p3: int
    :rtype: typing.Any
    """

    ...

def glBufferSubData(p0: int, p1: int, p2: int, p3: typing.Any) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: typing.Any
    :rtype: typing.Any
    """

    ...

def glCheckFramebufferStatus(p0: int) -> int:
    """

    :type p0: int
    :rtype: int
    """

    ...

def glClear(mask: typing.Any):
    """Clear buffers to preset values

    :param mask: Bitwise OR of masks that indicate the buffers to be cleared.
    :type mask: typing.Any
    """

    ...

def glClearColor(red: float, green: float, blue: float, alpha: float):
    """Specify clear values for the color buffers

    :param red: Specify the red, green, blue, and alpha values used when the color buffers are cleared. The initial values are all 0.
    :type red: float
    :param green: Specify the red, green, blue, and alpha values used when the color buffers are cleared. The initial values are all 0.
    :type green: float
    :param blue: Specify the red, green, blue, and alpha values used when the color buffers are cleared. The initial values are all 0.
    :type blue: float
    :param alpha: Specify the red, green, blue, and alpha values used when the color buffers are cleared. The initial values are all 0.
    :type alpha: float
    """

    ...

def glClearDepth(depth: int):
    """Specify the clear value for the depth buffer

    :param depth: Specifies the depth value used when the depth buffer is cleared. The initial value is 1.
    :type depth: int
    """

    ...

def glClearStencil(s: int):
    """Specify the clear value for the stencil buffer

    :param s: Specifies the index used when the stencil buffer is cleared. The initial value is 0.
    :type s: int
    """

    ...

def glClipPlane(
    plane: typing.Union[typing.Set[str], typing.Set[int]], equation: "Buffer"
):
    """Specify a plane against which all geometry is clipped

    :param plane: Specifies which clipping plane is being positioned.
    :type plane: typing.Union[typing.Set[str], typing.Set[int]]
    :param equation: Specifies the address of an array of four double- precision floating-point values. These values are interpreted as a plane equation.
    :type equation: 'Buffer'
    """

    ...

def glColorMask(red: int, green: int, blue: int, alpha: int):
    """Enable and disable writing of frame buffer color components

    :param red: Specify whether red, green, blue, and alpha can or cannot be written into the frame buffer. The initial values are all GL_TRUE, indicating that the color components can be written.
    :type red: int
    :param green: Specify whether red, green, blue, and alpha can or cannot be written into the frame buffer. The initial values are all GL_TRUE, indicating that the color components can be written.
    :type green: int
    :param blue: Specify whether red, green, blue, and alpha can or cannot be written into the frame buffer. The initial values are all GL_TRUE, indicating that the color components can be written.
    :type blue: int
    :param alpha: Specify whether red, green, blue, and alpha can or cannot be written into the frame buffer. The initial values are all GL_TRUE, indicating that the color components can be written.
    :type alpha: int
    """

    ...

def glCompileShader(shader: int):
    """Compiles a shader object.

    :param shader: Specifies the shader object to be compiled.
    :type shader: int
    """

    ...

def glCompressedTexImage1D(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: int, p6: typing.Any
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: typing.Any
    :rtype: typing.Any
    """

    ...

def glCompressedTexImage2D(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: int, p6: int, p7: typing.Any
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :type p7: typing.Any
    :rtype: typing.Any
    """

    ...

def glCompressedTexImage3D(
    p0: int,
    p1: int,
    p2: int,
    p3: int,
    p4: int,
    p5: int,
    p6: int,
    p7: int,
    p8: typing.Any,
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :type p7: int
    :type p8: typing.Any
    :rtype: typing.Any
    """

    ...

def glCompressedTexSubImage1D(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: int, p6: typing.Any
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: typing.Any
    :rtype: typing.Any
    """

    ...

def glCompressedTexSubImage2D(
    p0: int,
    p1: int,
    p2: int,
    p3: int,
    p4: int,
    p5: int,
    p6: int,
    p7: int,
    p8: typing.Any,
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :type p7: int
    :type p8: typing.Any
    :rtype: typing.Any
    """

    ...

def glCopyTexImage1D(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: int, p6: int
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :rtype: typing.Any
    """

    ...

def glCopyTexImage2D(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    level: int,
    internalformat: int,
    x: int,
    y: int,
    width: int,
    height: int,
    border: int,
):
    """Copy pixels into a 2D texture image

    :param target: Specifies the target texture.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param level: Specifies the level-of-detail number. Level 0 is the base image level. Level n is the nth mipmap reduction image.
    :type level: int
    :param internalformat: Specifies the number of color components in the texture.
    :type internalformat: int
    :param width: Specifies the width of the texture image. Must be 2n+2(border) for some integer n. All implementations support texture images that are at least 64 texels wide.
    :type width: int
    :param x: Specify the window coordinates of the first pixel that is copied from the frame buffer. This location is the lower left corner of a rectangular block of pixels.
    :type x: int
    :param y: Specify the window coordinates of the first pixel that is copied from the frame buffer. This location is the lower left corner of a rectangular block of pixels.
    :type y: int
    :param height: Specifies the height of the texture image. Must be 2m+2(border) for some integer m. All implementations support texture images that are at least 64 texels high.
    :type height: int
    :param border: Specifies the width of the border. Must be either 0 or 1.
    :type border: int
    """

    ...

def glCopyTexSubImage1D(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: int
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :rtype: typing.Any
    """

    ...

def glCopyTexSubImage2D(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: int, p6: int, p7: int
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :type p7: int
    :rtype: typing.Any
    """

    ...

def glCopyTexSubImage3D(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: int, p6: int, p7: int, p8: int
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :type p7: int
    :type p8: int
    :rtype: typing.Any
    """

    ...

def glCreateProgram() -> int:
    """Creates a program object

    :rtype: int
    :return: The new program or zero if an error occurs.
    """

    ...

def glCreateShader(shaderType: typing.Any) -> int:
    """Creates a shader object.

    :type shaderType: typing.Any
    :rtype: int
    :return: 0 if an error occurs.
    """

    ...

def glCullFace(mode: typing.Union[typing.Set[str], typing.Set[int]]):
    """Specify whether front- or back-facing facets can be culled

    :param mode: Specifies whether front- or back-facing facets are candidates for culling.
    :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glDeleteBuffers(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glDeleteFramebuffers(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glDeleteProgram(program: int):
    """Deletes a program object.

    :param program: Specifies the program object to be deleted.
    :type program: int
    """

    ...

def glDeleteQueries(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glDeleteRenderbuffers(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glDeleteShader(shader: int):
    """Deletes a shader object.

    :param shader: Specifies the shader object to be deleted.
    :type shader: int
    """

    ...

def glDeleteTextures(n: int, textures: "Buffer"):
    """Delete named textures

    :param n: Specifies the number of textures to be deleted
    :type n: int
    :param textures: Specifies an array of textures to be deleted
    :type textures: 'Buffer'
    """

    ...

def glDeleteVertexArrays(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glDepthFunc(func: typing.Union[typing.Set[str], typing.Set[int]]):
    """Specify the value used for depth buffer comparisons

    :param func: Specifies the depth comparison function.
    :type func: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glDepthMask(flag: int):
    """Enable or disable writing into the depth buffer

    :param flag: Specifies whether the depth buffer is enabled for writing. If flag is GL_FALSE, depth buffer writing is disabled. Otherwise, it is enabled. Initially, depth buffer writing is enabled.
    :type flag: int
    """

    ...

def glDepthRange(zNear: int, zFar: int):
    """Specify mapping of depth values from normalized device coordinates to window coordinates

    :param zNear: Specifies the mapping of the near clipping plane to window coordinates. The initial value is 0.
    :type zNear: int
    :param zFar: Specifies the mapping of the far clipping plane to window coordinates. The initial value is 1.
    :type zFar: int
    """

    ...

def glDetachShader(program: int, shader: int):
    """Detaches a shader object from a program object to which it is attached.

    :param program: Specifies the program object from which to detach the shader object.
    :type program: int
    :param shader: pecifies the program object from which to detach the shader object.
    :type shader: int
    """

    ...

def glDisable(cap: typing.Union[typing.Set[str], typing.Set[int]]):
    """Disable server-side GL capabilities

    :param cap: Specifies a symbolic constant indicating a GL capability.
    :type cap: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glDisableVertexAttribArray(p0: int) -> typing.Any:
    """

    :type p0: int
    :rtype: typing.Any
    """

    ...

def glDrawArrays(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glDrawBuffer(mode: typing.Union[typing.Set[str], typing.Set[int]]):
    """Specify which color buffers are to be drawn into

    :param mode: Specifies up to four color buffers to be drawn into.
    :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glDrawBuffers(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glDrawElements(p0: int, p1: int, p2: int, p3: typing.Any) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: typing.Any
    :rtype: typing.Any
    """

    ...

def glDrawRangeElements(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: typing.Any
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: typing.Any
    :rtype: typing.Any
    """

    ...

def glEdgeFlag(flag: typing.Any):
    """B{glEdgeFlag, glEdgeFlagv} Flag edges as either boundary or non-boundary

    :param flag: Specifies the current edge flag value.The initial value is GL_TRUE.
    :type flag: typing.Any
    """

    ...

def glEnable(cap: typing.Union[typing.Set[str], typing.Set[int]]):
    """Enable server-side GL capabilities

    :param cap: Specifies a symbolic constant indicating a GL capability.
    :type cap: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glEnableVertexAttribArray(p0: int) -> typing.Any:
    """

    :type p0: int
    :rtype: typing.Any
    """

    ...

def glEndQuery(p0: int) -> typing.Any:
    """

    :type p0: int
    :rtype: typing.Any
    """

    ...

def glEvalCoord(u: typing.Any, v: typing.Any):
    """B{glEvalCoord1d, glEvalCoord1f, glEvalCoord2d, glEvalCoord2f, glEvalCoord1dv, glEvalCoord1fv, glEvalCoord2dv, glEvalCoord2fv} Evaluate enabled one- and two-dimensional maps

    :param u: Specifies a value that is the domain coordinate u to the basis function defined in a previous glMap1 or glMap2 command. If the function prototype ends in 'v' then u specifies a pointer to an array containing either one or two domain coordinates. The first coordinate is u. The second coordinate is v, which is present only in glEvalCoord2 versions.
    :type u: typing.Any
    :param v: Specifies a value that is the domain coordinate v to the basis function defined in a previous glMap2 command. This argument is not present in a glEvalCoord1 command.
    :type v: typing.Any
    """

    ...

def glEvalMesh(mode: typing.Union[typing.Set[str], typing.Set[int]], i1: int, i2: int):
    """B{glEvalMesh1 or glEvalMesh2} Compute a one- or two-dimensional grid of points or lines

    :param mode: In glEvalMesh1, specifies whether to compute a one-dimensional mesh of points or lines.
    :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    :param i1: Specify the first and last integer values for the grid domain variable i.
    :type i1: int
    :param i2: Specify the first and last integer values for the grid domain variable i.
    :type i2: int
    """

    ...

def glEvalPoint(i: int, j: int):
    """B{glEvalPoint1 and glEvalPoint2} Generate and evaluate a single point in a mesh

    :param i: Specifies the integer value for grid domain variable i.
    :type i: int
    :param j: Specifies the integer value for grid domain variable j (glEvalPoint2 only).
    :type j: int
    """

    ...

def glFeedbackBuffer(
    size: int, type: typing.Union[typing.Set[str], typing.Set[int]], buffer: "Buffer"
):
    """Controls feedback mode

    :param size: Specifies the maximum number of values that can be written into buffer.
    :type size: int
    :param type: Specifies a symbolic constant that describes the information that will be returned for each vertex.
    :type type: typing.Union[typing.Set[str], typing.Set[int]]
    :param buffer: Returns the feedback data.
    :type buffer: 'Buffer'
    """

    ...

def glFinish():
    """Block until all GL execution is complete"""

    ...

def glFlush():
    """Force Execution of GL commands in finite time"""

    ...

def glFog(pname: typing.Union[typing.Set[str], typing.Set[int]], param: typing.Any):
    """B{glFogf, glFogi, glFogfv, glFogiv} Specify fog parameters

    :param pname: Specifies a single-valued fog parameter. If the function prototype ends in 'v' specifies a fog parameter.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param param: Specifies the value or values to be assigned to pname. GL_FOG_COLOR requires an array of four values. All other parameters accept an array containing only a single value.
    :type param: typing.Any
    """

    ...

def glFramebufferRenderbuffer(p0: int, p1: int, p2: int, p3: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :rtype: typing.Any
    """

    ...

def glFramebufferTexture(p0: int, p1: int, p2: int, p3: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :rtype: typing.Any
    """

    ...

def glFrontFace(mode: typing.Union[typing.Set[str], typing.Set[int]]):
    """Define front- and back-facing polygons

    :param mode: Specifies the orientation of front-facing polygons.
    :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glGenBuffers(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glGenFramebuffers(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glGenQueries(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glGenRenderbuffers(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glGenTextures(n: int, textures: "Buffer"):
    """Generate texture names

    :param n: Specifies the number of textures name to be generated.
    :type n: int
    :param textures: Specifies an array in which the generated textures names are stored.
    :type textures: 'Buffer'
    """

    ...

def glGenVertexArrays(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glGet(pname: typing.Union[typing.Set[str], typing.Set[int]], param: typing.Any):
    """B{glGetBooleanv, glGetfloatv, glGetFloatv, glGetIntegerv} Return the value or values of a selected parameter

    :param pname: Specifies the parameter value to be returned.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param param: Returns the value or values of the specified parameter.
    :type param: typing.Any
    """

    ...

def glGetActiveAttrib(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: int, p6: int
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :rtype: typing.Any
    """

    ...

def glGetActiveUniform(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: int, p6: int
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :rtype: typing.Any
    """

    ...

def glGetActiveUniformBlockName(
    p0: int, p1: int, p2: int, p3: int, p4: int
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :rtype: typing.Any
    """

    ...

def glGetActiveUniformBlockiv(p0: int, p1: int, p2: int, p3: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :rtype: typing.Any
    """

    ...

def glGetActiveUniformName(p0: int, p1: int, p2: int, p3: int, p4: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :rtype: typing.Any
    """

    ...

def glGetActiveUniformsiv(p0: int, p1: int, p2: int, p3: int, p4: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :rtype: typing.Any
    """

    ...

def glGetAttachedShaders(
    program: int, maxCount: int, count: "Buffer", shaders: "Buffer"
):
    """Returns the handles of the shader objects attached to a program object.

    :param program: Specifies the program object to be queried.
    :type program: int
    :param maxCount: Specifies the size of the array for storing the returned object names.
    :type maxCount: int
    :param count: Returns the number of names actually returned in objects.
    :type count: 'Buffer'
    :param shaders: Specifies an array that is used to return the names of attached shader objects.
    :type shaders: 'Buffer'
    """

    ...

def glGetAttribLocation(p0: int, p1: str) -> int:
    """

    :type p0: int
    :type p1: str
    :rtype: int
    """

    ...

def glGetBooleanv(p0: int, p1: bool) -> typing.Any:
    """

    :type p0: int
    :type p1: bool
    :rtype: typing.Any
    """

    ...

def glGetBufferParameteri64v(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glGetBufferParameteriv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glGetBufferPointerv(p0: int, p1: int, p2: typing.Any) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: typing.Any
    :rtype: typing.Any
    """

    ...

def glGetBufferSubData(p0: int, p1: int, p2: int, p3: typing.Any) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: typing.Any
    :rtype: typing.Any
    """

    ...

def glGetCompressedTexImage(p0: int, p1: int, p2: typing.Any) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: typing.Any
    :rtype: typing.Any
    """

    ...

def glGetDoublev(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glGetError():
    """Return error information"""

    ...

def glGetFloatv(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glGetIntegerv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glGetLight(
    light: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: "Buffer",
):
    """B{glGetLightfv and glGetLightiv} Return light source parameter values

    :param light: Specifies a light source. The number of possible lights depends on the implementation, but at least eight lights are supported. They are identified by symbolic names of the form GL_LIGHTi where 0 < i < GL_MAX_LIGHTS.
    :type light: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies a light source parameter for light.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param params: Returns the requested data.
    :type params: 'Buffer'
    """

    ...

def glGetMap(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    query: typing.Union[typing.Set[str], typing.Set[int]],
    v: "Buffer",
):
    """B{glGetMapdv, glGetMapfv, glGetMapiv} Return evaluator parameters

    :param target: Specifies the symbolic name of a map.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param query: Specifies which parameter to return.
    :type query: typing.Union[typing.Set[str], typing.Set[int]]
    :param v: Returns the requested data.
    :type v: 'Buffer'
    """

    ...

def glGetMaterial(
    face: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: "Buffer",
):
    """B{glGetMaterialfv, glGetMaterialiv} Return material parameters

    :param face: Specifies which of the two materials is being queried. representing the front and back materials, respectively.
    :type face: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies the material parameter to return.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param params: Returns the requested data.
    :type params: 'Buffer'
    """

    ...

def glGetMultisamplefv(p0: int, p1: int, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glGetPixelMap(
    map: typing.Union[typing.Set[str], typing.Set[int]], values: "Buffer"
):
    """B{glGetPixelMapfv, glGetPixelMapuiv, glGetPixelMapusv} Return the specified pixel map

    :param map: Specifies the name of the pixel map to return.
    :type map: typing.Union[typing.Set[str], typing.Set[int]]
    :param values: Returns the pixel map contents.
    :type values: 'Buffer'
    """

    ...

def glGetProgramInfoLog(
    program: int, maxLength: int, length: "Buffer", infoLog: "Buffer"
):
    """Returns the information log for a program object.

    :param program: Specifies the program object whose information log is to be queried.
    :type program: int
    :param maxLength: Specifies the size of the character buffer for storing the returned information log.
    :type maxLength: int
    :param length: Returns the length of the string returned in **infoLog** (excluding the null terminator).
    :type length: 'Buffer'
    :param infoLog: Specifies an array of characters that is used to return the information log.
    :type infoLog: 'Buffer'
    """

    ...

def glGetProgramiv(program: int, pname: int, params: "Buffer"):
    """Returns a parameter from a program object.

    :param program: Specifies the program object to be queried.
    :type program: int
    :param pname: Specifies the object parameter.
    :type pname: int
    :param params: Returns the requested object parameter.
    :type params: 'Buffer'
    """

    ...

def glGetQueryObjectiv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glGetQueryObjectuiv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glGetQueryiv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glGetShaderInfoLog(program, maxLength: int, length: "Buffer", infoLog: "Buffer"):
    """Returns the information log for a shader object.

    :param shader: Specifies the shader object whose information log is to be queried.
    :type shader: int
    :param maxLength: Specifies the size of the character buffer for storing the returned information log.
    :type maxLength: int
    :param length: Returns the length of the string returned in **infoLog** (excluding the null terminator).
    :type length: 'Buffer'
    :param infoLog: Specifies an array of characters that is used to return the information log.
    :type infoLog: 'Buffer'
    """

    ...

def glGetShaderSource(shader: int, bufSize: int, length: "Buffer", source: "Buffer"):
    """Returns the source code string from a shader object

    :param shader: Specifies the shader object to be queried.
    :type shader: int
    :param bufSize: Specifies the size of the character buffer for storing the returned source code string.
    :type bufSize: int
    :param length: Returns the length of the string returned in source (excluding the null terminator).
    :type length: 'Buffer'
    :param source: Specifies an array of characters that is used to return the source code string.
    :type source: 'Buffer'
    """

    ...

def glGetShaderiv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glGetString(name: typing.Union[typing.Set[str], typing.Set[int]]):
    """Return a string describing the current GL connection

    :param name: Specifies a symbolic constant.
    :type name: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glGetStringi(p0: int, p1: int) -> str:
    """

    :type p0: int
    :type p1: int
    :rtype: str
    """

    ...

def glGetTexEnv(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: "Buffer",
):
    """B{glGetTexEnvfv, glGetTexEnviv} Return texture environment parameters

    :param target: Specifies a texture environment. Must be GL_TEXTURE_ENV.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies the symbolic name of a texture environment parameter.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param params: Returns the requested data.
    :type params: 'Buffer'
    """

    ...

def glGetTexGen(
    coord: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: "Buffer",
):
    """B{glGetTexGendv, glGetTexGenfv, glGetTexGeniv} Return texture coordinate generation parameters

    :param coord: Specifies a texture coordinate.
    :type coord: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies the symbolic name of the value(s) to be returned.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param params: Returns the requested data.
    :type params: 'Buffer'
    """

    ...

def glGetTexImage(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    level: int,
    format: typing.Union[typing.Set[str], typing.Set[int]],
    type: typing.Union[typing.Set[str], typing.Set[int]],
    pixels: "Buffer",
):
    """Return a texture image

    :param target: Specifies which texture is to be obtained.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param level: Specifies the level-of-detail number of the desired image. Level 0 is the base image level. Level n is the nth mipmap reduction image.
    :type level: int
    :param format: Specifies a pixel format for the returned data.
    :type format: typing.Union[typing.Set[str], typing.Set[int]]
    :param type: Specifies a pixel type for the returned data.
    :type type: typing.Union[typing.Set[str], typing.Set[int]]
    :param pixels: Returns the texture image. Should be a pointer to an array of the type specified by type
    :type pixels: 'Buffer'
    """

    ...

def glGetTexLevelParameter(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    level: int,
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: "Buffer",
):
    """B{glGetTexLevelParameterfv, glGetTexLevelParameteriv} return texture parameter values for a specific level of detail

    :param target: Specifies the symbolic name of the target texture.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param level: Specifies the level-of-detail number of the desired image. Level 0 is the base image level. Level n is the nth mipmap reduction image.
    :type level: int
    :param pname: Specifies the symbolic name of a texture parameter.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param params: Returns the requested data.
    :type params: 'Buffer'
    """

    ...

def glGetTexLevelParameterfv(p0: int, p1: int, p2: int, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glGetTexLevelParameteriv(p0: int, p1: int, p2: int, p3: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :rtype: typing.Any
    """

    ...

def glGetTexParameter(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: "Buffer",
):
    """B{glGetTexParameterfv, glGetTexParameteriv} Return texture parameter values

    :param target: Specifies the symbolic name of the target texture.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies the symbolic name the target texture.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param params: Returns the texture parameters.
    :type params: 'Buffer'
    """

    ...

def glGetTexParameterfv(p0: int, p1: int, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glGetTexParameteriv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glGetUniformBlockIndex(p0: int, p1: str) -> int:
    """

    :type p0: int
    :type p1: str
    :rtype: int
    """

    ...

def glGetUniformIndices(p0: int, p1: int, p2: int, p3: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :rtype: typing.Any
    """

    ...

def glGetUniformLocation(p0: int, p1: str) -> int:
    """

    :type p0: int
    :type p1: str
    :rtype: int
    """

    ...

def glGetUniformfv(p0: int, p1: int, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glGetUniformiv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glGetVertexAttribPointerv(p0: int, p1: int, p2: typing.Any) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: typing.Any
    :rtype: typing.Any
    """

    ...

def glGetVertexAttribdv(p0: int, p1: int, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glGetVertexAttribfv(p0: int, p1: int, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glGetVertexAttribiv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glHint(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    mode: typing.Union[typing.Set[str], typing.Set[int]],
):
    """Specify implementation-specific hints

    :param target: Specifies a symbolic constant indicating the behavior to be controlled.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param mode: Specifies a symbolic constant indicating the desired behavior.
    :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glIsBuffer(p0: int) -> bool:
    """

    :type p0: int
    :rtype: bool
    """

    ...

def glIsEnabled(cap: typing.Union[typing.Set[str], typing.Set[int]]):
    """Test whether a capability is enabled

    :param cap: Specifies a constant representing a GL capability.
    :type cap: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glIsProgram(program: int):
    """Determines if a name corresponds to a program object

    :param program: Specifies a potential program object.
    :type program: int
    """

    ...

def glIsQuery(p0: int) -> bool:
    """

    :type p0: int
    :rtype: bool
    """

    ...

def glIsShader(shader: int):
    """Determines if a name corresponds to a shader object.

    :param shader: Specifies a potential shader object.
    :type shader: int
    """

    ...

def glIsTexture(texture: int):
    """Determine if a name corresponds to a texture

    :param texture: Specifies a value that may be the name of a texture.
    :type texture: int
    """

    ...

def glIsVertexArray(p0: int) -> bool:
    """

    :type p0: int
    :rtype: bool
    """

    ...

def glLight(
    light: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    param: typing.Any,
):
    """B{glLightf,glLighti, glLightfv, glLightiv} Set the light source parameters

    :param light: Specifies a light. The number of lights depends on the implementation, but at least eight lights are supported. They are identified by symbolic names of the form GL_LIGHTi where 0 < i < GL_MAX_LIGHTS.
    :type light: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies a single-valued light source parameter for light.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param param: Specifies the value that parameter pname of light source light will be set to. If function prototype ends in 'v' specifies a pointer to the value or values that parameter pname of light source light will be set to.
    :type param: typing.Any
    """

    ...

def glLightModel(
    pname: typing.Union[typing.Set[str], typing.Set[int]], param: typing.Any
):
    """B{glLightModelf, glLightModeli, glLightModelfv, glLightModeliv} Set the lighting model parameters

    :param pname: Specifies a single-value light model parameter.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param param: Specifies the value that param will be set to. If function prototype ends in 'v' specifies a pointer to the value or values that param will be set to.
    :type param: typing.Any
    """

    ...

def glLineWidth(width: float):
    """Specify the width of rasterized lines.

    :param width: Specifies the width of rasterized lines. The initial value is 1.
    :type width: float
    """

    ...

def glLinkProgram(program: int):
    """Links a program object.

    :param program: Specifies the handle of the program object to be linked.
    :type program: int
    """

    ...

def glLoadMatrix(m: "Buffer"):
    """B{glLoadMatrixd, glLoadMatixf} Replace the current matrix with the specified matrix

    :param m: Specifies a pointer to 16 consecutive values, which are used as the elements of a 4x4 column-major matrix.
    :type m: 'Buffer'
    """

    ...

def glLogicOp(opcode: typing.Union[typing.Set[str], typing.Set[int]]):
    """Specify a logical pixel operation for color index rendering

    :param opcode: Specifies a symbolic constant that selects a logical operation.
    :type opcode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glMap1(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    u1: typing.Any,
    u2: typing.Any,
    stride: int,
    order: int,
    points: "Buffer",
):
    """B{glMap1d, glMap1f} Define a one-dimensional evaluator

    :param target: Specifies the kind of values that are generated by the evaluator.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param u1: Specify a linear mapping of u, as presented to glEvalCoord1, to ^, t he variable that is evaluated by the equations specified by this command.
    :type u1: typing.Any
    :param u2: Specify a linear mapping of u, as presented to glEvalCoord1, to ^, t he variable that is evaluated by the equations specified by this command.
    :type u2: typing.Any
    :param stride: Specifies the number of floats or float (double)s between the beginning of one control point and the beginning of the next one in the data structure referenced in points. This allows control points to be embedded in arbitrary data structures. The only constraint is that the values for a particular control point must occupy contiguous memory locations.
    :type stride: int
    :param order: Specifies the number of control points. Must be positive.
    :type order: int
    :param points: Specifies a pointer to the array of control points.
    :type points: 'Buffer'
    """

    ...

def glMap2(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    u1: typing.Any,
    u2: typing.Any,
    ustride: int,
    uorder: int,
    v1: typing.Any,
    v2: typing.Any,
    vstride: int,
    vorder: int,
    points: "Buffer",
):
    """B{glMap2d, glMap2f} Define a two-dimensional evaluator

    :param target: Specifies the kind of values that are generated by the evaluator.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param u1: Specify a linear mapping of u, as presented to glEvalCoord2, to ^, t he variable that is evaluated by the equations specified by this command. Initially u1 is 0 and u2 is 1.
    :type u1: typing.Any
    :param u2: Specify a linear mapping of u, as presented to glEvalCoord2, to ^, t he variable that is evaluated by the equations specified by this command. Initially u1 is 0 and u2 is 1.
    :type u2: typing.Any
    :param ustride: Specifies the number of floats or float (double)s between the beginning of control point R and the beginning of control point R ij, where i and j are the u and v control point indices, respectively. This allows control points to be embedded in arbitrary data structures. The only constraint is that the values for a particular control point must occupy contiguous memory locations. The initial value of ustride is 0.
    :type ustride: int
    :param uorder: Specifies the dimension of the control point array in the u axis. Must be positive. The initial value is 1.
    :type uorder: int
    :param v1: Specify a linear mapping of v, as presented to glEvalCoord2, to ^, one of the two variables that are evaluated by the equations specified by this command. Initially, v1 is 0 and v2 is 1.
    :type v1: typing.Any
    :param v2: Specify a linear mapping of v, as presented to glEvalCoord2, to ^, one of the two variables that are evaluated by the equations specified by this command. Initially, v1 is 0 and v2 is 1.
    :type v2: typing.Any
    :param vstride: Specifies the number of floats or float (double)s between the beginning of control point R and the beginning of control point R ij, where i and j are the u and v control point(indices, respectively. This allows control points to be embedded in arbitrary data structures. The only constraint is that the values for a particular control point must occupy contiguous memory locations. The initial value of vstride is 0.
    :type vstride: int
    :param vorder: Specifies the dimension of the control point array in the v axis. Must be positive. The initial value is 1.
    :type vorder: int
    :param points: Specifies a pointer to the array of control points.
    :type points: 'Buffer'
    """

    ...

def glMapBuffer(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glMapGrid(
    un: int, u1: typing.Any, u2: typing.Any, vn: int, v1: typing.Any, v2: typing.Any
):
    """B{glMapGrid1d, glMapGrid1f, glMapGrid2d, glMapGrid2f} Define a one- or two-dimensional mesh

    :param un: Specifies the number of partitions in the grid range interval [u1, u2]. Must be positive.
    :type un: int
    :param u1: Specify the mappings for integer grid domain values i=0 and i=un.
    :type u1: typing.Any
    :param u2: Specify the mappings for integer grid domain values i=0 and i=un.
    :type u2: typing.Any
    :param vn: Specifies the number of partitions in the grid range interval [v1, v2] (glMapGrid2 only).
    :type vn: int
    :param v1: Specify the mappings for integer grid domain values j=0 and j=vn (glMapGrid2 only).
    :type v1: typing.Any
    :param v2: Specify the mappings for integer grid domain values j=0 and j=vn (glMapGrid2 only).
    :type v2: typing.Any
    """

    ...

def glMaterial(
    face: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: int,
):
    """Specify material parameters for the lighting model.

    :type face: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies the single-valued material parameter of the face or faces that is being updated. Must be GL_SHININESS.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param params: Specifies the value that parameter GL_SHININESS will be set to. If function prototype ends in 'v' specifies a pointer to the value or values that pname will be set to.
    :type params: int
    """

    ...

def glMultMatrix(m: "Buffer"):
    """B{glMultMatrixd, glMultMatrixf} Multiply the current matrix with the specified matrix

    :param m: Points to 16 consecutive values that are used as the elements of a 4x4 column major matrix.
    :type m: 'Buffer'
    """

    ...

def glNormal3(nx: typing.Any, ny: typing.Any, nz: typing.Any, v: "Buffer"):
    """B{Normal3b, Normal3bv, Normal3d, Normal3dv, Normal3f, Normal3fv, Normal3i, Normal3iv, Normal3s, Normal3sv} Set the current normal vector

    :param nx: Specify the x, y, and z coordinates of the new current normal. The initial value of the current normal is the unit vector, (0, 0, 1).
    :type nx: typing.Any
    :param ny: Specify the x, y, and z coordinates of the new current normal. The initial value of the current normal is the unit vector, (0, 0, 1).
    :type ny: typing.Any
    :param nz: Specify the x, y, and z coordinates of the new current normal. The initial value of the current normal is the unit vector, (0, 0, 1).
    :type nz: typing.Any
    :param v: the x, y, and z coordinates of the new current normal.
    :type v: 'Buffer'
    """

    ...

def glPixelMap(
    map: typing.Union[typing.Set[str], typing.Set[int]], mapsize: int, values: "Buffer"
):
    """B{glPixelMapfv, glPixelMapuiv, glPixelMapusv} Set up pixel transfer maps

    :param map: Specifies a symbolic map name.
    :type map: typing.Union[typing.Set[str], typing.Set[int]]
    :param mapsize: Specifies the size of the map being defined.
    :type mapsize: int
    :param values: Specifies an array of mapsize values.
    :type values: 'Buffer'
    """

    ...

def glPixelStore(
    pname: typing.Union[typing.Set[str], typing.Set[int]], param: typing.Any
):
    """B{glPixelStoref, glPixelStorei} Set pixel storage modes

    :param pname: Specifies the symbolic name of the parameter to be set. Six values affect the packing of pixel data into memory. Six more affect the unpacking of pixel data from memory.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param param: Specifies the value that pname is set to.
    :type param: typing.Any
    """

    ...

def glPixelStoref(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glPixelStorei(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glPixelTransfer(
    pname: typing.Union[typing.Set[str], typing.Set[int]], param: typing.Any
):
    """B{glPixelTransferf, glPixelTransferi} Set pixel transfer modes

    :param pname: Specifies the symbolic name of the pixel transfer parameter to be set.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param param: Specifies the value that pname is set to.
    :type param: typing.Any
    """

    ...

def glPointSize(size: float):
    """Specify the diameter of rasterized points

    :param size: Specifies the diameter of rasterized points. The initial value is 1.
    :type size: float
    """

    ...

def glPolygonMode(
    face: typing.Union[typing.Set[str], typing.Set[int]],
    mode: typing.Union[typing.Set[str], typing.Set[int]],
):
    """Select a polygon rasterization mode

    :param face: Specifies the polygons that mode applies to. Must be GL_FRONT for front-facing polygons, GL_BACK for back- facing polygons, or GL_FRONT_AND_BACK for front- and back-facing polygons.
    :type face: typing.Union[typing.Set[str], typing.Set[int]]
    :param mode: Specifies how polygons will be rasterized. The initial value is GL_FILL for both front- and back- facing polygons.
    :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glPolygonOffset(factor: float, units: float):
    """Set the scale and units used to calculate depth values

    :param factor: Specifies a scale factor that is used to create a variable depth offset for each polygon. The initial value is 0.
    :type factor: float
    :param units: Is multiplied by an implementation-specific value to create a constant depth offset. The initial value is 0.
    :type units: float
    """

    ...

def glRasterPos(x: typing.Any, y: typing.Any, z: typing.Any, w: typing.Any):
    """B{glRasterPos2d, glRasterPos2f, glRasterPos2i, glRasterPos2s, glRasterPos3d, glRasterPos3f, glRasterPos3i, glRasterPos3s, glRasterPos4d, glRasterPos4f, glRasterPos4i, glRasterPos4s, glRasterPos2dv, glRasterPos2fv, glRasterPos2iv, glRasterPos2sv, glRasterPos3dv, glRasterPos3fv, glRasterPos3iv, glRasterPos3sv, glRasterPos4dv, glRasterPos4fv, glRasterPos4iv, glRasterPos4sv} Specify the raster position for pixel operations

    :param x: Specify the x,y,z, and w object coordinates (if present) for the raster position. If function prototype ends in 'v' specifies a pointer to an array of two, three, or four elements, specifying x, y, z, and w coordinates, respectively.
    :type x: typing.Any
    :param y: Specify the x,y,z, and w object coordinates (if present) for the raster position. If function prototype ends in 'v' specifies a pointer to an array of two, three, or four elements, specifying x, y, z, and w coordinates, respectively.
    :type y: typing.Any
    :param z: Specify the x,y,z, and w object coordinates (if present) for the raster position. If function prototype ends in 'v' specifies a pointer to an array of two, three, or four elements, specifying x, y, z, and w coordinates, respectively.
    :type z: typing.Any
    :param w: Specify the x,y,z, and w object coordinates (if present) for the raster position. If function prototype ends in 'v' specifies a pointer to an array of two, three, or four elements, specifying x, y, z, and w coordinates, respectively.
    :type w: typing.Any
    """

    ...

def glReadBuffer(mode: typing.Union[typing.Set[str], typing.Set[int]]):
    """Select a color buffer source for pixels.

    :param mode: Specifies a color buffer.
    :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glReadPixels(
    x: int,
    y: int,
    width: int,
    height: int,
    format: typing.Union[typing.Set[str], typing.Set[int]],
    type: typing.Union[typing.Set[str], typing.Set[int]],
    pixels: "Buffer",
):
    """Read a block of pixels from the frame buffer

    :param x: Specify the window coordinates of the first pixel that is read from the frame buffer. This location is the lower left corner of a rectangular block of pixels.
    :type x: int
    :param y: Specify the window coordinates of the first pixel that is read from the frame buffer. This location is the lower left corner of a rectangular block of pixels.
    :type y: int
    :param width: Specify the dimensions of the pixel rectangle. width and height of one correspond to a single pixel.
    :type width: int
    :param height: Specify the dimensions of the pixel rectangle. width and height of one correspond to a single pixel.
    :type height: int
    :param format: Specifies the format of the pixel data.
    :type format: typing.Union[typing.Set[str], typing.Set[int]]
    :param type: Specifies the data type of the pixel data.
    :type type: typing.Union[typing.Set[str], typing.Set[int]]
    :param pixels: Returns the pixel data.
    :type pixels: 'Buffer'
    """

    ...

def glRect(
    x1: typing.Any,
    y1: typing.Any,
    x2: typing.Any,
    y2: typing.Any,
    v1: typing.Any,
    v2: typing.Any,
):
    """B{glRectd, glRectf, glRecti, glRects, glRectdv, glRectfv, glRectiv, glRectsv} Draw a rectangle

    :param x1: Specify one vertex of a rectangle
    :type x1: typing.Any
    :param y1: Specify one vertex of a rectangle
    :type y1: typing.Any
    :param x2: Specify the opposite vertex of the rectangle
    :type x2: typing.Any
    :param y2: Specify the opposite vertex of the rectangle
    :type y2: typing.Any
    :param v1: Specifies a pointer to one vertex of a rectangle and the pointer to the opposite vertex of the rectangle
    :type v1: typing.Any
    :param v2: Specifies a pointer to one vertex of a rectangle and the pointer to the opposite vertex of the rectangle
    :type v2: typing.Any
    """

    ...

def glRenderbufferStorage(p0: int, p1: int, p2: int, p3: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :rtype: typing.Any
    """

    ...

def glRotate(angle: typing.Any, x: typing.Any, y: typing.Any, z: typing.Any):
    """B{glRotated, glRotatef} Multiply the current matrix by a rotation matrix

    :param angle: Specifies the angle of rotation in degrees.
    :type angle: typing.Any
    :param x: Specify the x, y, and z coordinates of a vector respectively.
    :type x: typing.Any
    :param y: Specify the x, y, and z coordinates of a vector respectively.
    :type y: typing.Any
    :param z: Specify the x, y, and z coordinates of a vector respectively.
    :type z: typing.Any
    """

    ...

def glSampleCoverage(p0: float, p1: bool) -> typing.Any:
    """

    :type p0: float
    :type p1: bool
    :rtype: typing.Any
    """

    ...

def glSampleMaski(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glScale(x: typing.Any, y: typing.Any, z: typing.Any):
    """B{glScaled, glScalef} Multiply the current matrix by a general scaling matrix

    :param x: Specify scale factors along the x, y, and z axes, respectively.
    :type x: typing.Any
    :param y: Specify scale factors along the x, y, and z axes, respectively.
    :type y: typing.Any
    :param z: Specify scale factors along the x, y, and z axes, respectively.
    :type z: typing.Any
    """

    ...

def glScissor(x: int, y: int, width: int, height: int):
    """Define the scissor box

    :param x: Specify the lower left corner of the scissor box. Initially (0, 0).
    :type x: int
    :param y: Specify the lower left corner of the scissor box. Initially (0, 0).
    :type y: int
    :type width: int
    :type height: int
    :param width height:  Specify the width and height of the scissor box. When a GL context is first attached to a window, width and height are set to the dimensions of that window.
    :type width height: typing.Any
    """

    ...

def glShaderSource(shader: int, shader_string: str):
    """Replaces the source code in a shader object.

    :param shader: Specifies the handle of the shader object whose source code is to be replaced.
    :type shader: int
    :param shader_string: The shader string.
    :type shader_string: str
    """

    ...

def glStencilFunc(
    func: typing.Union[typing.Set[str], typing.Set[int]], ref: int, mask: int
):
    """Set function and reference value for stencil testing

    :param func: Specifies the test function.
    :type func: typing.Union[typing.Set[str], typing.Set[int]]
    :param ref: Specifies the reference value for the stencil test. ref is clamped to the range [0,2n-1], where n is the number of bitplanes in the stencil buffer. The initial value is 0.
    :type ref: int
    :param mask: Specifies a mask that is ANDed with both the reference value and the stored stencil value when the test is done. The initial value is all 1's.
    :type mask: int
    """

    ...

def glStencilFuncSeparate(p0: int, p1: int, p2: int, p3: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :rtype: typing.Any
    """

    ...

def glStencilMask(mask: int):
    """Control the writing of individual bits in the stencil planes

    :param mask: Specifies a bit mask to enable and disable writing of individual bits in the stencil planes. Initially, the mask is all 1's.
    :type mask: int
    """

    ...

def glStencilMaskSeparate(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glStencilOp(
    fail: typing.Union[typing.Set[str], typing.Set[int]],
    zfail: typing.Union[typing.Set[str], typing.Set[int]],
    zpass: typing.Union[typing.Set[str], typing.Set[int]],
):
    """Set stencil test actions

    :param fail: Specifies the action to take when the stencil test fails. The initial value is GL_KEEP.
    :type fail: typing.Union[typing.Set[str], typing.Set[int]]
    :param zfail: Specifies the stencil action when the stencil test passes, but the depth test fails. zfail accepts the same symbolic constants as fail. The initial value is GL_KEEP.
    :type zfail: typing.Union[typing.Set[str], typing.Set[int]]
    :param zpass: Specifies the stencil action when both the stencil test and the depth test pass, or when the stencil test passes and either there is no depth buffer or depth testing is not enabled. zpass accepts the same symbolic constants as fail. The initial value is GL_KEEP.
    :type zpass: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glStencilOpSeparate(p0: int, p1: int, p2: int, p3: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :rtype: typing.Any
    """

    ...

def glTexCoord(s: typing.Any, t: typing.Any, r: typing.Any, q: typing.Any, v: "Buffer"):
    """B{glTexCoord1d, glTexCoord1f, glTexCoord1i, glTexCoord1s, glTexCoord2d, glTexCoord2f, glTexCoord2i, glTexCoord2s, glTexCoord3d, glTexCoord3f, glTexCoord3i, glTexCoord3s, glTexCoord4d, glTexCoord4f, glTexCoord4i, glTexCoord4s, glTexCoord1dv, glTexCoord1fv, glTexCoord1iv, glTexCoord1sv, glTexCoord2dv, glTexCoord2fv, glTexCoord2iv, glTexCoord2sv, glTexCoord3dv, glTexCoord3fv, glTexCoord3iv, glTexCoord3sv, glTexCoord4dv, glTexCoord4fv, glTexCoord4iv, glTexCoord4sv} Set the current texture coordinates

    :param s: Specify s, t, r, and q texture coordinates. Not all parameters are present in all forms of the command.
    :type s: typing.Any
    :param t: Specify s, t, r, and q texture coordinates. Not all parameters are present in all forms of the command.
    :type t: typing.Any
    :param r: Specify s, t, r, and q texture coordinates. Not all parameters are present in all forms of the command.
    :type r: typing.Any
    :param q: Specify s, t, r, and q texture coordinates. Not all parameters are present in all forms of the command.
    :type q: typing.Any
    :param v: Specifies a pointer to an array of one, two, three, or four elements, which in turn specify the s, t, r, and q texture coordinates.
    :type v: 'Buffer'
    """

    ...

def glTexEnv(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    param: typing.Any,
):
    """B{glTextEnvf, glTextEnvi, glTextEnvfv, glTextEnviv} Set texture environment parameters

    :param target: Specifies a texture environment. Must be GL_TEXTURE_ENV.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies the symbolic name of a single-valued texture environment parameter. Must be GL_TEXTURE_ENV_MODE.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param param: Specifies a single symbolic constant. If function prototype ends in 'v' specifies a pointer to a parameter array that contains either a single symbolic constant or an RGBA color
    :type param: typing.Any
    """

    ...

def glTexGen(
    coord: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    param: typing.Any,
):
    """B{glTexGend, glTexGenf, glTexGeni, glTexGendv, glTexGenfv, glTexGeniv} Control the generation of texture coordinates

    :param coord: Specifies a texture coordinate.
    :type coord: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies the symbolic name of the texture- coordinate generation function.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param param: Specifies a single-valued texture generation parameter. If function prototype ends in 'v' specifies a pointer to an array of texture generation parameters. If pname is GL_TEXTURE_GEN_MODE, then the array must contain a single symbolic constant. Otherwise, params holds the coefficients for the texture-coordinate generation function specified by pname.
    :type param: typing.Any
    """

    ...

def glTexImage1D(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    level: int,
    internalformat: int,
    width: int,
    border: int,
    format: typing.Union[typing.Set[str], typing.Set[int]],
    type: typing.Union[typing.Set[str], typing.Set[int]],
    pixels: "Buffer",
):
    """Specify a one-dimensional texture image

    :param target: Specifies the target texture.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param level: Specifies the level-of-detail number. Level 0 is the base image level. Level n is the nth mipmap reduction image.
    :type level: int
    :param internalformat: Specifies the number of color components in the texture.
    :type internalformat: int
    :param width: Specifies the width of the texture image. Must be 2n+2(border) for some integer n. All implementations support texture images that are at least 64 texels wide. The height of the 1D texture image is 1.
    :type width: int
    :param border: Specifies the width of the border. Must be either 0 or 1.
    :type border: int
    :param format: Specifies the format of the pixel data.
    :type format: typing.Union[typing.Set[str], typing.Set[int]]
    :param type: Specifies the data type of the pixel data.
    :type type: typing.Union[typing.Set[str], typing.Set[int]]
    :param pixels: Specifies a pointer to the image data in memory.
    :type pixels: 'Buffer'
    """

    ...

def glTexImage2D(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    level: int,
    internalformat: int,
    width: int,
    height: int,
    border: int,
    format: typing.Union[typing.Set[str], typing.Set[int]],
    type: typing.Union[typing.Set[str], typing.Set[int]],
    pixels: "Buffer",
):
    """Specify a two-dimensional texture image

    :param target: Specifies the target texture.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param level: Specifies the level-of-detail number. Level 0 is the base image level. Level n is the nth mipmap reduction image.
    :type level: int
    :param internalformat: Specifies the number of color components in the texture.
    :type internalformat: int
    :param width: Specifies the width of the texture image. Must be 2n+2(border) for some integer n. All implementations support texture images that are at least 64 texels wide.
    :type width: int
    :param height: Specifies the height of the texture image. Must be 2m+2(border) for some integer m. All implementations support texture images that are at least 64 texels high.
    :type height: int
    :param border: Specifies the width of the border. Must be either 0 or 1.
    :type border: int
    :param format: Specifies the format of the pixel data.
    :type format: typing.Union[typing.Set[str], typing.Set[int]]
    :param type: Specifies the data type of the pixel data.
    :type type: typing.Union[typing.Set[str], typing.Set[int]]
    :param pixels: Specifies a pointer to the image data in memory.
    :type pixels: 'Buffer'
    """

    ...

def glTexImage2DMultisample(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: bool
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: bool
    :rtype: typing.Any
    """

    ...

def glTexImage3D(
    p0: int,
    p1: int,
    p2: int,
    p3: int,
    p4: int,
    p5: int,
    p6: int,
    p7: int,
    p8: int,
    p9: typing.Any,
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :type p7: int
    :type p8: int
    :type p9: typing.Any
    :rtype: typing.Any
    """

    ...

def glTexImage3DMultisample(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: int, p6: bool
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: bool
    :rtype: typing.Any
    """

    ...

def glTexParameter(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    param: typing.Any,
):
    """B{glTexParameterf, glTexParameteri, glTexParameterfv, glTexParameteriv} Set texture parameters

    :param target: Specifies the target texture.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies the symbolic name of a single-valued texture parameter.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param param: Specifies the value of pname. If function prototype ends in 'v' specifies a pointer to an array where the value or values of pname are stored.
    :type param: typing.Any
    """

    ...

def glTexParameterf(p0: int, p1: int, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glTexParameterfv(p0: int, p1: int, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glTexParameteri(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glTexParameteriv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glTexSubImage1D(
    p0: int, p1: int, p2: int, p3: int, p4: int, p5: int, p6: typing.Any
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: typing.Any
    :rtype: typing.Any
    """

    ...

def glTexSubImage2D(
    p0: int,
    p1: int,
    p2: int,
    p3: int,
    p4: int,
    p5: int,
    p6: int,
    p7: int,
    p8: typing.Any,
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :type p7: int
    :type p8: typing.Any
    :rtype: typing.Any
    """

    ...

def glTexSubImage3D(
    p0: int,
    p1: int,
    p2: int,
    p3: int,
    p4: int,
    p5: int,
    p6: int,
    p7: int,
    p8: int,
    p9: int,
    p10: typing.Any,
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :type p5: int
    :type p6: int
    :type p7: int
    :type p8: int
    :type p9: int
    :type p10: typing.Any
    :rtype: typing.Any
    """

    ...

def glTranslate(x: typing.Any, y: typing.Any, z: typing.Any):
    """B{glTranslatef, glTranslated} Multiply the current matrix by a translation matrix

    :param x: Specify the x, y, and z coordinates of a translation vector.
    :type x: typing.Any
    :param y: Specify the x, y, and z coordinates of a translation vector.
    :type y: typing.Any
    :param z: Specify the x, y, and z coordinates of a translation vector.
    :type z: typing.Any
    """

    ...

def glUniform1f(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glUniform1fv(p0: int, p1: int, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glUniform1i(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glUniform1iv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glUniform2f(p0: int, p1: float, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glUniform2fv(p0: int, p1: int, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glUniform2i(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glUniform2iv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glUniform3f(p0: int, p1: float, p2: float, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :type p2: float
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glUniform3fv(p0: int, p1: int, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glUniform3i(p0: int, p1: int, p2: int, p3: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :rtype: typing.Any
    """

    ...

def glUniform3iv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glUniform4f(p0: int, p1: float, p2: float, p3: float, p4: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :type p2: float
    :type p3: float
    :type p4: float
    :rtype: typing.Any
    """

    ...

def glUniform4fv(p0: int, p1: int, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glUniform4i(p0: int, p1: int, p2: int, p3: int, p4: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :rtype: typing.Any
    """

    ...

def glUniform4iv(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glUniformBlockBinding(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glUniformMatrix2fv(p0: int, p1: int, p2: bool, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: bool
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glUniformMatrix2x3fv(p0: int, p1: int, p2: bool, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: bool
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glUniformMatrix2x4fv(p0: int, p1: int, p2: bool, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: bool
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glUniformMatrix3fv(p0: int, p1: int, p2: bool, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: bool
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glUniformMatrix3x2fv(p0: int, p1: int, p2: bool, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: bool
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glUniformMatrix3x4fv(p0: int, p1: int, p2: bool, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: bool
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glUniformMatrix4fv(p0: int, p1: int, p2: bool, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: bool
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glUniformMatrix4x2fv(p0: int, p1: int, p2: bool, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: bool
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glUniformMatrix4x3fv(p0: int, p1: int, p2: bool, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: bool
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glUnmapBuffer(p0: int) -> bool:
    """

    :type p0: int
    :rtype: bool
    """

    ...

def glUseProgram(program: int):
    """Installs a program object as part of current rendering state

    :param program: Specifies the handle of the program object whose executables are to be used as part of current rendering state.
    :type program: int
    """

    ...

def glValidateProgram(program: int):
    """Validates a program object

    :param program: Specifies the handle of the program object to be validated.
    :type program: int
    """

    ...

def glVertexAttrib1d(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib1dv(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib1f(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib1fv(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib1s(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib1sv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib2d(p0: int, p1: float, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib2dv(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib2f(p0: int, p1: float, p2: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :type p2: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib2fv(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib2s(p0: int, p1: int, p2: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib2sv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib3d(p0: int, p1: float, p2: float, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :type p2: float
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib3dv(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib3f(p0: int, p1: float, p2: float, p3: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :type p2: float
    :type p3: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib3fv(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib3s(p0: int, p1: int, p2: int, p3: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib3sv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4Nbv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4Niv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4Nsv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4Nub(p0: int, p1: int, p2: int, p3: int, p4: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4Nubv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4Nuiv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4Nusv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4bv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4d(p0: int, p1: float, p2: float, p3: float, p4: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :type p2: float
    :type p3: float
    :type p4: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4dv(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4f(p0: int, p1: float, p2: float, p3: float, p4: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :type p2: float
    :type p3: float
    :type p4: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4fv(p0: int, p1: float) -> typing.Any:
    """

    :type p0: int
    :type p1: float
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4iv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4s(p0: int, p1: int, p2: int, p3: int, p4: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4sv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4ubv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4uiv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttrib4usv(p0: int, p1: int) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :rtype: typing.Any
    """

    ...

def glVertexAttribIPointer(
    p0: int, p1: int, p2: int, p3: int, p4: typing.Any
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: int
    :type p4: typing.Any
    :rtype: typing.Any
    """

    ...

def glVertexAttribPointer(
    p0: int, p1: int, p2: int, p3: bool, p4: int, p5: typing.Any
) -> typing.Any:
    """

    :type p0: int
    :type p1: int
    :type p2: int
    :type p3: bool
    :type p4: int
    :type p5: typing.Any
    :rtype: typing.Any
    """

    ...

def glViewport(x: int, y: int, width: int, height: int):
    """Set the viewport

    :param x: Specify the lower left corner of the viewport rectangle, in pixels. The initial value is (0,0).
    :type x: int
    :param y: Specify the lower left corner of the viewport rectangle, in pixels. The initial value is (0,0).
    :type y: int
    :param width: Specify the width and height of the viewport. When a GL context is first attached to a window, width and height are set to the dimensions of that window.
    :type width: int
    :param height: Specify the width and height of the viewport. When a GL context is first attached to a window, width and height are set to the dimensions of that window.
    :type height: int
    """

    ...

GL_ACTIVE_ATTRIBUTES: float

GL_ACTIVE_ATTRIBUTE_MAX_LENGTH: float

GL_ACTIVE_TEXTURE: float

GL_ACTIVE_UNIFORMS: float

GL_ACTIVE_UNIFORM_BLOCKS: float

GL_ACTIVE_UNIFORM_BLOCK_MAX_NAME_LENGTH: float

GL_ACTIVE_UNIFORM_MAX_LENGTH: float

GL_ALIASED_LINE_WIDTH_RANGE: float

GL_ALPHA: float

GL_ALREADY_SIGNALED: float

GL_ALWAYS: float

GL_AND: float

GL_AND_INVERTED: float

GL_AND_REVERSE: float

GL_ANY_SAMPLES_PASSED: float

GL_ARRAY_BUFFER: float

GL_ARRAY_BUFFER_BINDING: float

GL_ATTACHED_SHADERS: float

GL_BACK: float

GL_BACK_LEFT: float

GL_BACK_RIGHT: float

GL_BGR: float

GL_BGRA: float

GL_BGRA_INTEGER: float

GL_BGR_INTEGER: float

GL_BLEND: float

GL_BLEND_DST: float

GL_BLEND_DST_ALPHA: float

GL_BLEND_DST_RGB: float

GL_BLEND_EQUATION_ALPHA: float

GL_BLEND_EQUATION_RGB: float

GL_BLEND_SRC: float

GL_BLEND_SRC_ALPHA: float

GL_BLEND_SRC_RGB: float

GL_BLUE: float

GL_BLUE_INTEGER: float

GL_BOOL: float

GL_BOOL_VEC2: float

GL_BOOL_VEC3: float

GL_BOOL_VEC4: float

GL_BUFFER_ACCESS: float

GL_BUFFER_ACCESS_FLAGS: float

GL_BUFFER_MAPPED: float

GL_BUFFER_MAP_LENGTH: float

GL_BUFFER_MAP_OFFSET: float

GL_BUFFER_MAP_POINTER: float

GL_BUFFER_SIZE: float

GL_BUFFER_USAGE: float

GL_BYTE: float

GL_CCW: float

GL_CLAMP_READ_COLOR: float

GL_CLAMP_TO_BORDER: float

GL_CLAMP_TO_EDGE: float

GL_CLEAR: float

GL_CLIP_DISTANCE0: float

GL_CLIP_DISTANCE1: float

GL_CLIP_DISTANCE2: float

GL_CLIP_DISTANCE3: float

GL_CLIP_DISTANCE4: float

GL_CLIP_DISTANCE5: float

GL_CLIP_DISTANCE6: float

GL_CLIP_DISTANCE7: float

GL_COLOR: float

GL_COLOR_ATTACHMENT0: float

GL_COLOR_ATTACHMENT1: float

GL_COLOR_ATTACHMENT10: float

GL_COLOR_ATTACHMENT11: float

GL_COLOR_ATTACHMENT12: float

GL_COLOR_ATTACHMENT13: float

GL_COLOR_ATTACHMENT14: float

GL_COLOR_ATTACHMENT15: float

GL_COLOR_ATTACHMENT16: float

GL_COLOR_ATTACHMENT17: float

GL_COLOR_ATTACHMENT18: float

GL_COLOR_ATTACHMENT19: float

GL_COLOR_ATTACHMENT2: float

GL_COLOR_ATTACHMENT20: float

GL_COLOR_ATTACHMENT21: float

GL_COLOR_ATTACHMENT22: float

GL_COLOR_ATTACHMENT23: float

GL_COLOR_ATTACHMENT24: float

GL_COLOR_ATTACHMENT25: float

GL_COLOR_ATTACHMENT26: float

GL_COLOR_ATTACHMENT27: float

GL_COLOR_ATTACHMENT28: float

GL_COLOR_ATTACHMENT29: float

GL_COLOR_ATTACHMENT3: float

GL_COLOR_ATTACHMENT30: float

GL_COLOR_ATTACHMENT31: float

GL_COLOR_ATTACHMENT4: float

GL_COLOR_ATTACHMENT5: float

GL_COLOR_ATTACHMENT6: float

GL_COLOR_ATTACHMENT7: float

GL_COLOR_ATTACHMENT8: float

GL_COLOR_ATTACHMENT9: float

GL_COLOR_BUFFER_BIT: float

GL_COLOR_CLEAR_VALUE: float

GL_COLOR_LOGIC_OP: float

GL_COLOR_WRITEMASK: float

GL_COMPARE_REF_TO_TEXTURE: float

GL_COMPILE_STATUS: float

GL_COMPRESSED_RED: float

GL_COMPRESSED_RED_RGTC1: float

GL_COMPRESSED_RG: float

GL_COMPRESSED_RGB: float

GL_COMPRESSED_RGBA: float

GL_COMPRESSED_RG_RGTC2: float

GL_COMPRESSED_SIGNED_RED_RGTC1: float

GL_COMPRESSED_SIGNED_RG_RGTC2: float

GL_COMPRESSED_SRGB: float

GL_COMPRESSED_SRGB_ALPHA: float

GL_COMPRESSED_TEXTURE_FORMATS: float

GL_CONDITION_SATISFIED: float

GL_CONSTANT_ALPHA: float

GL_CONSTANT_COLOR: float

GL_CONTEXT_COMPATIBILITY_PROFILE_BIT: float

GL_CONTEXT_CORE_PROFILE_BIT: float

GL_CONTEXT_FLAGS: float

GL_CONTEXT_FLAG_FORWARD_COMPATIBLE_BIT: float

GL_CONTEXT_PROFILE_MASK: float

GL_COPY: float

GL_COPY_INVERTED: float

GL_COPY_READ_BUFFER: float

GL_COPY_WRITE_BUFFER: float

GL_CULL_FACE: float

GL_CULL_FACE_MODE: float

GL_CURRENT_PROGRAM: float

GL_CURRENT_QUERY: float

GL_CURRENT_VERTEX_ATTRIB: float

GL_CW: float

GL_DECR: float

GL_DECR_WRAP: float

GL_DELETE_STATUS: float

GL_DEPTH: float

GL_DEPTH24_STENCIL8: float

GL_DEPTH32F_STENCIL8: float

GL_DEPTH_ATTACHMENT: float

GL_DEPTH_BUFFER_BIT: float

GL_DEPTH_CLAMP: float

GL_DEPTH_CLEAR_VALUE: float

GL_DEPTH_COMPONENT: float

GL_DEPTH_COMPONENT16: float

GL_DEPTH_COMPONENT24: float

GL_DEPTH_COMPONENT32: float

GL_DEPTH_COMPONENT32F: float

GL_DEPTH_FUNC: float

GL_DEPTH_RANGE: float

GL_DEPTH_STENCIL: float

GL_DEPTH_STENCIL_ATTACHMENT: float

GL_DEPTH_TEST: float

GL_DEPTH_WRITEMASK: float

GL_DITHER: float

GL_DONT_CARE: float

GL_DOUBLE: float

GL_DOUBLEBUFFER: float

GL_DRAW_BUFFER: float

GL_DRAW_BUFFER0: float

GL_DRAW_BUFFER1: float

GL_DRAW_BUFFER10: float

GL_DRAW_BUFFER11: float

GL_DRAW_BUFFER12: float

GL_DRAW_BUFFER13: float

GL_DRAW_BUFFER14: float

GL_DRAW_BUFFER15: float

GL_DRAW_BUFFER2: float

GL_DRAW_BUFFER3: float

GL_DRAW_BUFFER4: float

GL_DRAW_BUFFER5: float

GL_DRAW_BUFFER6: float

GL_DRAW_BUFFER7: float

GL_DRAW_BUFFER8: float

GL_DRAW_BUFFER9: float

GL_DRAW_FRAMEBUFFER: float

GL_DRAW_FRAMEBUFFER_BINDING: float

GL_DST_ALPHA: float

GL_DST_COLOR: float

GL_DYNAMIC_COPY: float

GL_DYNAMIC_DRAW: float

GL_DYNAMIC_READ: float

GL_ELEMENT_ARRAY_BUFFER: float

GL_ELEMENT_ARRAY_BUFFER_BINDING: float

GL_EQUAL: float

GL_EQUIV: float

GL_EXTENSIONS: float

GL_FALSE: float

GL_FASTEST: float

GL_FILL: float

GL_FIRST_VERTEX_CONVENTION: float

GL_FIXED_ONLY: float

GL_FLOAT: float

GL_FLOAT_32_UNSIGNED_INT_24_8_REV: float

GL_FLOAT_MAT2: float

GL_FLOAT_MAT2x3: float

GL_FLOAT_MAT2x4: float

GL_FLOAT_MAT3: float

GL_FLOAT_MAT3x2: float

GL_FLOAT_MAT3x4: float

GL_FLOAT_MAT4: float

GL_FLOAT_MAT4x2: float

GL_FLOAT_MAT4x3: float

GL_FLOAT_VEC2: float

GL_FLOAT_VEC3: float

GL_FLOAT_VEC4: float

GL_FRAGMENT_SHADER: float

GL_FRAGMENT_SHADER_DERIVATIVE_HINT: float

GL_FRAMEBUFFER: float

GL_FRAMEBUFFER_ATTACHMENT_ALPHA_SIZE: float

GL_FRAMEBUFFER_ATTACHMENT_BLUE_SIZE: float

GL_FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING: float

GL_FRAMEBUFFER_ATTACHMENT_COMPONENT_TYPE: float

GL_FRAMEBUFFER_ATTACHMENT_DEPTH_SIZE: float

GL_FRAMEBUFFER_ATTACHMENT_GREEN_SIZE: float

GL_FRAMEBUFFER_ATTACHMENT_LAYERED: float

GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME: float

GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE: float

GL_FRAMEBUFFER_ATTACHMENT_RED_SIZE: float

GL_FRAMEBUFFER_ATTACHMENT_STENCIL_SIZE: float

GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE: float

GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LAYER: float

GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL: float

GL_FRAMEBUFFER_BINDING: float

GL_FRAMEBUFFER_COMPLETE: float

GL_FRAMEBUFFER_DEFAULT: float

GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT: float

GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER: float

GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS: float

GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT: float

GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE: float

GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER: float

GL_FRAMEBUFFER_SRGB: float

GL_FRAMEBUFFER_UNDEFINED: float

GL_FRAMEBUFFER_UNSUPPORTED: float

GL_FRONT: float

GL_FRONT_AND_BACK: float

GL_FRONT_FACE: float

GL_FRONT_LEFT: float

GL_FRONT_RIGHT: float

GL_FUNC_ADD: float

GL_FUNC_REVERSE_SUBTRACT: float

GL_FUNC_SUBTRACT: float

GL_GEOMETRY_INPUT_TYPE: float

GL_GEOMETRY_OUTPUT_TYPE: float

GL_GEOMETRY_SHADER: float

GL_GEOMETRY_VERTICES_OUT: float

GL_GEQUAL: float

GL_GREATER: float

GL_GREEN: float

GL_GREEN_INTEGER: float

GL_HALF_FLOAT: float

GL_INCR: float

GL_INCR_WRAP: float

GL_INDEX: float

GL_INFO_LOG_LENGTH: float

GL_INT: float

GL_INTERLEAVED_ATTRIBS: float

GL_INT_2_10_10_10_REV: float

GL_INT_SAMPLER_1D: float

GL_INT_SAMPLER_1D_ARRAY: float

GL_INT_SAMPLER_2D: float

GL_INT_SAMPLER_2D_ARRAY: float

GL_INT_SAMPLER_2D_MULTISAMPLE: float

GL_INT_SAMPLER_2D_MULTISAMPLE_ARRAY: float

GL_INT_SAMPLER_2D_RECT: float

GL_INT_SAMPLER_3D: float

GL_INT_SAMPLER_BUFFER: float

GL_INT_SAMPLER_CUBE: float

GL_INT_VEC2: float

GL_INT_VEC3: float

GL_INT_VEC4: float

GL_INVALID_ENUM: float

GL_INVALID_FRAMEBUFFER_OPERATION: float

GL_INVALID_INDEX: float

GL_INVALID_OPERATION: float

GL_INVALID_VALUE: float

GL_INVERT: float

GL_KEEP: float

GL_LAST_VERTEX_CONVENTION: float

GL_LEFT: float

GL_LEQUAL: float

GL_LESS: float

GL_LINE: float

GL_LINEAR: float

GL_LINEAR_MIPMAP_LINEAR: float

GL_LINEAR_MIPMAP_NEAREST: float

GL_LINES: float

GL_LINES_ADJACENCY: float

GL_LINE_LOOP: float

GL_LINE_SMOOTH: float

GL_LINE_SMOOTH_HINT: float

GL_LINE_STRIP: float

GL_LINE_STRIP_ADJACENCY: float

GL_LINE_WIDTH: float

GL_LINE_WIDTH_GRANULARITY: float

GL_LINE_WIDTH_RANGE: float

GL_LINK_STATUS: float

GL_LOGIC_OP_MODE: float

GL_LOWER_LEFT: float

GL_MAJOR_VERSION: float

GL_MAP_FLUSH_EXPLICIT_BIT: float

GL_MAP_INVALIDATE_BUFFER_BIT: float

GL_MAP_INVALIDATE_RANGE_BIT: float

GL_MAP_READ_BIT: float

GL_MAP_UNSYNCHRONIZED_BIT: float

GL_MAP_WRITE_BIT: float

GL_MAX: float

GL_MAX_3D_TEXTURE_SIZE: float

GL_MAX_ARRAY_TEXTURE_LAYERS: float

GL_MAX_CLIP_DISTANCES: float

GL_MAX_COLOR_ATTACHMENTS: float

GL_MAX_COLOR_TEXTURE_SAMPLES: float

GL_MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS: float

GL_MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS: float

GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS: float

GL_MAX_COMBINED_UNIFORM_BLOCKS: float

GL_MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS: float

GL_MAX_CUBE_MAP_TEXTURE_SIZE: float

GL_MAX_DEPTH_TEXTURE_SAMPLES: float

GL_MAX_DRAW_BUFFERS: float

GL_MAX_DUAL_SOURCE_DRAW_BUFFERS: float

GL_MAX_ELEMENTS_INDICES: float

GL_MAX_ELEMENTS_VERTICES: float

GL_MAX_FRAGMENT_INPUT_COMPONENTS: float

GL_MAX_FRAGMENT_UNIFORM_BLOCKS: float

GL_MAX_FRAGMENT_UNIFORM_COMPONENTS: float

GL_MAX_GEOMETRY_INPUT_COMPONENTS: float

GL_MAX_GEOMETRY_OUTPUT_COMPONENTS: float

GL_MAX_GEOMETRY_OUTPUT_VERTICES: float

GL_MAX_GEOMETRY_TEXTURE_IMAGE_UNITS: float

GL_MAX_GEOMETRY_TOTAL_OUTPUT_COMPONENTS: float

GL_MAX_GEOMETRY_UNIFORM_BLOCKS: float

GL_MAX_GEOMETRY_UNIFORM_COMPONENTS: float

GL_MAX_INTEGER_SAMPLES: float

GL_MAX_PROGRAM_TEXEL_OFFSET: float

GL_MAX_RECTANGLE_TEXTURE_SIZE: float

GL_MAX_RENDERBUFFER_SIZE: float

GL_MAX_SAMPLES: float

GL_MAX_SAMPLE_MASK_WORDS: float

GL_MAX_SERVER_WAIT_TIMEOUT: float

GL_MAX_TEXTURE_BUFFER_SIZE: float

GL_MAX_TEXTURE_IMAGE_UNITS: float

GL_MAX_TEXTURE_LOD_BIAS: float

GL_MAX_TEXTURE_SIZE: float

GL_MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS: float

GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS: float

GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS: float

GL_MAX_UNIFORM_BLOCK_SIZE: float

GL_MAX_UNIFORM_BUFFER_BINDINGS: float

GL_MAX_VARYING_COMPONENTS: float

GL_MAX_VARYING_FLOATS: float

GL_MAX_VERTEX_ATTRIBS: float

GL_MAX_VERTEX_OUTPUT_COMPONENTS: float

GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS: float

GL_MAX_VERTEX_UNIFORM_BLOCKS: float

GL_MAX_VERTEX_UNIFORM_COMPONENTS: float

GL_MAX_VIEWPORT_DIMS: float

GL_MIN: float

GL_MINOR_VERSION: float

GL_MIN_PROGRAM_TEXEL_OFFSET: float

GL_MIRRORED_REPEAT: float

GL_MULTISAMPLE: float

GL_NAND: float

GL_NEAREST: float

GL_NEAREST_MIPMAP_LINEAR: float

GL_NEAREST_MIPMAP_NEAREST: float

GL_NEVER: float

GL_NICEST: float

GL_NONE: float

GL_NOOP: float

GL_NOR: float

GL_NOTEQUAL: float

GL_NO_ERROR: float

GL_NUM_COMPRESSED_TEXTURE_FORMATS: float

GL_NUM_EXTENSIONS: float

GL_OBJECT_TYPE: float

GL_ONE: float

GL_ONE_MINUS_CONSTANT_ALPHA: float

GL_ONE_MINUS_CONSTANT_COLOR: float

GL_ONE_MINUS_DST_ALPHA: float

GL_ONE_MINUS_DST_COLOR: float

GL_ONE_MINUS_SRC1_ALPHA: float

GL_ONE_MINUS_SRC1_COLOR: float

GL_ONE_MINUS_SRC_ALPHA: float

GL_ONE_MINUS_SRC_COLOR: float

GL_OR: float

GL_OR_INVERTED: float

GL_OR_REVERSE: float

GL_OUT_OF_MEMORY: float

GL_PACK_ALIGNMENT: float

GL_PACK_IMAGE_HEIGHT: float

GL_PACK_LSB_FIRST: float

GL_PACK_ROW_LENGTH: float

GL_PACK_SKIP_IMAGES: float

GL_PACK_SKIP_PIXELS: float

GL_PACK_SKIP_ROWS: float

GL_PACK_SWAP_BYTES: float

GL_PIXEL_PACK_BUFFER: float

GL_PIXEL_PACK_BUFFER_BINDING: float

GL_PIXEL_UNPACK_BUFFER: float

GL_PIXEL_UNPACK_BUFFER_BINDING: float

GL_POINT: float

GL_POINTS: float

GL_POINT_FADE_THRESHOLD_SIZE: float

GL_POINT_SIZE: float

GL_POINT_SPRITE_COORD_ORIGIN: float

GL_POLYGON_MODE: float

GL_POLYGON_OFFSET_FACTOR: float

GL_POLYGON_OFFSET_FILL: float

GL_POLYGON_OFFSET_LINE: float

GL_POLYGON_OFFSET_POINT: float

GL_POLYGON_OFFSET_UNITS: float

GL_POLYGON_SMOOTH: float

GL_POLYGON_SMOOTH_HINT: float

GL_PRIMITIVES_GENERATED: float

GL_PRIMITIVE_RESTART: float

GL_PRIMITIVE_RESTART_INDEX: float

GL_PROGRAM_POINT_SIZE: float

GL_PROVOKING_VERTEX: float

GL_PROXY_TEXTURE_1D: float

GL_PROXY_TEXTURE_1D_ARRAY: float

GL_PROXY_TEXTURE_2D: float

GL_PROXY_TEXTURE_2D_ARRAY: float

GL_PROXY_TEXTURE_2D_MULTISAMPLE: float

GL_PROXY_TEXTURE_2D_MULTISAMPLE_ARRAY: float

GL_PROXY_TEXTURE_3D: float

GL_PROXY_TEXTURE_CUBE_MAP: float

GL_PROXY_TEXTURE_RECTANGLE: float

GL_QUADS_FOLLOW_PROVOKING_VERTEX_CONVENTION: float

GL_QUERY_BY_REGION_NO_WAIT: float

GL_QUERY_BY_REGION_WAIT: float

GL_QUERY_COUNTER_BITS: float

GL_QUERY_NO_WAIT: float

GL_QUERY_RESULT: float

GL_QUERY_RESULT_AVAILABLE: float

GL_QUERY_WAIT: float

GL_R11F_G11F_B10F: float

GL_R16: float

GL_R16F: float

GL_R16I: float

GL_R16UI: float

GL_R16_SNORM: float

GL_R32F: float

GL_R32I: float

GL_R32UI: float

GL_R3_G3_B2: float

GL_R8: float

GL_R8I: float

GL_R8UI: float

GL_R8_SNORM: float

GL_RASTERIZER_DISCARD: float

GL_READ_BUFFER: float

GL_READ_FRAMEBUFFER: float

GL_READ_FRAMEBUFFER_BINDING: float

GL_READ_ONLY: float

GL_READ_WRITE: float

GL_RED: float

GL_RED_INTEGER: float

GL_RENDERBUFFER: float

GL_RENDERBUFFER_ALPHA_SIZE: float

GL_RENDERBUFFER_BINDING: float

GL_RENDERBUFFER_BLUE_SIZE: float

GL_RENDERBUFFER_DEPTH_SIZE: float

GL_RENDERBUFFER_GREEN_SIZE: float

GL_RENDERBUFFER_HEIGHT: float

GL_RENDERBUFFER_INTERNAL_FORMAT: float

GL_RENDERBUFFER_RED_SIZE: float

GL_RENDERBUFFER_SAMPLES: float

GL_RENDERBUFFER_STENCIL_SIZE: float

GL_RENDERBUFFER_WIDTH: float

GL_RENDERER: float

GL_REPEAT: float

GL_REPLACE: float

GL_RG: float

GL_RG16: float

GL_RG16F: float

GL_RG16I: float

GL_RG16UI: float

GL_RG16_SNORM: float

GL_RG32F: float

GL_RG32I: float

GL_RG32UI: float

GL_RG8: float

GL_RG8I: float

GL_RG8UI: float

GL_RG8_SNORM: float

GL_RGB: float

GL_RGB10: float

GL_RGB10_A2: float

GL_RGB10_A2UI: float

GL_RGB12: float

GL_RGB16: float

GL_RGB16F: float

GL_RGB16I: float

GL_RGB16UI: float

GL_RGB16_SNORM: float

GL_RGB32F: float

GL_RGB32I: float

GL_RGB32UI: float

GL_RGB4: float

GL_RGB5: float

GL_RGB5_A1: float

GL_RGB8: float

GL_RGB8I: float

GL_RGB8UI: float

GL_RGB8_SNORM: float

GL_RGB9_E5: float

GL_RGBA: float

GL_RGBA12: float

GL_RGBA16: float

GL_RGBA16F: float

GL_RGBA16I: float

GL_RGBA16UI: float

GL_RGBA16_SNORM: float

GL_RGBA2: float

GL_RGBA32F: float

GL_RGBA32I: float

GL_RGBA32UI: float

GL_RGBA4: float

GL_RGBA8: float

GL_RGBA8I: float

GL_RGBA8UI: float

GL_RGBA8_SNORM: float

GL_RGBA_INTEGER: float

GL_RGB_INTEGER: float

GL_RG_INTEGER: float

GL_RIGHT: float

GL_SAMPLER_1D: float

GL_SAMPLER_1D_ARRAY: float

GL_SAMPLER_1D_ARRAY_SHADOW: float

GL_SAMPLER_1D_SHADOW: float

GL_SAMPLER_2D: float

GL_SAMPLER_2D_ARRAY: float

GL_SAMPLER_2D_ARRAY_SHADOW: float

GL_SAMPLER_2D_MULTISAMPLE: float

GL_SAMPLER_2D_MULTISAMPLE_ARRAY: float

GL_SAMPLER_2D_RECT: float

GL_SAMPLER_2D_RECT_SHADOW: float

GL_SAMPLER_2D_SHADOW: float

GL_SAMPLER_3D: float

GL_SAMPLER_BINDING: float

GL_SAMPLER_BUFFER: float

GL_SAMPLER_CUBE: float

GL_SAMPLER_CUBE_SHADOW: float

GL_SAMPLES: float

GL_SAMPLES_PASSED: float

GL_SAMPLE_ALPHA_TO_COVERAGE: float

GL_SAMPLE_ALPHA_TO_ONE: float

GL_SAMPLE_BUFFERS: float

GL_SAMPLE_COVERAGE: float

GL_SAMPLE_COVERAGE_INVERT: float

GL_SAMPLE_COVERAGE_VALUE: float

GL_SAMPLE_MASK: float

GL_SAMPLE_MASK_VALUE: float

GL_SAMPLE_POSITION: float

GL_SCISSOR_BOX: float

GL_SCISSOR_TEST: float

GL_SEPARATE_ATTRIBS: float

GL_SET: float

GL_SHADER_SOURCE_LENGTH: float

GL_SHADER_TYPE: float

GL_SHADING_LANGUAGE_VERSION: float

GL_SHORT: float

GL_SIGNALED: float

GL_SIGNED_NORMALIZED: float

GL_SMOOTH_LINE_WIDTH_GRANULARITY: float

GL_SMOOTH_LINE_WIDTH_RANGE: float

GL_SMOOTH_POINT_SIZE_GRANULARITY: float

GL_SMOOTH_POINT_SIZE_RANGE: float

GL_SRC1_COLOR: float

GL_SRC_ALPHA: float

GL_SRC_ALPHA_SATURATE: float

GL_SRC_COLOR: float

GL_SRGB: float

GL_SRGB8: float

GL_SRGB8_ALPHA8: float

GL_SRGB_ALPHA: float

GL_STATIC_COPY: float

GL_STATIC_DRAW: float

GL_STATIC_READ: float

GL_STENCIL: float

GL_STENCIL_ATTACHMENT: float

GL_STENCIL_BACK_FAIL: float

GL_STENCIL_BACK_FUNC: float

GL_STENCIL_BACK_PASS_DEPTH_FAIL: float

GL_STENCIL_BACK_PASS_DEPTH_PASS: float

GL_STENCIL_BACK_REF: float

GL_STENCIL_BACK_VALUE_MASK: float

GL_STENCIL_BACK_WRITEMASK: float

GL_STENCIL_BUFFER_BIT: float

GL_STENCIL_CLEAR_VALUE: float

GL_STENCIL_FAIL: float

GL_STENCIL_FUNC: float

GL_STENCIL_INDEX: float

GL_STENCIL_INDEX1: float

GL_STENCIL_INDEX16: float

GL_STENCIL_INDEX4: float

GL_STENCIL_INDEX8: float

GL_STENCIL_PASS_DEPTH_FAIL: float

GL_STENCIL_PASS_DEPTH_PASS: float

GL_STENCIL_REF: float

GL_STENCIL_TEST: float

GL_STENCIL_VALUE_MASK: float

GL_STENCIL_WRITEMASK: float

GL_STEREO: float

GL_STREAM_COPY: float

GL_STREAM_DRAW: float

GL_STREAM_READ: float

GL_SUBPIXEL_BITS: float

GL_SYNC_CONDITION: float

GL_SYNC_FENCE: float

GL_SYNC_FLAGS: float

GL_SYNC_FLUSH_COMMANDS_BIT: float

GL_SYNC_GPU_COMMANDS_COMPLETE: float

GL_SYNC_STATUS: float

GL_TEXTURE: float

GL_TEXTURE0: float

GL_TEXTURE1: float

GL_TEXTURE10: float

GL_TEXTURE11: float

GL_TEXTURE12: float

GL_TEXTURE13: float

GL_TEXTURE14: float

GL_TEXTURE15: float

GL_TEXTURE16: float

GL_TEXTURE17: float

GL_TEXTURE18: float

GL_TEXTURE19: float

GL_TEXTURE2: float

GL_TEXTURE20: float

GL_TEXTURE21: float

GL_TEXTURE22: float

GL_TEXTURE23: float

GL_TEXTURE24: float

GL_TEXTURE25: float

GL_TEXTURE26: float

GL_TEXTURE27: float

GL_TEXTURE28: float

GL_TEXTURE29: float

GL_TEXTURE3: float

GL_TEXTURE30: float

GL_TEXTURE31: float

GL_TEXTURE4: float

GL_TEXTURE5: float

GL_TEXTURE6: float

GL_TEXTURE7: float

GL_TEXTURE8: float

GL_TEXTURE9: float

GL_TEXTURE_1D: float

GL_TEXTURE_1D_ARRAY: float

GL_TEXTURE_2D: float

GL_TEXTURE_2D_ARRAY: float

GL_TEXTURE_2D_MULTISAMPLE: float

GL_TEXTURE_2D_MULTISAMPLE_ARRAY: float

GL_TEXTURE_3D: float

GL_TEXTURE_ALPHA_SIZE: float

GL_TEXTURE_ALPHA_TYPE: float

GL_TEXTURE_BASE_LEVEL: float

GL_TEXTURE_BINDING_1D: float

GL_TEXTURE_BINDING_1D_ARRAY: float

GL_TEXTURE_BINDING_2D: float

GL_TEXTURE_BINDING_2D_ARRAY: float

GL_TEXTURE_BINDING_2D_MULTISAMPLE: float

GL_TEXTURE_BINDING_2D_MULTISAMPLE_ARRAY: float

GL_TEXTURE_BINDING_3D: float

GL_TEXTURE_BINDING_BUFFER: float

GL_TEXTURE_BINDING_CUBE_MAP: float

GL_TEXTURE_BINDING_RECTANGLE: float

GL_TEXTURE_BLUE_SIZE: float

GL_TEXTURE_BLUE_TYPE: float

GL_TEXTURE_BORDER_COLOR: float

GL_TEXTURE_BUFFER: float

GL_TEXTURE_BUFFER_DATA_STORE_BINDING: float

GL_TEXTURE_COMPARE_FUNC: float

GL_TEXTURE_COMPARE_MODE: float

GL_TEXTURE_COMPRESSED: float

GL_TEXTURE_COMPRESSED_IMAGE_SIZE: float

GL_TEXTURE_COMPRESSION_HINT: float

GL_TEXTURE_CUBE_MAP: float

GL_TEXTURE_CUBE_MAP_NEGATIVE_X: float

GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: float

GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: float

GL_TEXTURE_CUBE_MAP_POSITIVE_X: float

GL_TEXTURE_CUBE_MAP_POSITIVE_Y: float

GL_TEXTURE_CUBE_MAP_POSITIVE_Z: float

GL_TEXTURE_CUBE_MAP_SEAMLESS: float

GL_TEXTURE_DEPTH: float

GL_TEXTURE_DEPTH_SIZE: float

GL_TEXTURE_DEPTH_TYPE: float

GL_TEXTURE_FIXED_SAMPLE_LOCATIONS: float

GL_TEXTURE_GREEN_SIZE: float

GL_TEXTURE_GREEN_TYPE: float

GL_TEXTURE_HEIGHT: float

GL_TEXTURE_INTERNAL_FORMAT: float

GL_TEXTURE_LOD_BIAS: float

GL_TEXTURE_MAG_FILTER: float

GL_TEXTURE_MAX_LEVEL: float

GL_TEXTURE_MAX_LOD: float

GL_TEXTURE_MIN_FILTER: float

GL_TEXTURE_MIN_LOD: float

GL_TEXTURE_RECTANGLE: float

GL_TEXTURE_RED_SIZE: float

GL_TEXTURE_RED_TYPE: float

GL_TEXTURE_SAMPLES: float

GL_TEXTURE_SHARED_SIZE: float

GL_TEXTURE_STENCIL_SIZE: float

GL_TEXTURE_SWIZZLE_A: float

GL_TEXTURE_SWIZZLE_B: float

GL_TEXTURE_SWIZZLE_G: float

GL_TEXTURE_SWIZZLE_R: float

GL_TEXTURE_SWIZZLE_RGBA: float

GL_TEXTURE_WIDTH: float

GL_TEXTURE_WRAP_R: float

GL_TEXTURE_WRAP_S: float

GL_TEXTURE_WRAP_T: float

GL_TIMEOUT_EXPIRED: float

GL_TIMEOUT_IGNORED: float

GL_TIMESTAMP: float

GL_TIME_ELAPSED: float

GL_TRANSFORM_FEEDBACK_BUFFER: float

GL_TRANSFORM_FEEDBACK_BUFFER_BINDING: float

GL_TRANSFORM_FEEDBACK_BUFFER_MODE: float

GL_TRANSFORM_FEEDBACK_BUFFER_SIZE: float

GL_TRANSFORM_FEEDBACK_BUFFER_START: float

GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN: float

GL_TRANSFORM_FEEDBACK_VARYINGS: float

GL_TRANSFORM_FEEDBACK_VARYING_MAX_LENGTH: float

GL_TRIANGLES: float

GL_TRIANGLES_ADJACENCY: float

GL_TRIANGLE_FAN: float

GL_TRIANGLE_STRIP: float

GL_TRIANGLE_STRIP_ADJACENCY: float

GL_TRUE: float

GL_UNIFORM_ARRAY_STRIDE: float

GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS: float

GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES: float

GL_UNIFORM_BLOCK_BINDING: float

GL_UNIFORM_BLOCK_DATA_SIZE: float

GL_UNIFORM_BLOCK_INDEX: float

GL_UNIFORM_BLOCK_NAME_LENGTH: float

GL_UNIFORM_BLOCK_REFERENCED_BY_FRAGMENT_SHADER: float

GL_UNIFORM_BLOCK_REFERENCED_BY_GEOMETRY_SHADER: float

GL_UNIFORM_BLOCK_REFERENCED_BY_VERTEX_SHADER: float

GL_UNIFORM_BUFFER: float

GL_UNIFORM_BUFFER_BINDING: float

GL_UNIFORM_BUFFER_OFFSET_ALIGNMENT: float

GL_UNIFORM_BUFFER_SIZE: float

GL_UNIFORM_BUFFER_START: float

GL_UNIFORM_IS_ROW_MAJOR: float

GL_UNIFORM_MATRIX_STRIDE: float

GL_UNIFORM_NAME_LENGTH: float

GL_UNIFORM_OFFSET: float

GL_UNIFORM_SIZE: float

GL_UNIFORM_TYPE: float

GL_UNPACK_ALIGNMENT: float

GL_UNPACK_IMAGE_HEIGHT: float

GL_UNPACK_LSB_FIRST: float

GL_UNPACK_ROW_LENGTH: float

GL_UNPACK_SKIP_IMAGES: float

GL_UNPACK_SKIP_PIXELS: float

GL_UNPACK_SKIP_ROWS: float

GL_UNPACK_SWAP_BYTES: float

GL_UNSIGNALED: float

GL_UNSIGNED_BYTE: float

GL_UNSIGNED_BYTE_2_3_3_REV: float

GL_UNSIGNED_BYTE_3_3_2: float

GL_UNSIGNED_INT: float

GL_UNSIGNED_INT_10F_11F_11F_REV: float

GL_UNSIGNED_INT_10_10_10_2: float

GL_UNSIGNED_INT_24_8: float

GL_UNSIGNED_INT_2_10_10_10_REV: float

GL_UNSIGNED_INT_5_9_9_9_REV: float

GL_UNSIGNED_INT_8_8_8_8: float

GL_UNSIGNED_INT_8_8_8_8_REV: float

GL_UNSIGNED_INT_SAMPLER_1D: float

GL_UNSIGNED_INT_SAMPLER_1D_ARRAY: float

GL_UNSIGNED_INT_SAMPLER_2D: float

GL_UNSIGNED_INT_SAMPLER_2D_ARRAY: float

GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE: float

GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE_ARRAY: float

GL_UNSIGNED_INT_SAMPLER_2D_RECT: float

GL_UNSIGNED_INT_SAMPLER_3D: float

GL_UNSIGNED_INT_SAMPLER_BUFFER: float

GL_UNSIGNED_INT_SAMPLER_CUBE: float

GL_UNSIGNED_INT_VEC2: float

GL_UNSIGNED_INT_VEC3: float

GL_UNSIGNED_INT_VEC4: float

GL_UNSIGNED_NORMALIZED: float

GL_UNSIGNED_SHORT: float

GL_UNSIGNED_SHORT_1_5_5_5_REV: float

GL_UNSIGNED_SHORT_4_4_4_4: float

GL_UNSIGNED_SHORT_4_4_4_4_REV: float

GL_UNSIGNED_SHORT_5_5_5_1: float

GL_UNSIGNED_SHORT_5_6_5: float

GL_UNSIGNED_SHORT_5_6_5_REV: float

GL_UPPER_LEFT: float

GL_VALIDATE_STATUS: float

GL_VENDOR: float

GL_VERSION: float

GL_VERTEX_ARRAY_BINDING: float

GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING: float

GL_VERTEX_ATTRIB_ARRAY_DIVISOR: float

GL_VERTEX_ATTRIB_ARRAY_ENABLED: float

GL_VERTEX_ATTRIB_ARRAY_INTEGER: float

GL_VERTEX_ATTRIB_ARRAY_NORMALIZED: float

GL_VERTEX_ATTRIB_ARRAY_POINTER: float

GL_VERTEX_ATTRIB_ARRAY_SIZE: float

GL_VERTEX_ATTRIB_ARRAY_STRIDE: float

GL_VERTEX_ATTRIB_ARRAY_TYPE: float

GL_VERTEX_PROGRAM_POINT_SIZE: float

GL_VERTEX_SHADER: float

GL_VIEWPORT: float

GL_WAIT_FAILED: float

GL_WRITE_ONLY: float

GL_XOR: float

GL_ZERO: float
