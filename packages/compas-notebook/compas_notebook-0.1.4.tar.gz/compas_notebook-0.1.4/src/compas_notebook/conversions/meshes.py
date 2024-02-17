import pythreejs as three
import numpy


def vertices_and_faces_to_threejs(vertices, faces) -> three.BufferGeometry:
    """Convert vertices and faces to a PyThreeJS geometry.

    Parameters
    ----------
    vertices : list
        List of vertices.
    faces : list
        List of faces.

    Returns
    -------
    :class:`three.BufferGeometry`
        The PyThreeJS geometry.

    """
    triangles = []
    for face in faces:
        if len(face) == 3:
            triangles.append(face)
        elif len(face) == 4:
            triangles.append([face[0], face[1], face[2]])
            triangles.append([face[0], face[2], face[3]])
        else:
            raise NotImplementedError

    vertices = numpy.array(vertices, dtype=numpy.float32)
    triangles = numpy.array(triangles, dtype=numpy.uint32).ravel()

    geometry = three.BufferGeometry(
        attributes={
            "position": three.BufferAttribute(vertices, normalized=False),
            "index": three.BufferAttribute(triangles, normalized=False, itemSize=3),
        }
    )

    return geometry


def vertices_and_edges_to_threejs(vertices, edges) -> three.BufferGeometry:
    """Convert vertices and edges to a PyThreeJS geometry.

    Parameters
    ----------
    vertices : list
        List of vertices.
    edges : list
        List of edges.

    Returns
    -------
    :class:`three.BufferGeometry`
        The PyThreeJS geometry.

    """
    vertices = numpy.array(vertices, dtype=numpy.float32)
    edges = numpy.array(edges, dtype=numpy.uint32).ravel()

    geometry = three.BufferGeometry(
        attributes={
            "position": three.BufferAttribute(vertices, normalized=False),
            "index": three.BufferAttribute(edges, normalized=False, itemSize=2),
        }
    )

    # lines = []
    # for u, v in edges:
    #     lines.append([vertices[u], vertices[v]])
    # lines = numpy.array(lines, dtype=numpy.float32)

    # geometry = three.LineSegmentsGeometry(positions=lines)

    return geometry


def vertices_to_threejs(vertices) -> three.BufferGeometry:
    """Convert vertices to a PyThreeJS geometry.

    Parameters
    ----------
    vertices : list
        List of vertices.

    Returns
    -------
    :class:`three.BufferGeometry`
        The PyThreeJS geometry.

    """
    vertices = numpy.array(vertices, dtype=numpy.float32)
    geometry = three.BufferGeometry(attributes={"position": three.BufferAttribute(vertices, normalized=False)})
    return geometry
