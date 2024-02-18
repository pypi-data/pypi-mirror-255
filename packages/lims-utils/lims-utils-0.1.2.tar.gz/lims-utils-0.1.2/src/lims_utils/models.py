from typing import Generic, Sequence, TypeVar

from fastapi import Query
from pydantic import BaseModel, ConfigDict


def pagination(
    page: int = Query(
        0,
        description=(
            "Page number/Results to skip. Negative numbers count backwards from "
            "the last page"
        ),
    ),
    limit: int = Query(25, gt=0, description="Number of results to show"),
) -> dict[str, int]:
    return {"page": page, "limit": limit}


T = TypeVar("T")


class Paged(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
