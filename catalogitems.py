from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

category1 = Category(name="Sunscreen")

session.add(category1)
session.commit()

item1 = Item(name="Watery Essence", description="my favorite cleanser",
             price="$8.99", company="Biore", category=category1)

session.add(item1)
session.commit()

category2 = Category(name="Moisturizer")

session.add(category2)
session.commit()

item2 = Item(name="First Aid Beauty Ultra Repair Cream",
             description="my favorite moisturizer",
             price="$32.00",
             company="Ulta",
             category=category2)

session.add(item2)
session.commit()

category3 = Category(name="Exfoliant")
session.add(category3)
session.commit()

item3 = Item(name="Hi Bye Vita Peel Exfoliating Scrub",
             description="this looks cool",
             price="$14.00",
             company="Banila Co",
             category=category3
             )

session.add(item3)
session.commit()

category4 = Category(name="Toner")

session.add(category4)
session.commit()

item4 = Item(name="Missha Time Revolution Clear Toner",
             description="rich and alpha and beta hydroxy acids",
             company="Missha",
             price="$15.00",
             category=category4
             )

session.add(item4)
session.commit()

category5 = Category(name="Serum")

session.add(category5)
session.commit()

item5 = Item(name="Klairs Freshly Juiced Vitamin C Serum",
             description="5% vitamin c",
             company="Klairs",
             price="$23.00",
             category=category5
             )

session.add(item5)
session.commit()

category6 = Category(name="Cleanser")

session.add(category6)
session.commit()

item6 = Item(name="First Aid Beauty Face Cleanser",
             description="my favorite cleanser",
             company="Ulta",
             price="$21.00",
             category=category6
             )

session.add(item6)
session.commit()

category7 = Category(name="Masks")

session.add(category7)
session.commit()

item7 = Item(name="Natural Gift Green Tea Pore Care Sheet Mask",
             description="hydrogel mask",
             company="Manefit",
             price="$19.99",
             category=category7
             )
