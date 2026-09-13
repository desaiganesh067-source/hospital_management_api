from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Doctor, User
from app.schemas import DoctorCreate, DoctorResponse


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


# =========================================================
# CREATE DOCTOR
# =========================================================

@router.post(
    "/",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED
)
def create_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new doctor.
    Only admin users can create doctors.
    """

    # Check whether email already exists
    existing_doctor = (
        db.query(Doctor)
        .filter(Doctor.email == doctor_data.email)
        .first()
    )

    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor with this email already exists"
        )

    # Create doctor
    new_doctor = Doctor(
        name=doctor_data.name,
        specialization=doctor_data.specialization,
        phone=doctor_data.phone,
        email=doctor_data.email,
        available_days=doctor_data.available_days
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor


# =========================================================
# GET ALL DOCTORS
# =========================================================

@router.get(
    "/",
    response_model=list[DoctorResponse]
)
def get_doctors(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all doctors with pagination.
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

    doctors = (
        db.query(Doctor)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return doctors


# =========================================================
# GET SINGLE DOCTOR
# =========================================================

@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get one doctor by ID.
    """

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return doctor


# =========================================================
# UPDATE DOCTOR
# =========================================================

@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def update_doctor(
    doctor_id: int,
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update an existing doctor.
    Only admin users can update doctors.
    """

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    # Check email belongs to another doctor
    existing_doctor = (
        db.query(Doctor)
        .filter(
            Doctor.email == doctor_data.email,
            Doctor.id != doctor_id
        )
        .first()
    )

    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Another doctor already uses this email"
        )

    doctor.name = doctor_data.name
    doctor.specialization = doctor_data.specialization
    doctor.phone = doctor_data.phone
    doctor.email = doctor_data.email
    doctor.available_days = doctor_data.available_days

    db.commit()
    db.refresh(doctor)

    return doctor


# =========================================================
# DELETE DOCTOR
# =========================================================

@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a doctor.
    Only admin users can delete doctors.
    """

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    db.delete(doctor)
    db.commit()

    return None