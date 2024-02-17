import pythreejs as three
from compas.scene import GeometryObject
from compas.colors import Color
from .sceneobject import ThreeSceneObject


class ConeObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing cone."""

    def draw(self, color: Color = None):
        """Draw the cone associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the cone.

        Returns
        -------
        list[three.Mesh, three.LineSegments]
            List of pythreejs objects created.

        """
        color: Color = Color.coerce(color) or self.color

        geometry = three.CylinderGeometry(
            radiusTop=0,
            radiusBottom=self.geometry.radius,
            height=self.geometry.height,
            radialSegments=32,
        )
        transformation = self.y_to_z(self.geometry.transformation)

        self._guids = self.geometry_to_objects(
            geometry,
            color,
            transformation=transformation,
        )
        return self.guids
