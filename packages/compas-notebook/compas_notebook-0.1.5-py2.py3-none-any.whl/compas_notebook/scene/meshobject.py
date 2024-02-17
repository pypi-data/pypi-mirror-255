import pythreejs as three
from compas.scene import MeshObject
from compas_notebook.conversions import vertices_and_edges_to_threejs
from compas_notebook.conversions import vertices_and_faces_to_threejs
from compas_notebook.conversions import vertices_to_threejs
from compas_notebook.scene import ThreeSceneObject


class MeshObject(ThreeSceneObject, MeshObject):
    """Scene object for drawing mesh."""

    def draw(self, color=None):
        """Draw the mesh associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the mesh.

        Returns
        -------
        list[three.Mesh, three.LineSegments]
            List of pythreejs objects created.

        """
        color = self.color if color is None else color
        contrastcolor = self.contrastcolor(color)

        vertices, faces = self.mesh.to_vertices_and_faces()
        edges = list(self.mesh.edges())

        geometry = vertices_and_faces_to_threejs(vertices, faces)
        mesh = three.Mesh(geometry, three.MeshBasicMaterial(color=color.hex, side="DoubleSide"))

        geometry = vertices_and_edges_to_threejs(vertices, edges)
        line = three.LineSegments(geometry, three.LineBasicMaterial(color=contrastcolor.hex))

        guids = [mesh, line]

        if self.show_vertices:
            geometry = vertices_to_threejs(vertices)
            points = three.Points(geometry, three.PointsMaterial(size=0.1, color=contrastcolor.hex))
            guids.append(points)

        self._guids = guids
        return self.guids
