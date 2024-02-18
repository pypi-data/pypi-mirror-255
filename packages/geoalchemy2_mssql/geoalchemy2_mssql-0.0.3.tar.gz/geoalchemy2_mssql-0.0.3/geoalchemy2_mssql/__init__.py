"""GeoAlchemy2 package."""

from sqlalchemy import (
    Column,
    ColumnCollection,
    ColumnElement,
    Index,
    Table,
    event,
    select,
)
from sqlalchemy.engine import Connection
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator

from . import functions, geo_types  # noqa: F401
from .elements import RasterElement, WKBElement, WKTElement  # noqa: F401
from .exc import ArgumentError
from .geo_types import Geography, Geometry, Raster, _DummyGeometry


def _check_spatial_type(
    tested_type: object, spatial_types: type | tuple[type, ...], dialect: Dialect | None = None
) -> bool:
    return isinstance(tested_type, spatial_types) or (
        isinstance(tested_type, TypeDecorator)
        and dialect is not None
        and isinstance(tested_type.load_dialect_impl(dialect), spatial_types)
    )


def _spatial_idx_name(table: Table, column: Column) -> str:
    # this needs to change.
    return f"idx_{table.name}_{column.name}"


def check_management(column: ColumnElement, dialect: str) -> bool:
    """Check Management."""
    return getattr(column.type, "management", False) is True or dialect == "sqlite"


def shared_before(table: Table, bind: Connection) -> list[Column]:
    """Shared before functionality for spatial tables."""
    gis_cols = [
        col
        for col in table.columns
        if _check_spatial_type(col.type, Geometry, bind.dialect)
        and check_management(col, bind.dialect.name)
    ]

    # Find all other columns that are not managed Geometries
    regular_cols = [x for x in table.columns if x not in gis_cols]

    # Save original table column list for later
    table.info["_saved_columns"] = table.columns

    # Temporarily patch a set of columns not including the
    # managed Geometry columns
    column_collection: ColumnCollection = ColumnCollection()
    for col in regular_cols:
        column_collection.add(col)
    table.columns = column_collection  # type: ignore
    return gis_cols


# def _setup_ddl_event_listeners() -> None:
@event.listens_for(Table, "before_create")
def before_create(target: Table, connection: Connection, **_: dict) -> None:
    """Before create handler."""
    gis_cols = shared_before(target, connection)

    # Remove the spatial indexes from the table metadata because they should not be
    # created during the table.create() step since the associated columns do not exist
    # at this time.
    target.info["_after_create_indexes"] = []
    current_indexes = set(target.indexes)
    for idx in current_indexes:
        for col in target.info["_saved_columns"]:
            if (
                _check_spatial_type(col.type, Geometry, connection.dialect)
                and check_management(col, connection.dialect.name)
            ) and col in idx.columns.values():
                target.indexes.remove(idx)
                if idx.name != _spatial_idx_name(target, col) or not getattr(
                    col.type,
                    "spatial_index",
                    False,
                ):
                    target.info["_after_create_indexes"].append(idx)
    if connection.dialect.name == "sqlite":
        for col in gis_cols:
            # Add dummy columns with GEOMETRY type
            col._actual_type = col.type
            col.type = _DummyGeometry()
            col.nullable = col._actual_type.nullable
        target.columns = target.info["_saved_columns"]  # type: ignore


def create_index(connection: Connection, target: Table, col: Column) -> None:
    """Create an index on a column."""
    if connection.dialect.name == "sqlite":
        stmt = select(*func.CreateSpatialIndex(target.name, col.name))
        stmt = stmt.execution_options(autocommit=True)
        connection.execute(stmt)
    elif connection.dialect.name == "postgresql":
        # If the index does not exist (which might be the case when
        # management=False), define it and create it
        if not [i for i in target.indexes if col in i.columns.values()] and check_management(
            col,
            connection.dialect.name,
        ):
            postgresql_ops = (
                {col.name: "gist_geometry_ops_nd"}
                if col.type.use_n_d_index  # type: ignore
                else {}
            )
            idx = Index(
                _spatial_idx_name(target, col),
                col,
                postgresql_using="gist",
                postgresql_ops=postgresql_ops,
            )
            idx.create(bind=connection)

    else:
        raise ArgumentError(f"{connection.dialect.name}")


@event.listens_for(Table, "after_create")
def after_create(target: Table, connection: Connection, **_: dict) -> None:
    """After create handler."""
    target.columns = target.info.pop("_saved_columns")  # type: ignore

    for col in target.columns:
        # Add the managed Geometry columns with AddGeometryColumn()
        if _check_spatial_type(col.type, Geometry, connection.dialect) and check_management(
            col,
            connection.dialect.name,
        ):
            if connection.dialect.name == "sqlite":
                col.type = col._actual_type
                del col._actual_type
                create_func = func.RecoverGeometryColumn
            else:
                create_func = func.AddGeometryColumn

            args = [target.schema] if target.schema else []
            args.extend(
                [
                    target.name,
                    col.name,
                    col.type.srid,  # type: ignore
                    col.type.geometry_type,  # type: ignore
                    col.type.dimension,  # type: ignore
                ],
            )
            if col.type.use_typmod is not None:  # type: ignore
                args.append(col.type.use_typmod)  # type: ignore

            stmt = select(*create_func(*args))
            stmt = stmt.execution_options(autocommit=True)
            connection.execute(stmt)

        # Add spatial indices for the Geometry and Geography columns
        if (
            _check_spatial_type(col.type, (Geometry, Geography), connection.dialect)
            and col.type.spatial_index is True  # type: ignore
        ):
            create_index(connection, target, col)

        if (
            isinstance(col.type, Geometry | Geography)
            and col.type.spatial_index is False
            and col.type.use_n_d_index is True
        ):
            raise ArgumentError("spatial_index")

    for idx in target.info.pop("_after_create_indexes"):
        target.indexes.add(idx)
        idx.create(bind=connection)


@event.listens_for(Table, "before_drop")
def before_drop(target: Table, connection: Connection, **_: dict) -> None:
    """Before drop handler."""
    gis_cols = shared_before(target, connection)

    for col in gis_cols:
        if connection.dialect.name == "sqlite":
            drop_func = "DiscardGeometryColumn"
        elif connection.dialect.name == "postgresql":
            drop_func = "DropGeometryColumn"
        else:
            raise ArgumentError(f"{connection.dialect.name}")
        args = [target.schema] if target.schema else []
        args.extend([target.name, col.name])

        stmt = select(*getattr(func, drop_func)(*args))
        stmt = stmt.execution_options(autocommit=True)
        connection.execute(stmt)


@event.listens_for(Table, "after_drop")
def after_drop(target: Table, **_: dict) -> None:
    """After drop handler."""
    target.columns = target.info.pop("_saved_columns")  # type: ignore


@event.listens_for(Column, "after_parent_attach")
def after_parent_attach(column: Column, table: Table) -> None:
    """After parent attach handler."""
    if not getattr(column.type, "spatial_index", False) and getattr(
        column.type,
        "use_n_d_index",
        False,
    ):
        raise ArgumentError("spatial_index")

    if getattr(column.type, "management", True) or not getattr(
        column.type,
        "spatial_index",
        False,
    ):
        # If the column is managed, the indexes are created after the table
        return

    if _check_spatial_type(column.type, (Geometry, Geography)):
        # "doing postgresql only stuff"
        postgresql_ops: dict = {}
        Index(
            _spatial_idx_name(table, column),
            column,
            postgresql_using="gist",
            postgresql_ops=postgresql_ops,
        )
    elif _check_spatial_type(column.type, Raster):
        # "doing spatial index stuff"
        Index(
            _spatial_idx_name(table, column),
            func.ST_ConvexHull(column),
            postgresql_using="gist",
        )


# Get version number
__version__ = "146.0.0"
