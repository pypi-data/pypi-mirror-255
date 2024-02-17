import pythreejs as three
from compas.scene import GeometryObject
from compas.colors import Color
from compas_notebook.conversions import line_to_threejs
from .sceneobject import ThreeSceneObject


class LineObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing line."""

    def draw(self, color: Color = None):
        """Draw the line associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the line.

        Returns
        -------
        list[three.Line]
            List of pythreejs objects created.

        """
        color = self.color if color is None else color
        contrastcolor = self.contrastcolor(color)

        geometry = line_to_threejs(self.geometry)
        line = three.Line(geometry, three.LineBasicMaterial(color=contrastcolor.hex))

        guids = [line]

        self._guids = guids
        return self.guids
