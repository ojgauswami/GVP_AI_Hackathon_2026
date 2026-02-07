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


class AttendanceData:
    """Attendance intelligence for a student."""
    
    def __init__(self, total_lectures: int = 0, attended_lectures: int = 0):
        self.total_lectures = max(0, total_lectures)
        self.attended_lectures = max(0, min(attended_lectures, total_lectures))
        self._previous_percentage = None
    
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
        
        # Trend analysis
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
        
        # Calculate: (attended + x) / (total + x) >= threshold/100
        # Solving: x >= (threshold * total - 100 * attended) / (100 - threshold)
        numerator = threshold * self.total_lectures - 100 * self.attended_lectures
        denominator = 100 - threshold
        
        if denominator == 0:
            return -1  # Impossible
        
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
    """Manages attendance intelligence across students."""
    
    def __init__(self):
        self._attendance_records: Dict[str, AttendanceData] = {}
    
    def initialize_attendance(self, roll_number: str, 
                            total: int = 0, attended: int = 0) -> AttendanceData:
        """Initialize attendance for a student."""
        roll_number = roll_number.strip().upper()
        attendance = AttendanceData(total, attended)
        self._attendance_records[roll_number] = attendance
        return attendance
    
    def get_attendance(self, roll_number: str) -> Optional[AttendanceData]:
        """Get attendance data for student."""
        return self._attendance_records.get(roll_number.strip().upper())
    
    def update_attendance(self, roll_number: str, attended: bool):
        """Update attendance record."""
        roll_number = roll_number.strip().upper()
        if roll_number not in self._attendance_records:
            self._attendance_records[roll_number] = AttendanceData()
        
        self._attendance_records[roll_number].update_attendance(attended)
    
    def set_attendance(self, roll_number: str, total: int, attended: int):
        """Set attendance data directly."""
        roll_number = roll_number.strip().upper()
        if roll_number not in self._attendance_records:
            self._attendance_records[roll_number] = AttendanceData()
        
        self._attendance_records[roll_number].set_attendance(total, attended)
    
    def get_overall_health(self) -> Tuple[float, int, int]:
        """
        Calculate overall attendance health across all students.
        Returns: (average_percentage, at_risk_count, total_count)
        """
        if not self._attendance_records:
            return 0.0, 0, 0
        
        total_percentage = 0.0
        at_risk_count = 0
        
        for attendance in self._attendance_records.values():
            total_percentage += attendance.attendance_percentage
            if attendance.is_at_risk:
                at_risk_count += 1
        
        avg_percentage = total_percentage / len(self._attendance_records)
        return round(avg_percentage, 2), at_risk_count, len(self._attendance_records)
    
    def get_at_risk_students(self) -> list:
        """Get list of roll numbers for at-risk students."""
        return [
            roll_num for roll_num, attendance in self._attendance_records.items()
            if attendance.is_at_risk
        ]
