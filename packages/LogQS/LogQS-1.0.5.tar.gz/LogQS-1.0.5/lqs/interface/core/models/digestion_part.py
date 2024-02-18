from typing import List, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel

from lqs.interface.core.models.__common__ import (
    PaginationModel,
    ProcessModel,
    ProcessCreateRequest,
    ProcessUpdateRequest,
    optional_field,
)


class DigestionPartIndexEntry(BaseModel):
    topic_id: str
    ingestion_id: Optional[str]
    source: Optional[str]

    data_offset: int
    data_length: int

    chunk_compression: Optional[str]
    chunk_offset: Optional[int]
    chunk_length: Optional[int]
    timestamp: int


# TODO: in Python 3.11, we can use Tuple[*get_type_hints(DigestionPartIndex).values()]
DigestionPartIndexTuple = Tuple[
    str,
    Optional[str],
    Optional[str],
    int,
    int,
    Optional[str],
    Optional[int],
    Optional[int],
    int,
]


class DigestionPartIndex(BaseModel):
    digestion_part_id: UUID
    index: Optional[List[DigestionPartIndexTuple]]


class DigestionPartIndexCreateRequest(BaseModel):
    digestion_part_id: UUID
    index: Optional[List[DigestionPartIndexTuple]] = None


class DigestionPartIndexUpdateRequest(BaseModel):
    index: Optional[List[DigestionPartIndexTuple]] = optional_field


class DigestionPartIndexDataResponse(BaseModel):
    data: DigestionPartIndex


class DigestionPartIndexListResponse(PaginationModel):
    data: List[DigestionPartIndex]


# Digestion Part


class DigestionPart(ProcessModel["DigestionPart"]):
    sequence: int
    digestion_id: UUID

    index: Optional[List[DigestionPartIndexTuple]]

    log_id: Optional[UUID] = None
    group_id: Optional[UUID] = None


class DigestionPartCreateRequest(ProcessCreateRequest):
    sequence: int
    index: Optional[List[DigestionPartIndexTuple]] = None


class DigestionPartUpdateRequest(ProcessUpdateRequest):
    sequence: int = optional_field
    index: Optional[List[DigestionPartIndexTuple]] = optional_field


class DigestionPartDataResponse(BaseModel):
    data: DigestionPart


class DigestionPartListResponse(PaginationModel):
    data: List[DigestionPart]
