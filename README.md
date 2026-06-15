# SSP Inventory Service

This service is responsible for maintaining the stock levels of all products in the Smart Shop Platform. It is an event-driven service that listens to Kafka events to update inventory.

## Core Responsibilities & Features

1.  **Inventory Management:**
    *   Maintains the canonical count of available stock for each product ID in a PostgreSQL database.
    *   Provides an API endpoint to query the current stock level for a given product.

2.  **Event-Driven Updates:**
    *   The primary function of this service is to act as a **Kafka consumer**.
    *   It subscribes to the `order_created` topic. When a new order is placed, this service consumes the event and decrements the stock count for the items in the order.
    *   This asynchronous approach ensures that the order placement process is fast for the user and that inventory updates are handled reliably in the background.

3.  **Database Migrations:**
    *   Uses **Alembic** to manage the `inventory` table schema, ensuring changes are version-controlled and repeatable.

## Architecture
- **Framework:** **FastAPI**
- **Database:** **PostgreSQL** (provisioned via Amazon RDS).
- **Event Bus:** **Kafka** (provisioned via Amazon MSK or self-managed EC2).
- **Deployment:** **AWS ECS Fargate**
- **Dependencies:**
    - `SQLAlchemy` & `asyncpg`: For asynchronous database operations.
    - `alembic`: For database migrations.
    - `kafka-python-ng`: For consuming events from Kafka.
    - `boto3`: To fetch database and Kafka endpoints from AWS SSM.

## Local Development

1.  Create a virtual environment: `python3 -m venv venv`
2.  Activate it: `source venv/bin/activate`
3.  Install dependencies: `pip install -r requirements.txt` and `pip install -r requirements-dev.txt`
4.  **Set Up Local Infrastructure:** This service requires PostgreSQL and Kafka.
    *   *PostgreSQL:* `docker run --name ssp-postgres-inv -e POSTGRES_PASSWORD=password -e POSTGRES_DB=ssp_inventory -p 5434:5432 -d postgres`
    *   *Kafka:* Using a docker-compose file for Kafka/Zookeeper is recommended for local dev.
5.  **Run Migrations:** Apply the database schema:
    ```bash
    alembic upgrade head
    ```
6.  Run the application:
    ```bash
    uvicorn app.main:app --reload --port 8005
    ```
