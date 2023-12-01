from sqlalchemy import Column, Integer, String
from database import Base


class Adresse(Base):
    __tablename__ = 'adressen'

    adresse_id = Column(Integer, primary_key=True, index=True)
    strasse = Column(String, index=True)
    hausnummer = Column(Integer, index=True)
    zusatz = Column(String, index=True)
    plz = Column(Integer, index=True)
    stadt = Column(String, index=True)
    land = Column(String, index=True)

