import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.database import get_db, Base, engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_inventory.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client():
    # Since the app starts a background consumer, we need to manage it for tests
    with patch("app.main.asyncio.create_task") as mock_create_task:
        yield TestClient(app)

@pytest.fixture(scope="function")
def mock_kafka_consumer():
    with patch("app.events.kafka_consumer.KafkaConsumer") as MockKafka:
        mock_consumer_instance = MagicMock()
        MockKafka.return_value = mock_consumer_instance

        with patch("app.events.kafka_consumer.consumer_service.consumer", mock_consumer_instance):
            yield mock_consumer_instance
