import pytest
from unittest.mock import AsyncMock
from app.services.inventory_service import InventoryService
from app.models.inventory import Inventory

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def inventory_service(mock_db_session):
    with patch("app.services.inventory_service.InventoryRepository") as MockRepo:
        mock_repo_instance = AsyncMock()
        MockRepo.return_value = mock_repo_instance
        
        service = InventoryService(mock_db_session)
        service.repository = mock_repo_instance
        return service

@pytest.mark.asyncio
async def test_get_inventory_found(inventory_service):
    # Setup
    mock_inventory = Inventory(product_id="prod1", quantity=100)
    inventory_service.repository.get_inventory.return_value = mock_inventory

    # Execute
    result = await inventory_service.get_inventory("prod1")

    # Assert
    assert result["quantity"] == 100
    inventory_service.repository.get_inventory.assert_called_once_with("prod1")

@pytest.mark.asyncio
async def test_get_inventory_not_found(inventory_service):
    # Setup
    inventory_service.repository.get_inventory.return_value = None

    # Execute
    result = await inventory_service.get_inventory("prod_unknown")

    # Assert
    assert result["quantity"] == 0

@pytest.mark.asyncio
async def test_process_order_event_success(inventory_service):
    # Setup
    order_data = {
        "order_id": "order1",
        "items": [
            {"product_id": "prod1", "quantity": 2},
            {"product_id": "prod2", "quantity": 1}
        ]
    }
    inventory_service.repository.update_inventory.return_value = None

    # Execute
    await inventory_service.process_order_event(order_data)

    # Assert
    assert inventory_service.repository.update_inventory.call_count == 2
    # Check the calls were to decrease inventory
    inventory_service.repository.update_inventory.assert_any_call("prod1", -2)
    inventory_service.repository.update_inventory.assert_any_call("prod2", -1)

@pytest.mark.asyncio
async def test_process_order_event_db_failure(inventory_service):
    # Setup
    order_data = {"order_id": "order1", "items": [{"product_id": "prod1", "quantity": 1}]}
    inventory_service.repository.update_inventory.side_effect = Exception("DB is down")

    # Execute and Assert
    with pytest.raises(Exception) as exc_info:
        await inventory_service.process_order_event(order_data)
    
    assert "DB is down" in str(exc_info.value)
    inventory_service.repository.update_inventory.assert_called_once()
