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



from core.database import db_session
from core.models import StudentModel
from sqlalchemy.orm.exc import NoResultFound

class StudentManager:
    """Manages student entities with database persistence."""
    
    def __init__(self):
        pass  # Session is handled via scoped_session
    
    def add_student(self, roll_number: str, name: str, semester: int) -> StudentModel:
        """Add a new student with validation and persistence."""
        # Validation Logic (Moved from Student class or reused)
        if not roll_number or not isinstance(roll_number, str):
            raise ValueError("Roll number must be a non-empty string")
        roll_number = roll_number.strip().upper()
        if not re.match(r'^[A-Z0-9]{4,15}$', roll_number):
            raise ValueError("Roll number must be 4-15 alphanumeric characters")
            
        if not name or not isinstance(name, str):
             raise ValueError("Name must be a non-empty string")
        name = name.strip()
        if len(name) < 2 or len(name) > 100:
             raise ValueError("Name must be between 2 and 100 characters")
             
        if not isinstance(semester, int) or semester < 1 or semester > 8:
             raise ValueError("Semester must be between 1 and 8")

        # Check existing
        existing = db_session.query(StudentModel).filter_by(roll_number=roll_number).first()
        if existing:
            raise ValueError(f"Student with roll number {roll_number} already exists")
        
        student = StudentModel(roll_number=roll_number, name=name, semester=semester)
        db_session.add(student)
        db_session.commit()
        return student
    
    def get_student(self, roll_number: str) -> Optional[StudentModel]:
        """Retrieve student by roll number."""
        return db_session.query(StudentModel).filter_by(roll_number=roll_number.strip().upper()).first()
    
    def update_student(self, roll_number: str, name: Optional[str] = None, 
                      semester: Optional[int] = None) -> StudentModel:
        """Update student attributes."""
        student = self.get_student(roll_number)
        if not student:
            raise ValueError(f"Student with roll number {roll_number} not found")
        
        if name is not None:
            if not name or len(name.strip()) < 2:
                raise ValueError("Name too short")
            student.name = name.strip()
            
        if semester is not None:
             if semester < 1 or semester > 8:
                raise ValueError("Invalid semester")
             student.semester = semester
        
        db_session.commit()
        return student
    
    def remove_student(self, roll_number: str) -> bool:
        """Remove student from system."""
        student = self.get_student(roll_number)
        if student:
            db_session.delete(student)
            db_session.commit()
            return True
        return False
    
    def get_all_students(self) -> List[StudentModel]:
        """Get all students."""
        return db_session.query(StudentModel).all()
    
    def get_students_by_semester(self, semester: int) -> List[StudentModel]:
        """Get students filtered by semester."""
        return db_session.query(StudentModel).filter_by(semester=semester).all()
    
    def student_count(self) -> int:
        """Get total number of students."""
        return db_session.query(StudentModel).count()
