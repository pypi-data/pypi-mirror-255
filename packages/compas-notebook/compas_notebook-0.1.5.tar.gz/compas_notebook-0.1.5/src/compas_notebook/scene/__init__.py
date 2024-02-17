"""This package provides scene object plugins for visualising COMPAS objects in Jupyter Notebooks using three.
When working in a notebook, :class:`compas.scene.SceneObject` will automatically use the corresponding PyThreeJS scene object for each COMPAS object type.

"""

from compas.plugins import plugin
from compas.scene import register

# from compas.geometry import Circle
# from compas.geometry import Curve
# from compas.geometry import Ellipse
# from compas.geometry import Frame
# from compas.geometry import Plane
# from compas.geometry import Surface
# from compas.geometry import Vector

from compas.geometry import Box
from compas.geometry import Brep
from compas.geometry import Capsule
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Pointcloud
from compas.geometry import Polygon
from compas.geometry import Polyhedron
from compas.geometry import Polyline
from compas.geometry import Sphere
from compas.geometry import Torus

# from compas.datastructures import VolMesh

from compas.datastructures import Graph
from compas.datastructures import Mesh

from .sceneobject import ThreeSceneObject

# from .circleobject import CircleObject
# from .ellipseobject import EllipseObject
# from .frameobject import FrameObject
# from .planeobject import PlaneObject
# from .vectorobject import VectorObject
# from .curveobject import CurveObject
# from .surfaceobject import SurfaceObject

from .boxobject import BoxObject
from .brepobject import BrepObject
from .capsuleobject import CapsuleObject
from .coneobject import ConeObject
from .cylinderobject import CylinderObject
from .lineobject import LineObject
from .pointobject import PointObject
from .pointcloudobject import PointcloudObject
from .polygonobject import PolygonObject
from .polyhedronobject import PolyhedronObject
from .polylineobject import PolylineObject
from .sphereobject import SphereObject
from .torusobject import TorusObject

# from .volmeshobject import VolMeshObject

from .graphobject import GraphObject
from .meshobject import MeshObject


@plugin(category="drawing-utils", pluggable_name="clear", requires=["pythreejs"])
def clear_pythreejs(guids=None):
    pass


@plugin(category="drawing-utils", pluggable_name="redraw", requires=["pythreejs"])
def redraw_pythreejs():
    pass


@plugin(
    category="drawing-utils",
    pluggable_name="after_draw",
    requires=["pythreejs"],
)
def after_draw(sceneobjects):
    pass


@plugin(category="factories", requires=["pythreejs"])
def register_scene_objects():
    # register(Circle, CircleObject, context="Notebook")
    # register(Ellipse, EllipseObject, context="Notebook")
    # register(Frame, FrameObject, context="Notebook")
    # register(Plane, PlaneObject, context="Notebook")
    # register(Vector, VectorObject, context="Notebook")
    # register(VolMesh, VolMeshObject, context="Notebook")
    # register(Curve, CurveObject, context="Notebook")
    # register(Surface, SurfaceObject, context="Notebook")

    register(Box, BoxObject, context="Notebook")
    register(Brep, BrepObject, context="Notebook")
    register(Capsule, CapsuleObject, context="Notebook")
    register(Cone, ConeObject, context="Notebook")
    register(Cylinder, CylinderObject, context="Notebook")
    register(Graph, GraphObject, context="Notebook")
    register(Line, LineObject, context="Notebook")
    register(Point, PointObject, context="Notebook")
    register(Pointcloud, PointcloudObject, context="Notebook")
    register(Polygon, PolygonObject, context="Notebook")
    register(Polyhedron, PolyhedronObject, context="Notebook")
    register(Polyline, PolylineObject, context="Notebook")
    register(Sphere, SphereObject, context="Notebook")
    register(Torus, TorusObject, context="Notebook")
    register(Mesh, MeshObject, context="Notebook")

    print("PyThreeJS SceneObjects registered.")


__all__ = [
    "BoxObject",
    "CapsuleObject",
    "ConeObject",
    "CylinderObject",
    "GraphObject",
    "PointObject",
    "PointcloudObject",
    "PolygonObject",
    "PolyhedronObject",
    "PolylineObject",
    "SphereObject",
    "TorusObject",
    "ThreeSceneObject",
]
