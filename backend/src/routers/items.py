from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/items", tags=["items"])


class Item(BaseModel):
    id: int
    name: str
    description: str = None


items_db = []


@router.get("/", response_model=List[Item])
async def read_items():
    return items_db


@router.post("/", response_model=Item)
async def create_item(item: Item):
    items_db.append(item)
    return item


@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")
