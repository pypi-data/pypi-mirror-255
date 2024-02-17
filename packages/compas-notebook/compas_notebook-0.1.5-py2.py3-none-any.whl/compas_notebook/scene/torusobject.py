import pythreejs as three
from compas.scene import GeometryObject
from compas.colors import Color
from .sceneobject import ThreeSceneObject


class TorusObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing torus."""

    def draw(self, color: Color = None, u=128, v=32):
        """Draw the torus associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the torus.
        u : int, optional
            The number of segments around the main axis.
        v : int, optional
            The number of segments around the pipe axis.

        Returns
        -------
        list[three.Mesh, three.LineSegments]
            List of pythreejs objects created.

        """
        color: Color = Color.coerce(color) or self.color

        geometry = three.TorusGeometry(
            radius=self.geometry.radius_axis,
            tube=self.geometry.radius_pipe,
            radialSegments=v,
            tubularSegments=u,
        )
        transformation = self.y_to_z(self.geometry.transformation)

        self._guids = self.geometry_to_objects(
            geometry,
            color,
            transformation=transformation,
        )
        return self.guids
