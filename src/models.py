from sqlalchemy import Column, Integer, VARCHAR, DateTime, String, func
from sqlalchemy.orm import declarative_base
from conf import engine

Base = declarative_base()

class Cars_used(Base):
    __tablename__ = 'cars_used'
    id_pk = Column(Integer, primary_key=True, autoincrement=True)
    url_uq = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    price_usd = Column(Integer, nullable=False)
    odometer = Column(Integer, nullable=False)
    username = Column(VARCHAR(56), nullable=False)
    phone_number = Column(VARCHAR(15), nullable=False)
    image_url = Column(String, nullable=False)
    images_count = Column(Integer, nullable=False)
    car_number = Column(VARCHAR(10), nullable=False)
    car_vin = Column(VARCHAR(17), nullable=False)
    datetime_found = Column(DateTime(timezone=True), default=func.now())

Base.metadata.create_all(engine)
Base.metadata.bind = engine