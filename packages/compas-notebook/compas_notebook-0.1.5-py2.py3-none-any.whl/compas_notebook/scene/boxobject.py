from compas.scene import GeometryObject
from compas.colors import Color
from compas_notebook.conversions import box_to_threejs
from .sceneobject import ThreeSceneObject


class BoxObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing box shapes."""

    def draw(self, color=None):
        """Draw the box associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the box.

        Returns
        -------
        list[three.Mesh, three.LineSegments]
            List of pythreejs objects created.

        """
        color = Color.coerce(color) or self.color

        geometry = box_to_threejs(self.geometry)
        transformation = self.y_to_z(self.geometry.transformation)

        self._guids = self.geometry_to_objects(
            geometry,
            color,
            transformation=transformation,
        )

        return self.guids
