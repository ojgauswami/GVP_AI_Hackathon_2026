"""
Core Intelligence Layer - Package Initialization
Makes core modules importable as a package.
"""

from .student_manager import StudentManager, Student
from .attendance_manager import AttendanceManager, AttendanceData, AttendanceRisk
from .performance_manager import PerformanceManager, PerformanceData, PerformanceCategory, PerformanceConfidence
from .ai_logic import AIInsightEngine

__all__ = [
    'StudentManager',
    'Student',
    'AttendanceManager',
    'AttendanceData',
    'AttendanceRisk',
    'PerformanceManager',
    'PerformanceData',
    'PerformanceCategory',
    'PerformanceConfidence',
    'AIInsightEngine'
]
