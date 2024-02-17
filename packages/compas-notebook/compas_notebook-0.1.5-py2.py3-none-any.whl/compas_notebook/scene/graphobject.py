import pythreejs as three
from compas.scene import GraphObject
from compas_notebook.conversions import nodes_and_edges_to_threejs
from compas_notebook.conversions import nodes_to_threejs
from compas_notebook.scene import ThreeSceneObject


class GraphObject(ThreeSceneObject, GraphObject):
    """Scene object for drawing graph."""

    def draw(self, color=None):
        """Draw the graph associated with the scene object.

        Parameters
        ----------
        color : rgb1 | rgb255 | :class:`compas.colors.Color`, optional
            The RGB color of the graph.

        Returns
        -------
        list[three.LineSegments, three.Points]
            List of pythreejs objects created.

        """
        color = self.color if color is None else color
        contrastcolor = self.contrastcolor(color)

        nodes, edges = self.graph.to_nodes_and_edges()

        geometry = nodes_and_edges_to_threejs(nodes, edges)
        line = three.LineSegments(geometry, three.LineBasicMaterial(color=contrastcolor.hex))

        guids = [line]

        if self.show_nodes:
            geometry = nodes_to_threejs(nodes)
            points = three.Points(geometry, three.PointsMaterial(size=0.1, color=contrastcolor.hex))
            guids.append(points)

        self._guids = guids
        return self.guids
