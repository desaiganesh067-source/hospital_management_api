from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# =========================================================
# USER SCHEMAS
# =========================================================

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    role: str = Field(default="staff", pattern="^(admin|staff)$")


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# =========================================================
# DOCTOR SCHEMAS
# =========================================================

class DoctorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    specialization: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=10, max_length=20)
    email: EmailStr
    available_days: str | None = None


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    phone: str
    email: EmailStr
    available_days: str | None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# PATIENT SCHEMAS
# =========================================================

class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(gt=0, le=120)
    gender: str = Field(min_length=1, max_length=20)
    phone: str = Field(min_length=10, max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    date_of_birth: str | None = None


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    phone: str
    email: EmailStr | None
    address: str | None
    date_of_birth: str | None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# APPOINTMENT SCHEMAS
# =========================================================

class AppointmentCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    patient_id: int = Field(gt=0)
    appointment_time: datetime
    reason: str | None = Field(default=None, max_length=255)


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    created_by_id: int
    appointment_time: datetime
    reason: str | None
    status: str

    model_config = ConfigDict(from_attributes=True)


class AppointmentStatusUpdate(BaseModel):
    status: str = Field(
        pattern="^(scheduled|completed|cancelled)$"
    )