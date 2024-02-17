import pythreejs as three
from compas.scene import GeometryObject
from compas.colors import Color
from compas_notebook.conversions import polyline_to_threejs
from .sceneobject import ThreeSceneObject


class PolylineObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing polyline."""

    def draw(self, color: Color = None):
        """Draw the polyline associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the polyline.

        Returns
        -------
        list[three.Line]
            List of pythreejs objects created.

        """
        color = self.color if color is None else color
        contrastcolor = self.contrastcolor(color)

        geometry = polyline_to_threejs(self.geometry)
        polyline = three.Line(geometry, three.LineBasicMaterial(color=contrastcolor.hex))

        guids = [polyline]

        self._guids = guids
        return self.guids
