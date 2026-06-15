from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.inventory_repository import InventoryRepository
import logging

logger = logging.getLogger("ssp-inventory-service")

class InventoryService:
    def __init__(self, db: AsyncSession):
        self.repository = InventoryRepository(db)

    async def get_inventory(self, product_id: str):
        inventory = await self.repository.get_inventory(product_id)
        return {"product_id": product_id, "quantity": inventory.quantity if inventory else 0}

    async def process_order_event(self, order_data: dict):
        logger.info(f"Processing inventory for order: {order_data.get('order_id')}")
        try:
            for item in order_data.get('items', []):
                product_id = item['product_id']
                quantity = item['quantity']
                # Decrease inventory
                await self.repository.update_inventory(product_id, -quantity)
                logger.info(f"Reduced inventory for product {product_id} by {quantity}")
        except Exception as e:
            logger.error(f"Failed to process inventory for order {order_data.get('order_id')}: {e}")
            # The message will be re-processed by the consumer due to the error
            raise
