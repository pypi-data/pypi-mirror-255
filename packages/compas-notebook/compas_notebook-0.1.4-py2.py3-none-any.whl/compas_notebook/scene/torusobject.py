import pythreejs as three
from compas.scene import GeometryObject
from compas.colors import Color
from .sceneobject import ThreeSceneObject


class TorusObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing torus."""

    def draw(self, color: Color = None):
        """Draw the torus associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the torus.

        Returns
        -------
        list[three.Mesh, three.LineSegments]
            List of pythreejs objects created.

        """
        color: Color = Color.coerce(color) or self.color
        contrastcolor: Color = color.darkened(50) if color.is_light else color.lightened(50)

        geometry = three.TorusGeometry(
            radius=self.geometry.radius_axis,
            tube=self.geometry.radius_pipe,
        )
        transformation = self.y_to_z(self.geometry.transformation)

        self._guids = self.geometry_to_objects(
            geometry,
            color,
            contrastcolor,
            transformation=transformation,
        )
        return self.guids
