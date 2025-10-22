from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# 1. إعداد الاتصال
DATABASE_URL = "sqlite:///./inventory_pro.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. تعريف جدول المنتج
class Product(Base):
    tablename = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    supplier = Column(String, default="")
    added_at = Column(DateTime, default=datetime.utcnow)

# 3. إنشاء الجداول في قاعدة البيانات
def create_db():
    Base.metadata.create_all(bind=engine)
