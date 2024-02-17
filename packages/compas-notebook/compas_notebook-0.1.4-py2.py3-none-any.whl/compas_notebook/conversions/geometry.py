import pythreejs as three
from compas.geometry import Box
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import Point
from compas.geometry import Polygon
from compas.geometry import Polyhedron
from compas.geometry import Polyline
from compas.geometry import Sphere
from compas.geometry import Torus


def point_to_threejs(point: Point) -> three.SphereGeometry:
    """Convert a COMPAS point to PyThreeJS.

    Parameters
    ----------
    point : :class:`compas.geometry.Point`
        The point to convert.

    Returns
    -------
    :class:`three.SphereGeometry`

    Examples
    --------
    >>> from compas.geometry import Point
    >>> point = Point(1, 2, 3)
    >>> point_to_threejs(point)  # doctest: +ELLIPSIS
    SphereGeometry(...)

    """
    return three.SphereGeometry(radius=0.05, widthSegments=32, heightSegments=32)


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
    geometry = three.BufferGeometry(
        attributes={
            "position": three.BufferAttribute([line.start, line.end], normalized=False),
        }
    )
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
    geometry = three.BufferGeometry(
        attributes={
            "position": three.BufferAttribute(polyline.points, normalized=False),
        }
    )
    return geometry


def polygon_to_threejs(polygon: Polygon) -> three.BufferGeometry:
    """Convert a COMPAS polygon to PyThreeJS.

    Parameters
    ----------
    polygon : :class:`compas.geometry.Polygon`
        The polygon to convert.

    Returns
    -------
    :class:`three.BufferGeometry`

    """
    raise NotImplementedError


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


# def capsule_to_threejs(cone: Capsule) -> three.CapsuleGeometry:
#     """Convert a COMPAS capsule to PyThreeJS.

#     Parameters
#     ----------
#     cone : :class:`compas.geometry.Capsule`
#         The capsule to convert.

#     Returns
#     -------
#     :class:`three.CapsuleGeometry`

#     Examples
#     --------
#     >>> from compas.geometry import Capsule
#     >>> capsule = Capsule(radius=1, height=2)
#     >>> capsule_to_threejs(cone)  # doctest: +ELLIPSIS
#     CapsuleGeometry(...)

#     """
#     return three.CapsuleGeometry()


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


def polyhedron_to_threejs(polyhedron: Polyhedron) -> three.BufferGeometry:
    raise NotImplementedError
