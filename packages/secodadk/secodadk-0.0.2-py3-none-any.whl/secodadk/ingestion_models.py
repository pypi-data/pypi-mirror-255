from datetime import datetime
from typing import Optional, Literal, Union

import pydantic
from pydantic import Field
from typing_extensions import Annotated


class Resource(pydantic.BaseModel):
    entity_type: str

    databuilder_id: str
    parent_databuilder_id: Optional[str] = None
    title: Optional[str] = ""
    description: Optional[str] = None
    definition: Optional[str] = None
    external_updated_at: Optional[datetime] = None
    native_type: Optional[str] = None

    # Column specific
    sort_order: Optional[int] = None
    type: Optional[str] = None
    is_pk: Optional[bool] = False
    hidden: Optional[bool] = False

    # Table specific, required for table
    schema: Optional[str] = None  # type: ignore
    database: Optional[str] = None

    # Dashboard specific
    group: Optional[str] = None

    # Chart specific
    product: Optional[str] = None


class InternalResource(pydantic.BaseModel):
    """
    InternalResource represents a resource that was declared and ingested by current integration.
    """

    type: Literal["internal_resource"] = "internal_resource"
    databuilder_id: str


class ExternalTable(pydantic.BaseModel):
    """
    ExternalTable represents a table in your workspace. It may or may not be part of the current integration.
    Secoda will use the following fields to match the table within the workspace.
    """

    type: Literal["external_table"] = "external_table"
    cluster: Optional[str] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    table: str


class ExternalColumn(pydantic.BaseModel):
    """
    ExternalColumn represents a column in your workspace. It may or may not be part of the current integration.
    Secoda will use the following fields to match the column within the workspace.
    """

    type: Literal["external_column"] = "external_column"
    cluster: Optional[str] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    table: str
    column: str


class TablesFromSQLQuery(pydantic.BaseModel):
    """
    TablesFromSQLQuery represents tables that are referenced in a SQL query.
    """

    type: Literal["tables_from_query"] = "tables_from_query"
    sql: str


# LineageID represents resource(s) in your workspace. The resource can be part of the current integration (InternalResource),
# or it can be a table or a column in your workspace (ExternalTable, ExternalColumn), or it can be a set of
# tables referenced in a SQL query (TablesFromSQLQuery).
LineageID = Annotated[
    Union[InternalResource, ExternalTable, ExternalColumn, TablesFromSQLQuery],
    Field(discriminator="type"),
]


class DeclaredLineage(pydantic.BaseModel):
    """
    A declared lineage represents a relationship between two resources in your workspace.
    """

    from_identifier: LineageID
    to_identifier: LineageID
