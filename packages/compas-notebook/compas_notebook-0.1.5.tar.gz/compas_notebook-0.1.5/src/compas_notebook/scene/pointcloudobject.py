import pythreejs as three
from compas.scene import GeometryObject
from compas.colors import Color
from compas_notebook.conversions import pointcloud_to_threejs
from .sceneobject import ThreeSceneObject


class PointcloudObject(ThreeSceneObject, GeometryObject):
    """Scene object for drawing pointcloud."""

    def draw(self, color: Color = None):
        """Draw the pointcloud associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the pointcloud.

        Returns
        -------
        list[three.Points]
            List of pythreejs objects created.

        """
        color: Color = Color.coerce(color) or self.color

        geometry = pointcloud_to_threejs(self.geometry)
        material = three.PointsMaterial(size=0.1, color=color.hex)
        pointclouds = three.Points(geometry, material)

        self._guids = [pointclouds]
        return self.guids
