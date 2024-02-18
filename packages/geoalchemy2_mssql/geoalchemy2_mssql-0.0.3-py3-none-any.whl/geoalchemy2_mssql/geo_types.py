"""This module defines the :class:`geoalchemy2_mssql.types.Geometry`.

:class:`geoalchemy2_mssql.types.Geography`, and :class:`geoalchemy2_mssql.types.Raster`
classes, that are used when defining geometry, geography and raster
columns/properties in models.

Reference
---------
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import ColumnElement, text
from sqlalchemy.dialects.postgresql.base import ischema_names as postgresql_ischema_names
from sqlalchemy.dialects.sqlite.base import ischema_names as sqlite_ischema_names
from sqlalchemy.sql import func
from sqlalchemy.types import UserDefinedType

if TYPE_CHECKING:
    from sqlalchemy.engine.interfaces import Dialect

from .comparator import Comparator
from .elements import RasterElement, WKBElement, WKTElement
from .exc import ArgumentError

SHAPELY = False
THREE_D = 3


class _GISType(UserDefinedType):
    """The base class for Geometry and Geography.

    This class defines ``bind_expression`` and ``column_expression`` methods
    that wrap column expressions in ``ST_GeomFromEWKT``, ``ST_GeogFromText``,
    or ``ST_AsEWKB`` calls.

    This class also defines ``result_processor`` and ``bind_processor``
    methods. The function returned by ``result_processor`` converts WKB values
    received from the database to :class:`geoalchemy2_mssql.elements.WKBElement`
    objects. The function returned by ``bind_processor`` converts
    :class:`geoalchemy2_mssql.elements.WKTElement` objects to EWKT strings.

    Args:
        geometry_type: The geometry type.

            Possible values are:

              * ``"GEOMETRY"``,
              * ``"POINT"``,
              * ``"LINESTRING"``,
              * ``"POLYGON"``,
              * ``"MULTIPOINT"``,
              * ``"MULTILINESTRING"``,
              * ``"MULTIPOLYGON"``,
              * ``"GEOMETRYCOLLECTION"``,
              * ``"CURVE"``,
              * ``None``.

           The latter is actually not supported with
           :class:`geoalchemy2_mssql.types.Geography`.

           When set to ``None`` then no "geometry type" constraints will be
           attached to the geometry type declaration. Using ``None`` here
           is not compatible with setting ``management`` to ``True``.

           Default is ``"GEOMETRY"``.

        srid: The SRID for this column. E.g. 4326. Default is ``-1``.
        dimension: The dimension of the geometry. Default is ``2``.

            With ``management`` set to ``True``, that is when ``AddGeometryColumn`` is used
            to add the geometry column, there are two constraints:

            * The ``geometry_type`` must not end with ``"ZM"``.  This is due to PostGIS'
              ``AddGeometryColumn`` failing with ZM geometry types. Instead the "simple"
              geometry type (e.g. POINT rather POINTZM) should be used with ``dimension``
              set to ``4``.
            * When the ``geometry_type`` ends with ``"Z"`` or ``"M"`` then ``dimension``
              must be set to ``3``.

            With ``management`` set to ``False`` (the default) ``dimension`` is not
            taken into account, and the actual dimension is fully defined with the
            ``geometry_type``.

        spatial_index: Indicate if a spatial index should be created. Default is ``True``.
        use_n_d_index: Use the N-D index instead of the standard 2-D index.
        management: Indicate if the ``AddGeometryColumn`` and ``DropGeometryColumn``
            managements functions should be called when adding and dropping the
            geometry column. Should be set to ``True`` for PostGIS 1.x and SQLite. Default is
            ``False``. Note that this option has no effect for
            :class:`geoalchemy2_mssql.types.Geography`.
        use_typmod: By default PostgreSQL type modifiers are used to create the geometry
            column. To use check constraints instead set ``use_typmod`` to
            ``False``. By default this option is not included in the call to
            ``AddGeometryColumn``. Note that this option is only taken
            into account if ``management`` is set to ``True`` and is only available
            for PostGIS 2.x.
    """

    name: str | None = None
    """ Name used for defining the main geo type (geometry or geography)
        in CREATE TABLE statements. Set in subclasses. """

    from_text: str | None = None
    """ The name of "from text" function for this type.
        Set in subclasses. """

    as_binary: str | None = None
    """ The name of the "as binary" function for this type.
        Set in subclasses. """

    comparator_factory = Comparator
    """ This is the way by which spatial operators are defined for
        geometry/geography columns. """

    cache_ok: bool = False
    """ Disable cache for this type. """

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        geometry_type: str | None = "GEOMETRY",
        srid: int = -1,
        dimension: int = 2,
        spatial_index: bool = True,
        use_n_d_index: bool = False,
        management: bool = False,
        use_typmod: bool | None = None,
        from_text: str | None = None,
        name: str | None = None,
        nullable: bool | None = True,
    ) -> None:
        geometry_type, srid = self.check_ctor_args(
            geometry_type,
            srid,
            dimension,
            management,
            use_typmod,
            nullable,
        )
        self.geometry_type = geometry_type
        self.srid = srid
        if name is not None:
            self.name = name
        if from_text is not None:
            self.from_text = from_text
        self.dimension = dimension
        self.spatial_index = spatial_index
        self.use_n_d_index = use_n_d_index
        self.management = management
        self.use_typmod = use_typmod
        self.extended: bool | None = self.as_binary == "ST_AsEWKB"
        self.nullable = nullable

    def get_col_spec(self) -> str | None:
        # if not self.geometry_type:
        return self.name

    def column_expression(self, col: ColumnElement) -> None | ColumnElement:
        """Specific column_expression that automatically adds a conversion function."""
        return func.IIF(col is None, None, col.as_text(), type_=self)
        # select
        # return getattr(func, self.as_binary)(col, type_=self

    def result_processor(self, *_: Any) -> Any:  # noqa: PLR6301
        """Specific result_processor that automatically process spatial elements."""

        def process(value: Any) -> Any:
            return value
            # if value is not None:
            #     if self.srid > 0:
            #     if self.extended is not None:

        return process

    def bind_expression(self, bindvalue: Any) -> Any:
        """Specific bind_expression that automatically adds a conversion function."""
        return text(f"{self.name}::STGeomFromText(:{bindvalue.key}, {self.srid})").bindparams(
            bindvalue,
        )

    def bind_processor(self, dialect: "Dialect") -> Any:  # noqa: PLR6301
        """Specific bind_processor that automatically process spatial elements."""

        def process(bindvalue: Any) -> Any:
            if isinstance(bindvalue, WKTElement):
                if bindvalue.extended:
                    return f"{bindvalue.data}"
                return "SRID=%d;%s" % (bindvalue.srid, bindvalue.data)
            if isinstance(bindvalue, WKBElement):
                if dialect.name == "sqlite" or not bindvalue.extended:
                    # With SpatiaLite or when the WKBElement includes a WKB value rather
                    # than a EWKB value we use Shapely to convert the WKBElement to an
                    # EWKT string
                    # if not SHAPELY:
                    raise ArgumentError
                return bindvalue.desc
            if isinstance(bindvalue, RasterElement):
                return "%s" % (bindvalue.data)
            return bindvalue

        return process

    @staticmethod
    def check_ctor_args(  # noqa: PLR0913, PLR0917
        geometry_type: str | None,
        srid: int,
        dimension: int,
        management: bool,
        use_typmod: bool | None,
        nullable: bool | None,
    ) -> tuple[str, int]:
        """Check the arguments passed to the constructor."""
        try:
            srid = int(srid)
        except ValueError as error:
            raise ArgumentError("srid") from error
        if geometry_type:
            geometry_type = geometry_type.upper()
            if management and geometry_type.endswith("ZM"):
                # PostGIS' AddGeometryColumn does not work with ZM geometry types. Instead,
                # the simple geometry type (e.g. POINT rather POINTZM) should be used with
                # dimension set to 4
                error_str = (
                    f"with management=True use geometry_type={geometry_type[:-2]} and "
                    f"dimension=4 for {geometry_type} geometries"
                )
                raise ArgumentError(error_str)

            if management and geometry_type[-1] in {"Z", "M"} and dimension != THREE_D:
                # If a Z or M geometry type is used then dimension must be set to 3
                raise ArgumentError("not_3D")
        else:
            raise ArgumentError("geometry_type")

        if use_typmod and not management:
            raise ArgumentError
        if use_typmod is not None and not nullable:
            raise ArgumentError

        return geometry_type, srid


class Geometry(_GISType):
    """The Geometry type.

    Creating a geometry column is done like this::

        Column(Geometry(geometry_type='POINT', srid=4326))

    See :class:`geoalchemy2_mssql.types._GISType` for the list of arguments that can
    be passed to the constructor.

    If ``srid`` is set then the ``WKBElement`` objects resulting from queries will
    have that SRID, and, when constructing the ``WKBElement`` objects, the SRID
    won't be read from the data returned by the database. If ``srid`` is not set
    (meaning it's ``-1``) then the SRID set in ``WKBElement`` objects will be read
    from the data returned by the database.
    """

    name = "geometry"
    """ Type name used for defining geometry columns in ``CREATE TABLE``. """

    from_text = "STGeomFromText"
    """ The "from text" geometry constructor. Used by the parent class'
        ``bind_expression`` method. """

    as_binary = "STAsBinary"
    """ The "as binary" function to use. Used by the parent class'
        ``column_expression`` method. """

    ElementType = WKBElement
    """ The element class to use. Used by the parent class'
        ``result_processor`` method. """

    cache_ok = False
    """ Disable cache for this type. """


class Geography(_GISType):
    """The Geography type.

    Creating a geography column is done like this::

        Column(Geography(geometry_type='POINT', srid=4326))

    See :class:`geoalchemy2_mssql.types._GISType` for the list of arguments that can
    be passed to the constructor.

    """

    name = "geography"
    """ Type name used for defining geography columns in ``CREATE TABLE``. """

    from_text = "ST_GeogFromText"
    """ The ``FromText`` geography constructor. Used by the parent class'
        ``bind_expression`` method. """

    as_binary = "STAsBinary"
    """ The "as binary" function to use. Used by the parent class'
        ``column_expression`` method. """

    ElementType = WKBElement
    """ The element class to use. Used by the parent class'
        ``result_processor`` method. """

    cache_ok = False
    """ Disable cache for this type. """


class Raster(_GISType):
    """The Raster column type.

    Creating a raster column is done like this::

        Column(Raster)

    This class defines the ``result_processor`` method, so that raster values
    received from the database are converted to
    :class:`geoalchemy2_mssql.elements.RasterElement` objects.

    Args:
        spatial_index: Indicate if a spatial index should be created. Default is ``True``.

    """

    """
    This is the way by which spatial operators and functions are
    defined for raster columns.
    """

    name = "raster"
    """ Type name used for defining raster columns in ``CREATE TABLE``. """

    from_text = "raster"
    """ The "from text" raster constructor. Used by the parent class'
        ``bind_expression`` method. """

    as_binary = "raster"
    """ The "as binary" function to use. Used by the parent class'
        ``column_expression`` method. """

    ElementType = RasterElement
    """ The element class to use. Used by the parent class'
        ``result_processor`` method. """

    cache_ok = False
    """ Disable cache for this type. """

    def __init__(
        self,
        spatial_index: bool = True,
        from_text: str | None = None,
        name: str | None = None,
        nullable: bool | None = True,
    ) -> None:
        """INIT geotype."""
        # Enforce default values
        super().__init__(
            geometry_type=None,
            srid=-1,
            dimension=2,
            spatial_index=spatial_index,
            use_n_d_index=False,
            management=False,
            use_typmod=False,
            from_text=from_text,
            name=name,
            nullable=nullable,
        )
        self.extended = None


class _DummyGeometry(Geometry):
    """A dummy type only used with SQLite."""

    def get_col_spec(self) -> str:  # noqa: PLR6301
        return "GEOMETRY"


# Register Geometry, Geography and Raster to SQLAlchemy's reflection subsystems.
postgresql_ischema_names["geometry"] = Geometry
postgresql_ischema_names["geography"] = Geography
postgresql_ischema_names["raster"] = Raster

sqlite_ischema_names["GEOMETRY"] = Geometry
sqlite_ischema_names["POINT"] = Geometry
sqlite_ischema_names["LINESTRING"] = Geometry
sqlite_ischema_names["POLYGON"] = Geometry
sqlite_ischema_names["MULTIPOINT"] = Geometry
sqlite_ischema_names["MULTILINESTRING"] = Geometry
sqlite_ischema_names["MULTIPOLYGON"] = Geometry
sqlite_ischema_names["CURVE"] = Geometry
sqlite_ischema_names["GEOMETRYCOLLECTION"] = Geometry
sqlite_ischema_names["RASTER"] = Raster
