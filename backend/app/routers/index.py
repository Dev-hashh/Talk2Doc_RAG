"""
routers/index.py
GET    /indexes          — list all available FAISS indexes
GET    /indexes/{name}   — check if a specific index exists
DELETE /indexes/{name}   — remove an index
"""
from fastapi import APIRouter, HTTPException, status
from fastapi import Depends
from sqlite3 import Row

from app.deps import get_current_user
from app.schemas.models import IndexInfo, IndexListResponse
from app.services.index_service import delete_index, index_exists, list_indexes

router = APIRouter(prefix="/indexes", tags=["Indexes"])


@router.get(
    "",
    response_model=IndexListResponse,
    summary="List all ingested indexes",
    description="Returns every (*.index + *.pkl) pair found in the index directory.",
)
async def get_indexes(user: Row = Depends(get_current_user)) -> IndexListResponse:
    indexes = list_indexes()
    return IndexListResponse(indexes=indexes, total=len(indexes))


@router.get(
    "/{name}",
    response_model=IndexInfo,
    summary="Get details of a single index",
)
async def get_index(
    name: str,
    user: Row = Depends(get_current_user),
) -> IndexInfo:
    matches = [i for i in list_indexes() if i.name == name]
    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Index '{name}' not found.",
        )
    return matches[0]


@router.delete(
    "/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an index",
    description="Removes the .index and .pkl files for the given index name.",
)
async def remove_index(
    name: str,
    user: Row = Depends(get_current_user),
) -> None:
    if not index_exists(name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Index '{name}' not found.",
        )
    delete_index(name)
