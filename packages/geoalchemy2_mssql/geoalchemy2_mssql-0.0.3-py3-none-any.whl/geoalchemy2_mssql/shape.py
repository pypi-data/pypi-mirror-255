"""This module provides utility functions for integrating with Shapely.

As GeoAlchemy 2 itself has no dependency on `Shapely`, applications using
functions of this module have to ensure that `Shapely` is available.
"""

from typing import TYPE_CHECKING

from .elements import WKBElement, WKTElement

if TYPE_CHECKING:
    from shapely import Geometry


def to_shape(element: WKTElement | WKBElement) -> "Geometry":
    """Function to convert a SpatialElement to a Shapely geometry.

    Args:
        element: The element to convert into a ``Shapely`` object.

    Example::

        lake = Session.query(Lake).get(1)
        polygon = to_shape(lake.geom)
    """
    import shapely.wkb  # noqa: PLC0415
    import shapely.wkt  # noqa: PLC0415

    if isinstance(element, WKBElement):
        data = element.data if isinstance(element.data, str) else bytes(element.data)
        return shapely.wkb.loads(data, hex=isinstance(element.data, str))

    if element.extended:
        return shapely.wkt.loads(element.data.split(";", 1)[1])
    return shapely.wkt.loads(element.data)


def from_shape(shape: "Geometry", srid: int = -1, extended: bool = False) -> WKBElement:
    """Function to convert a Shapely geometry to a WKBElement.

    Args:
        shape:
            shapely element
        srid:
            An integer representing the spatial reference system. E.g. ``4326``.
            Default value is ``-1``, which means no/unknown reference system.
        extended:
            A boolean to switch between WKB and EWKB.
            Default value is False.

    Example::

        from shapely. geometry import Point
        wkb_element = from_shape(Point(5, 45), srid=4326)
        ewkb_element = from_shape(Point(5, 45), srid=4326, extended=True)
    """
    from shapely.wkb import dumps  # noqa: PLC0415

    return WKBElement(
        memoryview(dumps(shape, srid=srid if extended else None)),
        srid=srid,
        extended=extended,
    )
