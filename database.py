from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = (
    "postgresql+psycopg://"
    "pbm_user:pbm_dev_password_123"
    "@localhost:5432/pbm_database"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
from sqlalchemy import Column, Integer, String

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    email = Column(String, unique=True, nullable=False)
    insurance_id = Column(String, unique=True, nullable=False)


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    generic_name = Column(String, nullable=False)
    manufacturer = Column(String)
    price = Column(Integer)
    strength = Column(String, nullable=True)
    dosage_form = Column(String, nullable=True)

    
def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar()

    # Pharmacy database model
class Pharmacy(Base):
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    license_number = Column(String, unique=True, nullable=False)

    # Claims database model
class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, nullable=False)
    medicine_id = Column(Integer, nullable=False)
    pharmacy_id = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default="Pending")

# Insurance Policy database model
class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, nullable=False)
    policy_name = Column(String, nullable=False)
    coverage_limit = Column(Integer, nullable=False)
    copay_percentage = Column(Integer, nullable=False)
    deductible = Column(Integer, nullable=False)
    deductible_used = Column(Integer, nullable=False, default=0)
    coverage_used = Column(Integer, nullable=False, default=0)
def create_tables():
    Base.metadata.create_all(bind=engine)