from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(15), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    bookings = relationship("Booking", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(name='{self.name}', email='{self.email}')>"

class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False)
    booking_type = Column(String(100), nullable=False)
    date = Column(String(20), nullable=False)
    time = Column(String(10), nullable=False)
    status = Column(String(20), default='confirmed')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    customer = relationship("Customer", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking(id={self.id}, type='{self.booking_type}', date='{self.date}')>"

# Database initialization
def init_db():
    """Initialize database and create tables"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get database session"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()