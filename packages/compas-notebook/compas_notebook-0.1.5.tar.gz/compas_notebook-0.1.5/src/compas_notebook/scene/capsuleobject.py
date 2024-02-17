import pythreejs as three
from compas.colors import Color
from compas.scene import GeometryObject
from compas.datastructures import Mesh
from compas_notebook.conversions import vertices_and_edges_to_threejs
from compas_notebook.conversions import vertices_and_faces_to_threejs
from .sceneobject import ThreeSceneObject


class CapsuleObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing capsule."""

    def draw(self, color: Color = None):
        """Draw the capsule associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the capsule.

        Returns
        -------
        list[three.Mesh, three.LineSegments]
            List of pythreejs objects created.

        """
        color: Color = Color.coerce(color) or self.color
        contrastcolor = self.contrastcolor(color)

        mesh = Mesh.from_shape(self.geometry)
        vertices, faces = mesh.to_vertices_and_faces()
        edges = list(mesh.edges())

        geometry = vertices_and_faces_to_threejs(vertices, faces)
        mesh = three.Mesh(geometry, three.MeshBasicMaterial(color=color.hex, side="DoubleSide"))

        geometry = vertices_and_edges_to_threejs(vertices, edges)
        line = three.LineSegments(geometry, three.LineBasicMaterial(color=contrastcolor.hex))

        self._guids = [mesh, line]

        return self.guids
