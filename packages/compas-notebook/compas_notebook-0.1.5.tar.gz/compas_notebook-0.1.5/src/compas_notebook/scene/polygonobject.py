import pythreejs as three
from compas.scene import GeometryObject
from compas.colors import Color
from compas.geometry import earclip_polygon
from compas.utilities import pairwise
from compas_notebook.conversions import vertices_and_edges_to_threejs
from compas_notebook.conversions import vertices_and_faces_to_threejs
from .sceneobject import ThreeSceneObject


class PolygonObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing polygons."""

    def draw(self, color: Color = None):
        """Draw the polygon associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the polygon.

        Returns
        -------
        list[three.Mesh, three.LineSegments]
            List of pythreejs objects created.

        """
        color: Color = Color.coerce(color) or self.color
        contrastcolor = self.contrastcolor(color)

        n = len(self.geometry.points)
        vertices = self.geometry.points
        triangles = earclip_polygon(self.geometry)
        edges = list(pairwise(range(len(vertices)))) + [(n - 1, 0)]

        geometry = vertices_and_faces_to_threejs(vertices, triangles)
        mesh = three.Mesh(geometry, three.MeshBasicMaterial(color=color.hex, side="DoubleSide"))

        geometry = vertices_and_edges_to_threejs(vertices, edges)
        line = three.LineSegments(geometry, three.LineBasicMaterial(color=contrastcolor.hex))

        self._guids = [mesh, line]
        return self.guids
