from typing import Any
import pythreejs as three
from compas.geometry import Brep
from compas.scene import GeometryObject
from compas_notebook.conversions import vertices_and_faces_to_threejs
from compas_notebook.conversions import polyline_to_threejs
from compas_notebook.scene import ThreeSceneObject


class BrepObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing a Brep."""

    def __init__(self, item: Brep, *args: Any, **kwargs: Any):
        super().__init__(geometry=item, *args, **kwargs)
        self.brep = item

    def draw(self, color=None):
        """Draw the Brep associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the Brep.

        Returns
        -------
        list[three.Mesh, three.LineSegments]
            List of pythreejs objects created.

        """
        color = self.color if color is None else color
        contrastcolor = self.contrastcolor(color)

        mesh, polylines = self.brep.to_viewmesh()
        vertices, faces = mesh.to_vertices_and_faces()

        geometry = vertices_and_faces_to_threejs(vertices, faces)
        mesh = three.Mesh(geometry, three.MeshBasicMaterial(color=color.hex, side="DoubleSide"))

        guids = [mesh]

        for polyline in polylines:
            geometry = polyline_to_threejs(polyline)
            line = three.LineSegments(geometry, three.LineBasicMaterial(color=contrastcolor.hex))
            guids.append(line)

        self._guids = guids
        return self.guids
