"""
Student Manager - Core Intelligence Layer
Manages student entities with validation and integrity.
"""

import re
from typing import Dict, List, Optional


class Student:
    """Student entity with validated attributes."""
    
    def __init__(self, roll_number: str, name: str, semester: int):
        self.roll_number = self._validate_roll_number(roll_number)
        self.name = self._validate_name(name)
        self.semester = self._validate_semester(semester)
        self.attendance_data = None
        self.performance_data = None
        self.risk_state = "stable"
    
    @staticmethod
    def _validate_roll_number(roll_number: str) -> str:
        """Validate roll number format."""
        if not roll_number or not isinstance(roll_number, str):
            raise ValueError("Roll number must be a non-empty string")
        
        roll_number = roll_number.strip().upper()
        if not re.match(r'^[A-Z0-9]{4,15}$', roll_number):
            raise ValueError("Roll number must be 4-15 alphanumeric characters")
        
        return roll_number
    
    @staticmethod
    def _validate_name(name: str) -> str:
        """Validate student name."""
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        
        name = name.strip()
        if len(name) < 2 or len(name) > 100:
            raise ValueError("Name must be between 2 and 100 characters")
        
        return name
    
    @staticmethod
    def _validate_semester(semester: int) -> int:
        """Validate semester number."""
        if not isinstance(semester, int):
            raise ValueError("Semester must be an integer")
        
        if semester < 1 or semester > 8:
            raise ValueError("Semester must be between 1 and 8")
        
        return semester
    
    def to_dict(self) -> Dict:
        """Convert student to dictionary."""
        return {
            "roll_number": self.roll_number,
            "name": self.name,
            "semester": self.semester,
            "attendance_data": self.attendance_data,
            "performance_data": self.performance_data,
            "risk_state": self.risk_state
        }


class StudentManager:
    """Manages student entities with uniqueness constraints."""
    
    def __init__(self):
        self._students: Dict[str, Student] = {}
    
    def add_student(self, roll_number: str, name: str, semester: int) -> Student:
        """Add a new student with validation."""
        student = Student(roll_number, name, semester)
        
        if student.roll_number in self._students:
            raise ValueError(f"Student with roll number {student.roll_number} already exists")
        
        self._students[student.roll_number] = student
        return student
    
    def get_student(self, roll_number: str) -> Optional[Student]:
        """Retrieve student by roll number."""
        return self._students.get(roll_number.strip().upper())
    
    def update_student(self, roll_number: str, name: Optional[str] = None, 
                      semester: Optional[int] = None) -> Student:
        """Update student attributes."""
        student = self.get_student(roll_number)
        if not student:
            raise ValueError(f"Student with roll number {roll_number} not found")
        
        if name is not None:
            student.name = Student._validate_name(name)
        if semester is not None:
            student.semester = Student._validate_semester(semester)
        
        return student
    
    def remove_student(self, roll_number: str) -> bool:
        """Remove student from system."""
        roll_number = roll_number.strip().upper()
        if roll_number in self._students:
            del self._students[roll_number]
            return True
        return False
    
    def get_all_students(self) -> List[Student]:
        """Get all students."""
        return list(self._students.values())
    
    def get_students_by_semester(self, semester: int) -> List[Student]:
        """Get students filtered by semester."""
        return [s for s in self._students.values() if s.semester == semester]
    
    def student_count(self) -> int:
        """Get total number of students."""
        return len(self._students)
