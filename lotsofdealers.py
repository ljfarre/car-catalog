from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Dealership, Base, Car, User

engine = create_engine('sqlite:///cardealerships.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Lee Farretta", email="ljfarre@pacbell.net",
             picture="/static/images/lees-pic.png")
session.add(User1)
session.commit()

# Inventory for Marin Classic Mercedes
dealership1 = Dealership(user_id=1, name="Marin Classic Mercedes", address="23 Industrial Way Greenbrae 94904", phone="415-456-2341")

session.add(dealership1)
session.commit()

Car1 = Car(user_id=1, name="190", brand="Mercedes", year="1961", color="Maroon", description="UP FOR SALE IS A VERY BEAUTIFUL CLASSIC 1961 MERCEDES 190D PONTON.",
                     price="$8,999", type="Sedan", dealership=dealership1)

session.add(Car1)
session.commit()

# Inventory for San Francisco Classics
dealership2 = Dealership(user_id=1, name="San Francisco Classics", address="23 Vanness Ave, San Francisco 94132", phone="415-585-2341")

session.add(dealership2)
session.commit()

Car1 = Car(user_id=1, name="Bel Air", brand="Chevrolet", year="1957", color="Red and White", description="This 1957 Chevrolet Bel Air Convertible represents an excellent example of what is indeed the quintessential American Classic Automobile.",
                     price="$96,000", type="Coupe", dealership=dealership2)

session.add(Car1)
session.commit()

# Inventory for Walnut Creek Oldies
dealership3 = Dealership(user_id=1, name="Walnut Creek Oldies", address="2200 North Main Street, Walnut Creek 94596", phone="925-935-2341")

session.add(dealership3)
session.commit()

Car1 = Car(user_id=1, name="Testa Rossa", brand="Ferrari", year="1957", color="Red", description="The Ferrari TR, or 250 Testa Rossa, is a race car model built by Ferrari in the 1950s and 1960s. They were introduced at the end of the 1957 season in preparation for the regulations restricting sports cars to 3 litres for Le Mans and World Sports Car Championship races from 1958.",
                     price="$15,000,000", type="Sports Car", dealership=dealership3)

session.add(Car1)
session.commit()


print "Added Cars to dealership inventories!"
