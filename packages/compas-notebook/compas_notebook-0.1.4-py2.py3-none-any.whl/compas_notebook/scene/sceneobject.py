import pythreejs as three
import numpy
from compas.geometry import Transformation, Rotation
from compas.scene import SceneObject

Rx = Rotation.from_axis_and_angle([1, 0, 0], 3.14159 / 2)


class ThreeSceneObject(SceneObject):
    """Base class for all PyThreeJS scene objects."""

    def y_to_z(self, transformation: Transformation) -> Transformation:
        """Convert a transformation from COMPAS to the ThreeJS coordinate system.

        Parameters
        ----------
        transformation : :class:`compas.geometry.Transformation`
            The transformation to convert.

        Returns
        -------
        :class:`compas.geometry.Transformation`
            The converted transformation.

        """
        return transformation * Rx

    def geometry_to_objects(self, geometry, color, contrastcolor, transformation=None):
        """Convert a PyThreeJS geometry to a list of PyThreeJS objects.

        Parameters
        ----------
        geometry : :class:`three.Geometry`
            The PyThreeJS geometry to convert.
        color : rgb1 | rgb255 | :class:`compas.colors.Color`
            The RGB color of the geometry.
        contrastcolor : rgb1 | rgb255 | :class:`compas.colors.Color`
            The RGB color of the edges.
        transformation : :class:`compas.geometry.Transformation`, optional
            The transformation to apply to the geometry.

        Returns
        -------
        list[three.Mesh, three.LineSegments]
            List of PyThreeJS objects created.

        """
        edges = three.EdgesGeometry(geometry)
        mesh = three.Mesh(geometry, three.MeshBasicMaterial(color=color.hex, side="DoubleSide"))
        line = three.LineSegments(edges, three.LineBasicMaterial(color=contrastcolor.hex))

        if transformation:
            matrix = numpy.array(transformation.matrix, dtype=numpy.float32).transpose().ravel().tolist()
            mesh.matrix = matrix
            line.matrix = matrix
            mesh.matrixAutoUpdate = False
            line.matrixAutoUpdate = False

        return [mesh, line]
