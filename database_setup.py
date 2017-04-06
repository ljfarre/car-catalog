from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Dealership(Base):
    __tablename__ = 'dealership'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    address = Column(String(250), nullable=False)
    phone = Column(String(15), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'address' : self.address,
            'phone' : self.phone,
        }


class Car(Base):
    __tablename__ = 'car'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    brand = Column(String(50))
    year = Column(String(4))
    color = Column(String(50))
    description = Column(String(250))
    price = Column(String(10))
    type = Column(String(250))
    dealership_id = Column(Integer, ForeignKey('dealership.id'))
    dealership = relationship(Dealership)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'brand': self.brand,
            'year': self.year,
            'color': self.color,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'type': self.type,
        }


engine = create_engine('sqlite:///cardealerships.db')


Base.metadata.create_all(engine)
