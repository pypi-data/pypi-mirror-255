"""This module defines the :class:`GenericFunction` class.

 which is the base for
the implementation of spatial functions in GeoAlchemy.  This module is also
where actual spatial functions are defined. Spatial functions supported by
GeoAlchemy are defined in this module. See :class:`GenericFunction` to know how
to create new spatial functions.

.. note::

    By convention the names of spatial functions are prefixed by ``ST_``.  This
    is to be consistent with PostGIS', which itself is based on the ``SQL-MM``
    standard.

Functions created by subclassing :class:`GenericFunction` can be called
in several ways:

* By using the ``func`` object, which is the SQLAlchemy standard way of calling
  a function. For example, without the ORM::

      select([func.ST_Area(lake_table.c.geom)])

  and with the ORM::

      Session.query(func.ST_Area(Lake.geom))

* By applying the function to a geometry column. For example, without the
  ORM::

      select([lake_table.c.geom.ST_Area()])

  and with the ORM::

      Session.query(Lake.geom.ST_Area())

* By applying the function to a :class:`geoalchemy2_mssql.elements.WKBElement`
  object (:class:`geoalchemy2_mssql.elements.WKBElement` is the type into
  which GeoAlchemy converts geometry values read from the database), or
  to a :class:`geoalchemy2_mssql.elements.WKTElement` object. For example,
  without the ORM::

      conn.scalar(lake['geom'].ST_Area())

  and with the ORM::

      session.scalar(lake.geom.ST_Area())

Reference
---------

"""

import re
from typing import Any

from sqlalchemy import FromClause, inspect
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import annotation, functions
from sqlalchemy.sql.elements import ColumnElement

from . import elements
from ._functions import _FUNCTIONS


class GeoGenericFunction(functions.GenericFunction):
    """Generic function for spatial functions."""

    def __init_subclass__(cls) -> None:
        """Register the function in the function registry."""
        if annotation.Annotated not in cls.__mro__:
            cls._register_geo_function(cls.__name__, cls.__dict__)
        super().__init_subclass__()

    @classmethod
    def _register_geo_function(cls, clsname: str, *_: Any) -> None:
        # Check _register attribute status
        cls._register = getattr(cls, "_register", True)

        # Register the function if required
        if cls._register:
            elements.function_registry.add(clsname.lower())
        else:
            # Set _register to True to register child classes by default
            cls._register = True


_GeoFunctionBase = GeoGenericFunction
_GeoFunctionParent = GeoGenericFunction


class TableRowElement(ColumnElement):
    """Row of Table from ColumnElement."""

    inherit_cache = False

    def __init__(self, selectable: FromClause) -> None:
        """Initialize."""
        self.selectable: FromClause = selectable

    @property
    def _from_objects(self) -> list[FromClause]:
        return [self.selectable]


class ST_AsGeoJSON(_GeoFunctionBase):  # noqa: N801
    """Special process for the ST_AsGeoJSON() function.

    To be able to work with its feature version introduced in PostGIS 3.
    """

    name = "ST_AsGeoJSON"
    inherit_cache = True

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        """Initialize."""
        expr = kwargs.pop("expr", None)
        l_args: list[Any] = list(args)
        if expr is not None:
            l_args = [expr, *l_args]
        for idx, element in enumerate(l_args):
            if isinstance(element, functions.Function):
                continue
            if isinstance(element, elements.HasFunction):
                if element.extended:  # type: ignore
                    func_name = element.geom_from_extended_version  # type: ignore
                    func_args = [element.data]  # type: ignore
                else:
                    func_name = element.geom_from  # type: ignore
                    func_args = [element.data, element.srid]  # type: ignore
                l_args[idx] = getattr(functions.func, func_name)(*func_args)
            else:
                insp = inspect(element)
                if hasattr(insp, "selectable"):
                    l_args[idx] = TableRowElement(insp.selectable)

        _GeoFunctionParent.__init__(self, *l_args, **kwargs)


@compiles(TableRowElement)
def _compile_table_row_thing(element: Any, compiler: Any, **kw: Any) -> str:
    # In order to get a name as reliably as possible, noting that some
    # SQL compilers don't say "table AS name" and might not have the "AS",
    # table and alias names can have spaces in them, etc., get it from
    # a column instead because that's what we want to be showing here anyway.

    # compiled = compiler.process(list(element.selectable.columns)[0], **kw)
    compiled = compiler.process(next(iter(element.selectable.columns)), **kw)

    # 1. check for exact name of the selectable is here, use that.
    # This way if it has dots and spaces and anything else in it, we
    # can get it w/ correct quoting
    schema = getattr(element.selectable, "schema", "")
    pattern = rf"(.?{schema}.?\.)?(.?{element.selectable.name}.?)\."
    matched = re.match(pattern, compiled)
    if matched:
        return matched.group(2)

    # 2. just split on the dot, assume anonymized name
    answer: str = compiled.split(".")[0]
    return answer


class GenericFunction(_GeoFunctionBase):
    """The base class for GeoAlchemy functions.

    This class inherits from ``sqlalchemy.sql.functions.GenericFunction``, so
    functions defined by subclassing this class can be given a fixed return
    type. For example, functions like :class:`ST_Buffer` and
    :class:`ST_Envelope` have their ``type`` attributes set to
    :class:`geoalchemy2_mssql.types.Geometry`.

    This class allows constructs like ``Lake.geom.ST_Buffer(2)``. In that
    case the ``Function`` instance is bound to an expression (``Lake.geom``
    here), and that expression is passed to the function when the function
    is actually called.

    If you need to use a function that GeoAlchemy does not provide you will
    certainly want to subclass this class. For example, if you need the
    ``ST_TransScale`` spatial function, which isn't (currently) natively
    supported by GeoAlchemy, you will write this::

        from geoalchemy2_mssql import Geometry
        from geoalchemy2_mssql.functions import GenericFunction

        class ST_TransScale(GenericFunction):
            name = 'ST_TransScale'
            type = Geometry
    """

    # Set _register to False in order not to register this class in
    # sqlalchemy.sql.functions._registry. Only its children will be registered.
    _register = False

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        """Initialize."""
        expr = kwargs.pop("expr", None)
        l_args: list[Any] = list(args)
        if expr is not None:
            l_args = [expr, *l_args]
        for idx, elem in enumerate(l_args):
            if isinstance(elem, elements.HasFunction):
                if elem.extended:  # type: ignore
                    func_name = elem.geom_from_extended_version  # type: ignore
                    func_args = [elem.data]  # type: ignore
                else:
                    func_name = elem.geom_from  # type: ignore
                    func_args = [elem.data, elem.srid]  # type: ignore
                l_args[idx] = getattr(functions.func, func_name)(*func_args)
        _GeoFunctionParent.__init__(self, *l_args, **kwargs)


# Iterate through _FUNCTIONS and create GenericFunction classes dynamically
for name, type_, doc in _FUNCTIONS:
    attributes = {
        "name": name,
        "inherit_cache": True,
    }
    docs: list[str] = []

    if isinstance(doc, tuple):
        docs.extend((doc[0], f"see https://postgis.net/docs/{doc[1]}.html"))
    elif doc is not None:
        docs.extend((doc, f"see https://postgis.net/docs/{name}.html"))  # type: ignore

    if type_ is not None:
        attributes["type"] = type_

        type_str = f"{type_.__module__}.{type_.__name__}"
        docs.append(f"Return type: :class:`{type_str}`.")

    if len(docs) != 0:
        attributes["__doc__"] = "\n\n".join(docs)

    globals()[name] = type(name, (GenericFunction,), attributes)


#
# Define compiled versions for functions in SpatiaLite whose names don't have
# the ST_ prefix.
#


_SQLITE_FUNCTIONS = {
    "ST_GeomFromEWKT": "GeomFromEWKT",
    "ST_GeomFromEWKB": "GeomFromEWKB",
    "ST_AsBinary": "AsBinary",
    "ST_AsEWKB": "AsEWKB",
    "ST_AsGeoJSON": "AsGeoJSON",
}


# Default handlers are required for SQLAlchemy < 1.1
# See more details in https://github.com/geoalchemy/geoalchemy2/issues/213
def _compiles_default(cls: Any) -> Any:
    def _compile_default(element: Any, compiler: Any, **kw: dict) -> str:
        return f"{cls}({compiler.process(element.clauses, **kw)})"

    compiles(globals()[cls])(_compile_default)


def _compiles_sqlite(cls: Any, function: Any) -> Any:
    def _compile_sqlite(element: Any, compiler: Any, **kw: dict) -> str:
        return f"{function}({compiler.process(element.clauses, **kw)})"

    compiles(globals()[cls], "sqlite")(_compile_sqlite)


def register_sqlite_mapping(mapping: dict) -> None:
    """Register compilation mappings for the given functions.

    Args:
        mapping: Should have the following form::

                {
                    "function_name_1": "sqlite_function_name_1",
                    "function_name_2": "sqlite_function_name_2",
                    ...
                }
    """
    for cls, fn in mapping.items():
        _compiles_default(cls)
        _compiles_sqlite(cls, fn)


register_sqlite_mapping(_SQLITE_FUNCTIONS)
