from sqlalchemy import Column, String, Integer
from ..core.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    product_id = Column(String, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False, default=0)
