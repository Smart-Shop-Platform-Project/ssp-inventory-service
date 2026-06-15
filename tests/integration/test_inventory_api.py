import pytest
from unittest.mock import patch, AsyncMock
from app.models.inventory import Inventory

def test_get_inventory_api_found(client, db_session):
    # Setup: We need to use the actual service and repo for integration tests,
    # but we can pre-populate the in-memory DB.
    async def setup_db():
        async with db_session as session:
            session.add(Inventory(product_id="prod_api_1", quantity=50))
            await session.commit()

    import asyncio
    asyncio.run(setup_db())

    # Execute
    response = client.get("/api/v1/inventory/prod_api_1")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"product_id": "prod_api_1", "quantity": 50}

def test_get_inventory_api_not_found(client):
    # No setup needed, DB is clean for this test
    response = client.get("/api/v1/inventory/prod_api_unknown")

    assert response.status_code == 200
    assert response.json() == {"product_id": "prod_api_unknown", "quantity": 0}

def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "SSP Inventory Service is running"}
