from compas.scene import GeometryObject
from compas.colors import Color
from compas_notebook.conversions import polyhedron_to_threejs
from .sceneobject import ThreeSceneObject


class PolyhedronObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing polyhedron."""

    def draw(self, color: Color = None):
        """Draw the polyhedron associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the polyhedron.

        Returns
        -------
        list[three.Mesh, three.LineSegments]
            List of pythreejs objects created.

        """
        color: Color = Color.coerce(color) or self.color
        contrastcolor: Color = color.darkened(50) if color.is_light else color.lightened(50)

        geometry = polyhedron_to_threejs(self.geometry)

        self._guids = self.geometry_to_objects(geometry, color, contrastcolor)
        return self.guids
