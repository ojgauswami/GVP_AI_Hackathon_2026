"""
Attendance Manager - Core Intelligence Layer
Manages attendance intelligence with risk detection and trend analysis.
"""

from typing import Dict, Optional, Tuple
from enum import Enum


class AttendanceRisk(Enum):
    """Attendance risk states."""
    CRITICAL = "critical"  # Below 75%
    WARNING = "warning"    # 75-80%, declining trend
    STABLE = "stable"      # Above 80%, stable trend
    EXCELLENT = "excellent"  # Above 90%



from core.database import db_session
from core.models import AttendanceModel, StudentModel
from sqlalchemy.orm.exc import NoResultFound

class AttendanceData:
    """Attendance intelligence wrapper around DB model."""
    
    def __init__(self, model: AttendanceModel):
        self._model = model
    
    @property
    def total_lectures(self) -> int:
        return self._model.total_lectures
    
    @total_lectures.setter
    def total_lectures(self, value: int):
        self._model.total_lectures = value

    @property
    def attended_lectures(self) -> int:
        return self._model.attended_lectures
    
    @attended_lectures.setter
    def attended_lectures(self, value: int):
        self._model.attended_lectures = value

    @property
    def _previous_percentage(self) -> Optional[float]:
        return self._model.previous_percentage

    @_previous_percentage.setter
    def _previous_percentage(self, value: float):
        self._model.previous_percentage = value

    @property
    def attendance_percentage(self) -> float:
        """Calculate attendance percentage."""
        if self.total_lectures == 0:
            return 0.0
        return round((self.attended_lectures / self.total_lectures) * 100, 2)
    
    @property
    def risk_level(self) -> AttendanceRisk:
        """Determine risk level based on percentage and trend."""
        percentage = self.attendance_percentage
        
        if percentage < 75:
            return AttendanceRisk.CRITICAL
        
        if self._previous_percentage is not None:
            trend = percentage - self._previous_percentage
            if percentage < 80 and trend < 0:
                return AttendanceRisk.WARNING
        
        if percentage >= 90:
            return AttendanceRisk.EXCELLENT
        
        return AttendanceRisk.STABLE
    
    @property
    def is_at_risk(self) -> bool:
        """Check if student is at attendance risk."""
        return self.risk_level in [AttendanceRisk.CRITICAL, AttendanceRisk.WARNING]
    
    def update_attendance(self, attended: bool):
        """Update attendance record."""
        self._previous_percentage = self.attendance_percentage
        self.total_lectures += 1
        if attended:
            self.attended_lectures += 1
    
    def set_attendance(self, total: int, attended: int):
        """Set attendance data directly."""
        self._previous_percentage = self.attendance_percentage
        self.total_lectures = max(0, total)
        self.attended_lectures = max(0, min(attended, total))
    
    def lectures_needed_for_threshold(self, threshold: float = 75.0) -> int:
        """Calculate lectures needed to reach threshold."""
        if self.attendance_percentage >= threshold:
            return 0
        
        numerator = threshold * self.total_lectures - 100 * self.attended_lectures
        denominator = 100 - threshold
        
        if denominator == 0:
            return -1
        
        needed = numerator / denominator
        return max(0, int(needed) + 1)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "total_lectures": self.total_lectures,
            "attended_lectures": self.attended_lectures,
            "attendance_percentage": self.attendance_percentage,
            "risk_level": self.risk_level.value,
            "is_at_risk": self.is_at_risk,
            "lectures_needed": self.lectures_needed_for_threshold()
        }


class AttendanceManager:
    """Manages attendance intelligence across students with DB persistence."""
    
    def __init__(self):
        pass
    
    def initialize_attendance(self, roll_number: str, 
                            total: int = 0, attended: int = 0) -> AttendanceData:
        """Initialize attendance for a student."""
        roll_number = roll_number.strip().upper()
        
        # Check if exists
        attendance = db_session.query(AttendanceModel).filter_by(student_roll=roll_number).first()
        if not attendance:
            attendance = AttendanceModel(student_roll=roll_number, total_lectures=total, attended_lectures=attended)
            db_session.add(attendance)
        else:
            attendance.total_lectures = total
            attendance.attended_lectures = attended
            
        db_session.commit()
        return AttendanceData(attendance)
    
    def get_attendance(self, roll_number: str) -> Optional[AttendanceData]:
        """Get attendance data for student."""
        roll_number = roll_number.strip().upper()
        attendance = db_session.query(AttendanceModel).filter_by(student_roll=roll_number).first()
        if attendance:
            return AttendanceData(attendance)
        return None
    
    def update_attendance(self, roll_number: str, attended: bool):
        """Update attendance record."""
        data = self.get_attendance(roll_number)
        if data:
            data.update_attendance(attended)
            db_session.commit()
        else:
             # Create new if missing? Usually initialize should be called first.
             # But let's support lazy creation
             self.initialize_attendance(roll_number, total=0, attended=0)
             self.update_attendance(roll_number, attended)

    def set_attendance(self, roll_number: str, total: int, attended: int):
        """Set attendance data directly."""
        data = self.get_attendance(roll_number)
        if data:
            data.set_attendance(total, attended)
            db_session.commit()
        else:
            self.initialize_attendance(roll_number, total, attended)
    
    def get_overall_health(self) -> Tuple[float, int, int]:
        """
        Calculate overall attendance health across all students.
        """
        attendances = db_session.query(AttendanceModel).all()
        if not attendances:
            return 0.0, 0, 0
            
        total_percentage = 0.0
        at_risk_count = 0
        
        for model in attendances:
            data = AttendanceData(model)
            total_percentage += data.attendance_percentage
            if data.is_at_risk:
                at_risk_count += 1
        
        avg_percentage = total_percentage / len(attendances)
        return round(avg_percentage, 2), at_risk_count, len(attendances)
    
    def get_at_risk_students(self) -> list:
        """Get list of roll numbers for at-risk students."""
        attendances = db_session.query(AttendanceModel).all()
        return [
            a.student_roll for a in attendances
            if AttendanceData(a).is_at_risk
        ]
