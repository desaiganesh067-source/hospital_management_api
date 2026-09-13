from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


# =========================
# User Model
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="staff", nullable=False)

    appointments = relationship(
        "Appointment",
        back_populates="created_by"
    )


# =========================
# Doctor Model
# =========================

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    available_days = Column(String(200), nullable=True)

    appointments = relationship(
        "Appointment",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )


# =========================
# Patient Model
# =========================

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    address = Column(String(255), nullable=True)
    date_of_birth = Column(String(20), nullable=True)

    appointments = relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan"
    )


# =========================
# Appointment Model
# =========================

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    created_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    appointment_time = Column(
        DateTime,
        nullable=False
    )

    reason = Column(
        String(255),
        nullable=True
    )

    status = Column(
        String(20),
        default="scheduled",
        nullable=False
    )

    # Relationships

    doctor = relationship(
        "Doctor",
        back_populates="appointments"
    )

    patient = relationship(
        "Patient",
        back_populates="appointments"
    )

    created_by = relationship(
        "User",
        back_populates="appointments"
    )