from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..services.inventory_service import InventoryService
from pydantic import BaseModel

router = APIRouter()

class InventoryResponse(BaseModel):
    product_id: str
    quantity: int

@router.get("/inventory/{product_id}", response_model=InventoryResponse, tags=["Inventory"])
async def get_inventory(product_id: str, db: AsyncSession = Depends(get_db)):
    service = InventoryService(db)
    return await service.get_inventory(product_id)
