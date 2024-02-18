from compas.colors import Color
from pythreejs import MeshBasicMaterial


def color_to_threejs(color: Color) -> MeshBasicMaterial:
    """Convert a COMPAS color to a PyThreeJS material.

    Parameters
    ----------
    color : :class:`compas.colors.Color`
        The color to convert.

    Returns
    -------
    :class:`three.MeshBasicMaterial`
        The PyThreeJS material.

    Examples
    --------
    >>> from compas.colors import Color
    >>> color = Color.from_rgb255(255, 0, 0)
    >>> color_to_threejs(color)
    MeshBasicMaterial(alphaMap=None, aoMap=None, color='#ff0000', envMap=None, lightMap=None, map=None, specularMap=None)

    """
    return MeshBasicMaterial(color=color.hex)
