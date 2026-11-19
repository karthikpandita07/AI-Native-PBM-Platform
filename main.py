from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import (
    test_database_connection,
    SessionLocal,
    Member,
    Medicine,
    Pharmacy,
     Claim,
    InsurancePolicy,
    create_tables
)


app = FastAPI(
    title="AI Native PBM Platform",
    description="Pharmacy Benefit Management System",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
create_tables()


# Database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Member registration data
class MemberCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int | None = Field(default=None, ge=0, le=120)
    email: str
    insurance_id: str

    # Medicine data
class MedicineCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    generic_name: str
    manufacturer: str | None = None
    price: int = Field(ge=0)
    strength: str | None = None
    dosage_form: str | None = None
    # Pharmacy registration data
class PharmacyCreate(BaseModel):
    name: str
    address: str
    phone: str
    email: str
    license_number: str
    # Claim submission data
class ClaimCreate(BaseModel):
    member_id: int
    medicine_id: int
    pharmacy_id: int
    amount: int = Field(gt=0)
# Insurance policy creation data
class InsurancePolicyCreate(BaseModel):
    member_id: int
    policy_name: str
    coverage_limit: int = Field(gt=0)
    copay_percentage: int = Field(ge=0, le=100)
    deductible: int = Field(ge=0)

class MedicineUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    generic_name: str
    manufacturer: str | None = None
    price: int = Field(ge=0)
    strength: str | None = None
    dosage_form: str | None = None
    # Pharmacy registration data
class PharmacyCreate(BaseModel):
    name: str
    address: str
    phone: str
    email: str
    license_number: str


@app.get("/")
def home():
    return {
        "message": "Welcome to AI Native PBM Platform",
        "status": "Backend is running successfully"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/database-test")
def database_test():
    try:
        result = test_database_connection()
        return {
            "database": "connected",
            "test_result": result
        }
    except Exception as e:
        return {
            "database": "connection failed",
            "error": str(e)
        }


# Register a new member
@app.post("/members", status_code=201)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):

    new_member = Member(
        name=member.name,
        age=member.age,
        email=member.email,
        insurance_id=member.insurance_id
    )

    db.add(new_member)

    try:
        db.commit()
        db.refresh(new_member)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email or insurance ID already exists"
        )

    return {
        "message": "Member registered successfully",
        "member": {
            "id": new_member.id,
            "name": new_member.name,
            "age": new_member.age,
            "email": new_member.email,
            "insurance_id": new_member.insurance_id
        }
    }


# View all registered members
@app.get("/members")
def get_members(db: Session = Depends(get_db)):
    members = db.query(Member).all()

    return [
        {
            "id": member.id,
            "name": member.name,
            "age": member.age,
            "email": member.email,
            "insurance_id": member.insurance_id
        }
        for member in members
    ]

# Search for a member by ID
@app.get("/members/{member_id}")
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()

    if member is None:
        raise HTTPException(
            status_code=404,
            detail="Member not found"
        )

    return {
        "id": member.id,
        "name": member.name,
        "age": member.age,
        "email": member.email,
        "insurance_id": member.insurance_id
    }

# Update an existing member
class MemberUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int | None = Field(default=None, ge=0, le=120)
    email: str
    insurance_id: str


@app.put("/members/{member_id}")
def update_member(
    member_id: int,
    updated_data: MemberUpdate,
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == member_id).first()

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    member.name = updated_data.name
    member.age = updated_data.age
    member.email = updated_data.email
    member.insurance_id = updated_data.insurance_id

    try:
        db.commit()
        db.refresh(member)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email or insurance ID already exists"
        )

    return {
        "message": "Member updated successfully",
        "id": member.id,
        "name": member.name,
        "age": member.age,
        "email": member.email,
        "insurance_id": member.insurance_id
    }
# Delete a member by ID
@app.delete("/members/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()

    if member is None:
        raise HTTPException(
            status_code=404,
            detail="Member not found"
        )

    db.delete(member)
    db.commit()

    return {
        "message": "Member deleted successfully",
        "id": member_id
    }
# Add a new medicine
@app.post("/medicines", status_code=201)
def create_medicine(
    medicine: MedicineCreate,
    db: Session = Depends(get_db)
):
    new_medicine = Medicine(
    name=medicine.name,
    generic_name=medicine.generic_name,
    manufacturer=medicine.manufacturer,
    price=medicine.price,
    strength=medicine.strength,
    dosage_form=medicine.dosage_form
    )

    db.add(new_medicine)
    db.commit()
    db.refresh(new_medicine)

    return {
        "message": "Medicine added successfully",
        "medicine": {
            "id": new_medicine.id,
            "name": new_medicine.name,
            "generic_name": new_medicine.generic_name,
            "manufacturer": new_medicine.manufacturer,
            "price": new_medicine.price
        }
    }
# View all medicines
@app.get("/medicines")
def get_medicines(db: Session = Depends(get_db)):

    medicines = db.query(Medicine).all()

    return [
        {
            "id": medicine.id,
            "name": medicine.name,
            "generic_name": medicine.generic_name,
            "manufacturer": medicine.manufacturer,
            "price": medicine.price,
            "strength": medicine.strength,
            "dosage_form": medicine.dosage_form
        }
        for medicine in medicines
    ]
# Search medicine by ID
@app.get("/medicines/{medicine_id}")
def get_medicine(
    medicine_id: int,
    db: Session = Depends(get_db)
):
    medicine = db.query(Medicine).filter(
        Medicine.id == medicine_id
    ).first()

    if medicine is None:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    return {
        "id": medicine.id,
        "name": medicine.name,
        "generic_name": medicine.generic_name,
        "manufacturer": medicine.manufacturer,
        "price": medicine.price,
        "strength": medicine.strength,
        "dosage_form": medicine.dosage_form
    }
# Update an existing medicine
@app.put("/medicines/{medicine_id}")
def update_medicine(
    medicine_id: int,
    updated_data: MedicineUpdate,
    db: Session = Depends(get_db)
):
    medicine = db.query(Medicine).filter(
        Medicine.id == medicine_id
    ).first()

    if medicine is None:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    medicine.name = updated_data.name
    medicine.generic_name = updated_data.generic_name
    medicine.manufacturer = updated_data.manufacturer
    medicine.price = updated_data.price
    medicine.strength = updated_data.strength
    medicine.dosage_form = updated_data.dosage_form

    db.commit()
    db.refresh(medicine)

    return {
        "message": "Medicine updated successfully",
        "id": medicine.id,
        "name": medicine.name,
        "generic_name": medicine.generic_name,
        "manufacturer": medicine.manufacturer,
        "price": medicine.price
    }
# Delete a medicine by ID
@app.delete("/medicines/{medicine_id}")
def delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db)
):
    medicine = db.query(Medicine).filter(
        Medicine.id == medicine_id
    ).first()

    if medicine is None:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    db.delete(medicine)
    db.commit()

    return {
        "message": "Medicine deleted successfully",
        "id": medicine_id
    }
# Register a new pharmacy
@app.get("/pharmacies")
def get_pharmacies(db: Session = Depends(get_db)):
    pharmacies = db.query(Pharmacy).all()

    return [
        {
            "id": pharmacy.id,
            "name": pharmacy.name,
            "address": pharmacy.address,
            "phone": pharmacy.phone,
            "email": pharmacy.email,
            "license_number": pharmacy.license_number
        }
        for pharmacy in pharmacies
    ]
@app.post("/pharmacies", status_code=201)
def create_pharmacy(
    pharmacy: PharmacyCreate,
    db: Session = Depends(get_db)
):
    new_pharmacy = Pharmacy(
        name=pharmacy.name,
        address=pharmacy.address,
        phone=pharmacy.phone,
        email=pharmacy.email,
        license_number=pharmacy.license_number
    )

    db.add(new_pharmacy)

    try:
        db.commit()
        db.refresh(new_pharmacy)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email or license number already exists"
        )

    return {
        "message": "Pharmacy registered successfully",
        "pharmacy": {
            "id": new_pharmacy.id,
            "name": new_pharmacy.name,
            "address": new_pharmacy.address,
            "phone": new_pharmacy.phone,
            "email": new_pharmacy.email,
            "license_number": new_pharmacy.license_number
        }
    }

# Get pharmacy by ID
@app.get("/pharmacies/{pharmacy_id}")
def get_pharmacy(
    pharmacy_id: int,
    db: Session = Depends(get_db)
):
    pharmacy = db.query(Pharmacy).filter(
        Pharmacy.id == pharmacy_id
    ).first()

    if not pharmacy:
        raise HTTPException(
            status_code=404,
            detail="Pharmacy not found"
        )

    return {
        "id": pharmacy.id,
        "name": pharmacy.name,
        "address": pharmacy.address,
        "phone": pharmacy.phone,
        "email": pharmacy.email,
        "license_number": pharmacy.license_number
    }

# Update pharmacy details
@app.put("/pharmacies/{pharmacy_id}")
def update_pharmacy(
    pharmacy_id: int,
    pharmacy: PharmacyCreate,
    db: Session = Depends(get_db)
):
    existing_pharmacy = db.query(Pharmacy).filter(
        Pharmacy.id == pharmacy_id
    ).first()

    if not existing_pharmacy:
        raise HTTPException(
            status_code=404,
            detail="Pharmacy not found"
        )

    existing_pharmacy.name = pharmacy.name
    existing_pharmacy.address = pharmacy.address
    existing_pharmacy.phone = pharmacy.phone
    existing_pharmacy.email = pharmacy.email
    existing_pharmacy.license_number = pharmacy.license_number

    try:
        db.commit()
        db.refresh(existing_pharmacy)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email or license number already exists"
        )

    return {
        "message": "Pharmacy updated successfully",
        "id": existing_pharmacy.id,
        "name": existing_pharmacy.name,
        "address": existing_pharmacy.address,
        "phone": existing_pharmacy.phone,
        "email": existing_pharmacy.email,
        "license_number": existing_pharmacy.license_number
    }

# Delete pharmacy
@app.delete("/pharmacies/{pharmacy_id}")
def delete_pharmacy(
    pharmacy_id: int,
    db: Session = Depends(get_db)
):
    pharmacy = db.query(Pharmacy).filter(
        Pharmacy.id == pharmacy_id
    ).first()

    if pharmacy is None:
        raise HTTPException(
            status_code=404,
            detail="Pharmacy not found"
        )

    db.delete(pharmacy)
    db.commit()

    return {
        "message": "Pharmacy deleted successfully",
        "id": pharmacy_id
    }
# Create a new claim
@app.post("/claims")
def create_claim(
    claim_data: ClaimCreate,
    db: Session = Depends(get_db)
):
    # Validate member
    member = db.query(Member).filter(Member.id == claim_data.member_id).first()

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    # Validate medicine
    medicine = db.query(Medicine).filter(Medicine.id == claim_data.medicine_id).first()

    if medicine is None:
        raise HTTPException(status_code=404, detail="Medicine not found")

    # Validate pharmacy
    pharmacy = db.query(Pharmacy).filter(Pharmacy.id == claim_data.pharmacy_id).first()

    if pharmacy is None:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    new_claim = Claim(
        member_id=claim_data.member_id,
        medicine_id=claim_data.medicine_id,
        pharmacy_id=claim_data.pharmacy_id,
        amount=claim_data.amount
    )

    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)

    return {
        "message": "Claim submitted successfully",
        "claim_id": new_claim.id,
        "status": new_claim.status
    }
# View all claims
@app.get("/claims")
def get_all_claims(db: Session = Depends(get_db)):
    claims = db.query(Claim).all()

    return [
        {
            "id": claim.id,
            "member_id": claim.member_id,
            "medicine_id": claim.medicine_id,
            "pharmacy_id": claim.pharmacy_id,
            "amount": claim.amount,
            "status": claim.status
        }
        for claim in claims
    ]
class ClaimUpdate(BaseModel):
    status: str
    # Update claim status
@app.put("/claims/{claim_id}")
def update_claim(
    claim_id: int,
    claim_data: ClaimUpdate,
    db: Session = Depends(get_db)
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()

    if claim is None:
        return {"message": "Claim not found"}

    claim.status = claim_data.status

    db.commit()
    db.refresh(claim)

    return {
        "message": "Claim updated successfully",
        "claim_id": claim.id,
        "status": claim.status
    }
# Delete a claim
@app.delete("/claims/{claim_id}")
def delete_claim(
    claim_id: int,
    db: Session = Depends(get_db)
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()

    if claim is None:
        return {"message": "Claim not found"}

    db.delete(claim)
    db.commit()

    return {
        "message": "Claim deleted successfully",
        "claim_id": claim_id
    }
# Create a new insurance policy
@app.post("/insurance-policies")
def create_insurance_policy(
    policy_data: InsurancePolicyCreate,
    db: Session = Depends(get_db)
):
    # Check whether member exists
    member = db.query(Member).filter(
        Member.id == policy_data.member_id
    ).first()

    if member is None:
        raise HTTPException(
            status_code=404,
            detail="Member not found"
        )

    # Create insurance policy
    new_policy = InsurancePolicy(
        member_id=policy_data.member_id,
        policy_name=policy_data.policy_name,
        coverage_limit=policy_data.coverage_limit,
        copay_percentage=policy_data.copay_percentage,
        deductible=policy_data.deductible
    )

    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)

    return {
        "message": "Insurance policy created successfully",
        "policy_id": new_policy.id,
        "policy_name": new_policy.policy_name
    }
# View all insurance policies
@app.get("/insurance-policies")
def get_all_insurance_policies(db: Session = Depends(get_db)):
    policies = db.query(InsurancePolicy).all()

    return [
        {
            "id": policy.id,
            "member_id": policy.member_id,
            "policy_name": policy.policy_name,
            "coverage_limit": policy.coverage_limit,
            "copay_percentage": policy.copay_percentage,
            "deductible": policy.deductible
        }
        for policy in policies
    ]

# Adjudicate an insurance claim
@app.post("/claims/{claim_id}/adjudicate")
def adjudicate_claim(
    claim_id: int,
    db: Session = Depends(get_db)
):
    # Find the claim
    claim = db.query(Claim).filter(
        Claim.id == claim_id
    ).first()

    if claim is None:
        raise HTTPException(
            status_code=404,
            detail="Claim not found"
        )

    # Find the member's insurance policy
    policy = db.query(InsurancePolicy).filter(
        InsurancePolicy.member_id == claim.member_id
    ).first()

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail="Insurance policy not found"
        )

    # Apply remaining deductible
    remaining_deductible = max(
        0,
        policy.deductible - policy.deductible_used
    )

    deductible_applied = min(
        claim.amount,
        remaining_deductible
    )

    policy.deductible_used += deductible_applied

    eligible_amount = claim.amount - deductible_applied

    # Calculate patient's copay
    copay = round(
        eligible_amount * policy.copay_percentage / 100
    )

        # Calculate remaining insurance coverage
    remaining_coverage = max(
        0,
        policy.coverage_limit - policy.coverage_used
    )

    # Calculate insurance company's payment
    insurer_payment = min(
        eligible_amount - copay,
        remaining_coverage
    )

    # Update used insurance coverage
    policy.coverage_used += insurer_payment

    # Calculate patient's total payment
    patient_payment = claim.amount - insurer_payment

    # Update claim status
    claim.status = "Adjudicated"

    db.commit()

    return {
        "message": "Claim adjudicated successfully",
        "claim_id": claim.id,
        "total_bill": claim.amount,
        "deductible_applied": deductible_applied,
        "copay": copay,
        "insurance_payment": insurer_payment,
        "patient_payment": patient_payment,
        "claim_status": claim.status
    }

# Check a claim for possible duplicate billing
@app.get("/fraud-check/{claim_id}")
def check_claim_fraud(
    claim_id: int,
    db: Session = Depends(get_db)
):
    # Find the claim
    claim = db.query(Claim).filter(
        Claim.id == claim_id
    ).first()

    if claim is None:
        raise HTTPException(
            status_code=404,
            detail="Claim not found"
        )

    # Search for similar claims
    similar_claims = db.query(Claim).filter(
        Claim.member_id == claim.member_id,
        Claim.medicine_id == claim.medicine_id,
        Claim.pharmacy_id == claim.pharmacy_id,
        Claim.amount == claim.amount,
        Claim.id != claim.id
    ).all()

    # Check whether a possible duplicate exists
    if similar_claims:
        return {
            "claim_id": claim.id,
            "fraud_alert": True,
            "message": "Possible duplicate claim detected. Manual review required.",
            "matching_claim_ids": [
                item.id for item in similar_claims
            ]
        }

    return {
        "claim_id": claim.id,
        "fraud_alert": False,
        "message": "No matching duplicate claim found."
    }

# Find cheaper generic medicine alternatives
@app.get("/medicines/{medicine_id}/alternatives")
def get_medicine_alternatives(
    medicine_id: int,
    db: Session = Depends(get_db)
):
    # Find the original medicine
    medicine = db.query(Medicine).filter(
        Medicine.id == medicine_id
    ).first()

    if medicine is None:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    # Find medicines with the same generic name
    alternatives = db.query(Medicine).filter(
        Medicine.generic_name == medicine.generic_name,
        Medicine.id != medicine.id,
        Medicine.price < medicine.price
    ).all()

    return {
        "original_medicine": medicine.name,
        "alternatives": [
            {
                "id": item.id,
                "name": item.name,
                "generic_name": item.generic_name,
                "price": item.price,
                "savings": medicine.price - item.price
            }
            for item in alternatives
        ]
    }

# Demo drug interaction checker
@app.get("/drug-interaction-check/{medicine_id}/{other_medicine_id}")
def check_drug_interaction(
    medicine_id: int,
    other_medicine_id: int,
    db: Session = Depends(get_db)
):
    # Find both medicines
    medicine1 = db.query(Medicine).filter(
        Medicine.id == medicine_id
    ).first()

    medicine2 = db.query(Medicine).filter(
        Medicine.id == other_medicine_id
    ).first()

    if medicine1 is None or medicine2 is None:
        raise HTTPException(
            status_code=404,
            detail="One or both medicines not found"
        )

    # Sample demonstration rule
    pair = {
        medicine1.generic_name.lower(),
        medicine2.generic_name.lower()
    }

    if pair == {"aspirin", "warfarin"}:
        return {
            "medicine_1": medicine1.name,
            "medicine_2": medicine2.name,
            "interaction_found": True,
            "alert": "Potential interaction",
            "message": "Flag for pharmacist review. This is a demo rule, not clinical advice."
        }

    return {
        "medicine_1": medicine1.name,
        "medicine_2": medicine2.name,
        "interaction_found": None,
        "alert": "Not checked",
        "message": "No matching demo rule found. This does not mean the combination is safe."
    }

# PBM Dashboard - Summary
@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):

    total_members = db.query(Member).count()
    total_medicines = db.query(Medicine).count()
    total_pharmacies = db.query(Pharmacy).count()
    total_claims = db.query(Claim).count()

    pending_claims = db.query(Claim).filter(
        Claim.status == "Pending"
    ).count()

    adjudicated_claims = db.query(Claim).filter(
        Claim.status == "Adjudicated"
    ).count()

    return {
        "total_members": total_members,
        "total_medicines": total_medicines,
        "total_pharmacies": total_pharmacies,
        "total_claims": total_claims,
        "pending_claims": pending_claims,
        "adjudicated_claims": adjudicated_claims
    }
