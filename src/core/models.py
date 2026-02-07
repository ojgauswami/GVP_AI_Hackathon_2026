from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class StudentModel(Base):
    __tablename__ = "students"

    roll_number = Column(String(15), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    semester = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    attendance = relationship("AttendanceModel", back_populates="student", uselist=False, cascade="all, delete-orphan")
    performance = relationship("PerformanceModel", back_populates="student", uselist=False, cascade="all, delete-orphan")
    risk_state = Column(String(20), default="stable")

    def to_dict(self):
        return {
            "roll_number": self.roll_number,
            "name": self.name,
            "semester": self.semester,
            "risk_state": self.risk_state,
            "attendance_data": self.attendance.to_dict() if self.attendance else None,
            "performance_data": self.performance.to_dict() if self.performance else None
        }

class AttendanceModel(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_roll = Column(String(15), ForeignKey("students.roll_number"), unique=True)
    total_lectures = Column(Integer, default=0)
    attended_lectures = Column(Integer, default=0)
    previous_percentage = Column(Float, nullable=True)
    
    student = relationship("StudentModel", back_populates="attendance")

    def to_dict(self):
        return {
            "total_lectures": self.total_lectures,
            "attended_lectures": self.attended_lectures,
            "attendance_percentage": round((self.attended_lectures / self.total_lectures * 100), 1) if self.total_lectures > 0 else 0
        }

class PerformanceModel(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)
    student_roll = Column(String(15), ForeignKey("students.roll_number"), unique=True)
    marks = Column(Float, default=0.0)
    marks_history = Column(JSON, default=list)
    
    student = relationship("StudentModel", back_populates="performance")

    def to_dict(self):
        return {
            "marks": self.marks,
            "history": self.marks_history
        }
