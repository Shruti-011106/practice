from sqlalchemy import Column, Integer, String, Date
from core.database import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"

# create table inventory_items(
# id int primary key index ,
# inventory_type varchar(100) not null,
# .....
# );


    id = Column(Integer, primary_key=True, index=True)

    inventory_type = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    sub_category = Column(String(100), nullable=True)

    asset_tag = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), nullable=False)

    vendor = Column(String(150), nullable=True)
    module_number = Column(String(100), nullable=True)
    serial_number = Column(String(150), nullable=True)

    configuration = Column(String(500), nullable=True)
    operating_system = Column(String(150), nullable=True)
    antivirus = Column(String(150), nullable=True)

    purchase_date = Column(Date, nullable=True)
    warranty_expiry = Column(Date, nullable=True)
    usage_year = Column(Integer, nullable=True)
    retirement_date = Column(Date, nullable=True)



