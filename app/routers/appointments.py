from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Appointment, Doctor, Patient, User
from app.schemas import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate,
)


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


# =========================================================
# CREATE APPOINTMENT
# =========================================================

@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new appointment.
    Any logged-in user can create an appointment.
    """

    # -----------------------------------------------------
    # Check doctor exists
    # -----------------------------------------------------

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == appointment_data.doctor_id)
        .first()
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    # -----------------------------------------------------
    # Check patient exists
    # -----------------------------------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == appointment_data.patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # -----------------------------------------------------
    # Check doctor appointment conflict
    # -----------------------------------------------------

    existing_appointment = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == appointment_data.doctor_id,
            Appointment.appointment_time
            == appointment_data.appointment_time,
            Appointment.status == "scheduled"
        )
        .first()
    )

    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor already has an appointment at this time"
        )

    # -----------------------------------------------------
    # Create appointment
    # -----------------------------------------------------

    new_appointment = Appointment(
        doctor_id=appointment_data.doctor_id,
        patient_id=appointment_data.patient_id,
        created_by_id=current_user.id,
        appointment_time=appointment_data.appointment_time,
        reason=appointment_data.reason,
        status="scheduled"
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment


# =========================================================
# GET ALL APPOINTMENTS
# =========================================================

@router.get(
    "/",
    response_model=list[AppointmentResponse]
)
def get_appointments(
    page: int = 1,
    limit: int = 10,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get appointments with pagination and optional status filter.
    """

    # Validate page
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be greater than 0"
        )

    # Validate limit
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100"
        )

    # Base query
    query = db.query(Appointment)

    # Optional status filter
    if status_filter:
        allowed_statuses = [
            "scheduled",
            "completed",
            "cancelled"
        ]

        if status_filter not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid status. Use scheduled, "
                    "completed or cancelled"
                )
            )

        query = query.filter(
            Appointment.status == status_filter
        )

    # Pagination
    offset = (page - 1) * limit

    appointments = (
        query
        .order_by(Appointment.appointment_time)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return appointments


# =========================================================
# GET SINGLE APPOINTMENT
# =========================================================

@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get one appointment by ID.
    """

    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    return appointment


# =========================================================
# UPDATE APPOINTMENT STATUS
# =========================================================

@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse
)
def update_appointment_status(
    appointment_id: int,
    status_data: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update appointment status.
    """

    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    appointment.status = status_data.status

    db.commit()
    db.refresh(appointment)

    return appointment


# =========================================================
# DELETE APPOINTMENT
# =========================================================

@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete an appointment.
    Only admin users can delete appointments.
    """

    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    db.delete(appointment)
    db.commit()

    return None