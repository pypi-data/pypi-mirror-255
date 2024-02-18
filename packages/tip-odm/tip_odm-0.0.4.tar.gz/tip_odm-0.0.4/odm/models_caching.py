from pydantic import BaseModel, Field
import datetime


class Cache(BaseModel):
    key: str = Field(serialization_alias="key")
    name: str = Field(serialization_alias="name")
    last_refresh: datetime.datetime | None = Field(None, serialization_alias="lastRefresh")
    lazy: bool = Field(serialization_alias="lazy")
    is_invalidated: bool = Field(serialization_alias="isInvalidated")
    size_mb: float | None = Field(None, serialization_alias="sizeMB")
