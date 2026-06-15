from fastapi import FastAPI
import logging
import sys
import asyncio
from .core.database import engine
from .api.inventory_routes import router as inventory_router
from .events.kafka_consumer import KafkaConsumerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s"}',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ssp-inventory-service")

app = FastAPI(title="SSP Inventory Service")
consumer_service = None
consumer_task = None

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Inventory Service...")
    global consumer_service, consumer_task
    consumer_service = KafkaConsumerService()
    consumer_task = asyncio.create_task(consumer_service.consume_messages())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Inventory Service...")
    if consumer_task:
        consumer_task.cancel()
    if consumer_service:
        consumer_service.close()
    await engine.dispose()

app.include_router(inventory_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "SSP Inventory Service is running"}
