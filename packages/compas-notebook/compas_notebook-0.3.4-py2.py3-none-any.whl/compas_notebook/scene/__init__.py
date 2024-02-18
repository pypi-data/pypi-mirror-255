"""This package provides scene object plugins for visualising COMPAS objects in Jupyter Notebooks using three.
When working in a notebook, :class:`compas.scene.SceneObject` will automatically use the corresponding PyThreeJS scene object for each COMPAS object type.

"""

from compas.plugins import plugin
from compas.scene import register

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

from compas.datastructures import Graph
from compas.datastructures import Mesh

from .sceneobject import ThreeSceneObject

from .boxobject import ThreeBoxObject
from .brepobject import ThreeBrepObject
from .capsuleobject import ThreeCapsuleObject
from .coneobject import ThreeConeObject
from .cylinderobject import ThreeCylinderObject
from .lineobject import ThreeLineObject
from .pointobject import ThreePointObject
from .pointcloudobject import ThreePointcloudObject
from .polygonobject import ThreePolygonObject
from .polyhedronobject import ThreePolyhedronObject
from .polylineobject import ThreePolylineObject
from .sphereobject import ThreeSphereObject
from .torusobject import ThreeTorusObject

from .graphobject import ThreeGraphObject
from .meshobject import ThreeMeshObject


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
    register(Box, ThreeBoxObject, context="Notebook")
    register(Brep, ThreeBrepObject, context="Notebook")
    register(Capsule, ThreeCapsuleObject, context="Notebook")
    register(Cone, ThreeConeObject, context="Notebook")
    register(Cylinder, ThreeCylinderObject, context="Notebook")
    register(Graph, ThreeGraphObject, context="Notebook")
    register(Line, ThreeLineObject, context="Notebook")
    register(Point, ThreePointObject, context="Notebook")
    register(Pointcloud, ThreePointcloudObject, context="Notebook")
    register(Polygon, ThreePolygonObject, context="Notebook")
    register(Polyhedron, ThreePolyhedronObject, context="Notebook")
    register(Polyline, ThreePolylineObject, context="Notebook")
    register(Sphere, ThreeSphereObject, context="Notebook")
    register(Torus, ThreeTorusObject, context="Notebook")
    register(Mesh, ThreeMeshObject, context="Notebook")

    print("PyThreeJS SceneObjects registered.")


__all__ = [
    "ThreeBoxObject",
    "ThreeCapsuleObject",
    "ThreeConeObject",
    "ThreeCylinderObject",
    "ThreeGraphObject",
    "ThreePointObject",
    "ThreePointcloudObject",
    "ThreePolygonObject",
    "ThreePolyhedronObject",
    "ThreePolylineObject",
    "ThreeSceneObject",
    "ThreeSphereObject",
    "ThreeTorusObject",
]
