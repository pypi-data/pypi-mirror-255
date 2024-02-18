from datetime import datetime
from typing import Optional

import pydantic


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


class InternalLineage(pydantic.BaseModel):
    from_databuilder_id: str
    to_databuilder_id: str
