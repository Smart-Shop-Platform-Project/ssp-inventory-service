from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.inventory import Inventory
import logging

logger = logging.getLogger("ssp-inventory-service")

class InventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_inventory(self, product_id: str):
        result = await self.db.execute(select(Inventory).where(Inventory.product_id == product_id))
        return result.scalars().first()

    async def update_inventory(self, product_id: str, quantity_change: int):
        try:
            inventory_item = await self.get_inventory(product_id)
            if inventory_item:
                inventory_item.quantity += quantity_change
            else:
                inventory_item = Inventory(product_id=product_id, quantity=quantity_change)
                self.db.add(inventory_item)
            
            await self.db.commit()
            return inventory_item
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating inventory for {product_id}: {e}")
            raise
