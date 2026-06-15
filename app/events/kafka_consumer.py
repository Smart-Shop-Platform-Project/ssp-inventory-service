from kafka import KafkaConsumer
import json
import logging
from ..core.config import settings
from ..core.database import AsyncSessionLocal
from ..services.inventory_service import InventoryService

logger = logging.getLogger("ssp-inventory-service")

class KafkaConsumerService:
    def __init__(self):
        self.consumer = None
        try:
            self.consumer = KafkaConsumer(
                'order_created',
                bootstrap_servers=settings.KAFKA_BROKER_URL,
                auto_offset_reset='earliest',
                enable_auto_commit=False, # Manual commit for safety
                group_id='inventory-service-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info(f"Kafka consumer connected to {settings.KAFKA_BROKER_URL}")
        except Exception as e:
            logger.critical(f"Failed to initialize Kafka consumer: {e}")

    async def consume_messages(self):
        if not self.consumer:
            logger.error("Consumer not available, cannot consume messages.")
            return

        try:
            for message in self.consumer:
                order_data = message.value
                logger.info(f"Received order event: {order_data.get('order_id')}")
                
                async with AsyncSessionLocal() as session:
                    service = InventoryService(session)
                    try:
                        await service.process_order_event(order_data)
                        self.consumer.commit() # Commit offset only after successful processing
                        logger.info(f"Successfully processed and committed offset for order {order_data.get('order_id')}")
                    except Exception as e:
                        logger.error(f"Error processing message for order {order_data.get('order_id')}. Will not commit offset. Error: {e}")
                        # Not committing means this message will be re-processed after a rebalance
        except Exception as e:
            logger.critical(f"Kafka consumer loop failed: {e}")

    def close(self):
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed.")
