from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Patient, User
from app.schemas import PatientCreate, PatientResponse


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


# =========================================================
# CREATE PATIENT
# =========================================================

@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new patient.
    Any logged-in user can create a patient.
    """

    # Check email if provided
    if patient_data.email:
        existing_patient = (
            db.query(Patient)
            .filter(Patient.email == patient_data.email)
            .first()
        )

        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this email already exists"
            )

    # Create patient
    new_patient = Patient(
        name=patient_data.name,
        age=patient_data.age,
        gender=patient_data.gender,
        phone=patient_data.phone,
        email=patient_data.email,
        address=patient_data.address,
        date_of_birth=patient_data.date_of_birth
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


# =========================================================
# GET ALL PATIENTS
# =========================================================

@router.get(
    "/",
    response_model=list[PatientResponse]
)
def get_patients(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all patients with pagination.
    """

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be greater than 0"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100"
        )

    offset = (page - 1) * limit

    patients = (
        db.query(Patient)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return patients


# =========================================================
# GET SINGLE PATIENT
# =========================================================

@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get one patient by ID.
    """

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient


# =========================================================
# UPDATE PATIENT
# =========================================================

@router.put(
    "/{patient_id}",
    response_model=PatientResponse
)
def update_patient(
    patient_id: int,
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing patient.
    """

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # Check email belongs to another patient
    if patient_data.email:
        existing_patient = (
            db.query(Patient)
            .filter(
                Patient.email == patient_data.email,
                Patient.id != patient_id
            )
            .first()
        )

        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another patient already uses this email"
            )

    patient.name = patient_data.name
    patient.age = patient_data.age
    patient.gender = patient_data.gender
    patient.phone = patient_data.phone
    patient.email = patient_data.email
    patient.address = patient_data.address
    patient.date_of_birth = patient_data.date_of_birth

    db.commit()
    db.refresh(patient)

    return patient


# =========================================================
# DELETE PATIENT
# =========================================================

@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a patient.
    Only admin users can delete patients.
    """

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    db.delete(patient)
    db.commit()

    return None