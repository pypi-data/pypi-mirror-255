import pythreejs as three
from compas.scene import GeometryObject
from compas.colors import Color
from compas_notebook.conversions import point_to_threejs
from .sceneobject import ThreeSceneObject


class PointObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing point."""

    def draw(self, color: Color = None):
        """Draw the point associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the point.

        Returns
        -------
        list[three.Points]
            List of pythreejs objects created.

        """
        color: Color = Color.coerce(color) or self.color

        geometry = point_to_threejs(self.geometry)
        material = three.PointsMaterial(size=0.1, color=color.hex)
        points = three.Points(geometry, material)

        self._guids = [points]
        return self.guids
