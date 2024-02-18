"""Elements or types for geoalchemy2_mssql."""

import binascii
import struct
from typing import Any

from sqlalchemy.sql import functions

from .exc import ArgumentError

BinasciiError = binascii.Error

function_registry: set = set()

_EWKT_LEN = 2


class HasFunction:
    """Base class used as a marker to know if a given element has a 'geom_from' function."""


class _SpatialElement(HasFunction):
    """The base class for public spatial elements.

    Args:
        data: The first argument passed to the constructor is the data wrapped
            by the ``_SpatialElement`` object being constructed.
        srid: An integer representing the spatial reference system. E.g. ``4326``.
            Default value is ``-1``, which means no/unknown reference system.
        extended: A boolean indicating whether the extended format (EWKT or EWKB)
            is used. Default is ``False``.

    """

    def __init__(self, data: Any, srid: int = -1, extended: bool = False) -> None:
        self.srid = srid
        self.data = data
        self.extended = extended

    def __str__(self) -> str:
        answer: str = self.desc
        return answer

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} at 0x{id(self):x}; {self}>"

    def __eq__(self, other: object) -> bool:
        if not getattr(other, "extended", None) == self.extended:
            return False

        if not getattr(other, "srid", None) == self.srid:
            return False

        if not getattr(other, "desc", None) == self.desc:
            return False

        return True

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.desc, self.srid, self.extended))

    def __getattr__(self, name: str) -> Any:
        #
        # This is how things like lake.geom.ST_Buffer(2) creates
        # SQL expressions of this form:
        #
        # ST_Buffer(ST_GeomFromWKB(:ST_GeomFromWKB_1), :param_1)
        #

        # Raise an AttributeError when the attribute name doesn't start
        # with st_. This is to be nice with other libraries that use
        # some duck typing (e.g. hasattr(element, "copy")) to determine
        # the type of the element.

        if name.lower() not in function_registry:
            raise AttributeError

        # We create our own _FunctionGenerator here, and use it in place of
        # SQLAlchemy's "func" object. This is to be able to "bind" the
        # function to the SQL expression. See also GenericFunction above.
        func_ = functions._FunctionGenerator(expr=self)
        return getattr(func_, name)

    def __getstate__(self) -> dict:
        return {
            "srid": self.srid,
            "data": str(self),
            "extended": self.extended,
        }

    def __setstate__(self, state: dict) -> None:
        self.srid = state["srid"]
        self.extended = state["extended"]
        self.data = self._data_from_desc(state["data"])

    @staticmethod
    def _data_from_desc(desc: str) -> bytes:
        raise NotImplementedError


class WKTElement(_SpatialElement):
    """Instances of this class wrap a WKT or EWKT value.

    Usage examples::

        wkt_element_1 = WKTElement('POINT(5 45)')
        wkt_element_2 = WKTElement('POINT(5 45)', srid=4326)
        wkt_element_3 = WKTElement('SRID=4326;POINT(5 45)', extended=True)
    """

    geom_from = "ST_GeomFromText"
    geom_from_extended_version = "ST_GeomFromEWKT"

    def __init__(self, data: str, srid: int = -1, extended: bool = False) -> None:
        """Init wktelement."""
        if extended and srid == -1:
            # read srid from EWKT
            if not data.startswith("SRID="):
                raise ArgumentError("EWKT")
            data_s = data.split(";", 1)

            if len(data_s) != _EWKT_LEN:
                raise ArgumentError("EWKT")
            header = data_s[0]
            try:
                srid = int(header[5:])
            except ValueError as error:
                raise ArgumentError("EWKT") from error
        _SpatialElement.__init__(self, data, srid, extended)

    @property
    def desc(self) -> Any:
        """This element's description string."""
        return self.data

    @staticmethod
    def _data_from_desc(desc: Any) -> Any:
        return desc


class WKBElement(_SpatialElement):
    """Instances of this class wrap a WKB or EWKB value.

    Geometry values read from the database are converted to instances of this
    type. In most cases you won't need to create ``WKBElement`` instances
    yourself.

    If ``extended`` is ``True`` and ``srid`` is ``-1`` at construction time
    then the SRID will be read from the EWKB data.

    Note: you can create ``WKBElement`` objects from Shapely geometries
    using the :func:`geoalchemy2_mssql.shape.from_shape` function.
    """

    geom_from = "ST_GeomFromWKB"
    geom_from_extended_version = "ST_GeomFromEWKB"

    def __init__(self, data: Any, srid: int = -1, extended: bool = False) -> None:
        """WKB."""
        if extended and srid == -1:
            # read srid from the EWKB
            #
            # WKB struct {
            #    byte    byteOrder;
            #    uint32  wkbType;
            #    uint32  SRID;
            #    struct  geometry;
            # byteOrder enum {
            #     WKB_XDR = 0,  // Most Significant Byte First
            #     WKB_NDR = 1,  // Least Significant Byte First
            header = binascii.unhexlify(data[:18]) if isinstance(data, str) else data[:9]
            byte_order, srid_s = header[0], header[5:]
            srid = struct.unpack("<I" if byte_order else ">I", srid_s)[0]
        _SpatialElement.__init__(self, data, srid, extended)

    @property
    def desc(self) -> str:
        """This element's description string."""
        if isinstance(self.data, str):
            # SpatiaLite case
            return self.data.lower()
        return str(binascii.hexlify(self.data), encoding="utf-8").lower()

    @staticmethod
    def _data_from_desc(desc: str) -> bytes:
        desc_enc = desc.encode(encoding="utf-8")
        return binascii.unhexlify(desc_enc)


class RasterElement(_SpatialElement):
    """Instances of this class wrap a ``raster`` value.

    Raster values read
    from the database are converted to instances of this type. In
    most cases you won't need to create ``RasterElement`` instances
    yourself.
    """

    geom_from_extended_version = "raster"

    def __init__(self, data: Any) -> None:
        """Raster Element."""
        # read srid from the WKB (binary or hexadecimal format)
        # The WKB structure is documented in the file
        # raster/doc/RFC2-WellKnownBinaryFormat of the PostGIS sources.
        try:
            bin_data = binascii.unhexlify(data[:114])
        except BinasciiError:
            bin_data = data
            data = str(binascii.hexlify(data).decode(encoding="utf-8"))
        byte_order = bin_data[0]
        srid = bin_data[53:57]
        srid_i = struct.unpack("<I" if byte_order else ">I", srid)[0]
        _SpatialElement.__init__(self, data, srid_i, True)

    @property
    def desc(self) -> Any:
        """This element's description string."""
        return self.data

    @staticmethod
    def _data_from_desc(desc: Any) -> Any:
        return desc
