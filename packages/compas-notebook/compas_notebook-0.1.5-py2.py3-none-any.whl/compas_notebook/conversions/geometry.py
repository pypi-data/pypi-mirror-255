import pythreejs as three
import numpy
from compas.geometry import Box
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import Point
from compas.geometry import Pointcloud
from compas.geometry import Polyline
from compas.geometry import Sphere
from compas.geometry import Torus


def line_to_threejs(line: Point) -> three.BufferGeometry:
    """Convert a COMPAS line to PyThreeJS.

    Parameters
    ----------
    line : :class:`compas.geometry.Line`
        The line to convert.

    Returns
    -------
    :class:`three.BufferGeometry`

    """
    vertices = numpy.array([line.start, line.end], dtype=numpy.float32)
    geometry = three.BufferGeometry(attributes={"position": three.BufferAttribute(vertices, normalized=False)})
    return geometry


def point_to_threejs(point: Point) -> three.SphereGeometry:
    """Convert a COMPAS point to PyThreeJS.

    Parameters
    ----------
    point : :class:`compas.geometry.Point`
        The point to convert.

    Returns
    -------
    :class:`three.BufferGeometry`

    Examples
    --------
    >>> from compas.geometry import Point
    >>> point = Point(1, 2, 3)
    >>> point_to_threejs(point)  # doctest: +ELLIPSIS
    BufferGeometry(...)

    """
    vertices = numpy.array([point], dtype=numpy.float32)
    geometry = three.BufferGeometry(attributes={"position": three.BufferAttribute(vertices, normalized=False)})
    return geometry


def pointcloud_to_threejs(pointcloud: Pointcloud) -> three.SphereGeometry:
    """Convert a COMPAS point to PyThreeJS.

    Parameters
    ----------
    pointcloud : :class:`compas.geometry.Pointcloud`
        The pointcloud to convert.

    Returns
    -------
    :class:`three.BufferGeometry`

    Examples
    --------
    >>>

    """
    vertices = numpy.array(pointcloud.points, dtype=numpy.float32)
    geometry = three.BufferGeometry(attributes={"position": three.BufferAttribute(vertices, normalized=False)})
    return geometry


def polyline_to_threejs(polyline: Polyline) -> three.BufferGeometry:
    """Convert a COMPAS polyline to PyThreeJS.

    Parameters
    ----------
    polyline : :class:`compas.geometry.Polyline`
        The polyline to convert.

    Returns
    -------
    :class:`three.BufferGeometry`

    """
    vertices = numpy.array(polyline.points, dtype=numpy.float32)
    geometry = three.BufferGeometry(attributes={"position": three.BufferAttribute(vertices, normalized=False)})
    return geometry


# =============================================================================
# Shapes
# =============================================================================


def box_to_threejs(box: Box) -> three.BoxGeometry:
    """Convert a COMPAS box to PyThreeJS.

    Parameters
    ----------
    box : :class:`compas.geometry.Box`
        The box to convert.

    Returns
    -------
    :class:`three.BoxGeometry`

    Examples
    --------
    >>> from compas.geometry import Box
    >>> box = Box.from_width_height_depth(1, 2, 3)
    >>> box_to_threejs(box)  # doctest: +ELLIPSIS
    BoxGeometry(...)

    """
    return three.BoxGeometry(width=box.width, height=box.height, depth=box.depth)


def cone_to_threejs(cone: Cone) -> three.CylinderGeometry:
    """Convert a COMPAS cone to PyThreeJS.

    Parameters
    ----------
    cone : :class:`compas.geometry.Cone`
        The cone to convert.

    Returns
    -------
    :class:`three.CylinderGeometry`

    Examples
    --------
    >>> from compas.geometry import Cone
    >>> cone = Cone(radius=1, height=2)
    >>> cone_to_threejs(cone)  # doctest: +ELLIPSIS
    CylinderGeometry(...)

    """
    return three.CylinderGeometry(radiusTop=0, radiusBottom=cone.radius, height=cone.height, radialSegments=32)


def cylinder_to_threejs(cylinder: Cylinder) -> three.CylinderGeometry:
    """Convert a COMPAS cylinder to PyThreeJS.

    Parameters
    ----------
    cylinder : :class:`compas.geometry.Cylinder`
        The cylinder to convert.

    Returns
    -------
    :class:`three.CylinderGeometry`

    Examples
    --------
    >>> from compas.geometry import Cylinder
    >>> cylinder = Cylinder(radius=1, height=2)
    >>> cylinder_to_threejs(cylinder)  # doctest: +ELLIPSIS
    CylinderGeometry(...)

    """
    return three.CylinderGeometry(radiusTop=cylinder.radius, radiusBottom=cylinder.radius, height=cylinder.height, radialSegments=32)


def sphere_to_threejs(sphere: Sphere) -> three.SphereGeometry:
    """Convert a COMPAS sphere to PyThreeJS.

    Parameters
    ----------
    sphere : :class:`compas.geometry.Sphere`
        The sphere to convert.

    Returns
    -------
    :class:`three.SphereGeometry`

    Examples
    --------
    >>> from compas.geometry import Sphere
    >>> sphere = Sphere(radius=1)
    >>> sphere_to_threejs(sphere)  # doctest: +ELLIPSIS
    SphereGeometry(...)

    """
    return three.SphereGeometry(radius=sphere.radius, widthSegments=32, heightSegments=32)


def torus_to_threejs(torus: Torus) -> three.TorusGeometry:
    """Convert a COMPAS torus to a PyThreeJS torus geometry.

    Parameters
    ----------
    torus : :class:`compas.geometry.Torus`
        The torus to convert.

    Returns
    -------
    :class:`three.TorusGeometry`
        The PyThreeJS torus geometry.

    Examples
    --------
    >>> from compas.geometry import Torus
    >>> torus = Torus(radius_axis=1, radius_pipe=0.2)
    >>> torus_to_threejs(torus)  # doctest: +ELLIPSIS
    TorusGeometry(...)

    """
    return three.TorusGeometry(radius=torus.radius_axis, tube=torus.radius_pipe, radialSegments=64, tubularSegments=32)
