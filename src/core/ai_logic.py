"""
AI Logic - Core Intelligence Layer
Deterministic reasoning engine for generating calm, intelligent insights.
"""

from typing import Dict, List, Optional
from .student_manager import Student
from .attendance_manager import AttendanceData, AttendanceRisk
from .performance_manager import PerformanceData, PerformanceCategory, PerformanceConfidence


class AIInsightEngine:
    """
    Generates explainable, rule-based insights.
    Not a model. Not an API. Pure reasoning.
    """
    
    @staticmethod
    def generate_student_insight(student: Student, 
                                 attendance: Optional[AttendanceData],
                                 performance: Optional[PerformanceData]) -> str:
        """
        Generate calm, intelligent narrative insight for a student.
        Speaks only when necessary.
        """
        insights = []
        
        # Attendance reasoning
        if attendance and attendance.total_lectures > 0:
            att_insight = AIInsightEngine._reason_attendance(attendance)
            if att_insight:
                insights.append(att_insight)
        
        # Performance reasoning
        if performance and performance.marks > 0:
            perf_insight = AIInsightEngine._reason_performance(performance)
            if perf_insight:
                insights.append(perf_insight)
        
        # Combined reasoning
        if attendance and performance and attendance.total_lectures > 0 and performance.marks > 0:
            combined = AIInsightEngine._reason_combined(attendance, performance)
            if combined:
                insights.append(combined)
        
        # Return primary insight or silence
        if not insights:
            return "Insufficient data for assessment."
        
        return insights[0]  # Most critical insight only
    
    @staticmethod
    def _reason_attendance(attendance: AttendanceData) -> Optional[str]:
        """Attendance-specific reasoning."""
        risk = attendance.risk_level
        percentage = attendance.attendance_percentage
        
        if risk == AttendanceRisk.CRITICAL:
            needed = attendance.lectures_needed_for_threshold()
            if needed > 20:
                return "Attendance recovery requires immediate intervention."
            elif needed > 0:
                return f"Attendance is below threshold. Recovery requires {needed} consecutive sessions."
            
        elif risk == AttendanceRisk.WARNING:
            return "Attendance trajectory indicates intervention may be required."
        
        elif risk == AttendanceRisk.EXCELLENT:
            return None  # Silence for excellence
        
        return None
    
    @staticmethod
    def _reason_performance(performance: PerformanceData) -> Optional[str]:
        """Performance-specific reasoning."""
        category = performance.category
        confidence = performance.confidence
        
        if category == PerformanceCategory.NEEDS_IMPROVEMENT:
            if confidence == PerformanceConfidence.DECLINING:
                return "Performance requires intervention. Declining pattern observed."
            return "Performance is below threshold. Intervention recommended."
        
        elif category == PerformanceCategory.AVERAGE:
            if confidence == PerformanceConfidence.UNSTABLE:
                return "Performance stability requires attention."
            elif confidence == PerformanceConfidence.IMPROVING:
                return None  # Quiet encouragement through silence
        
        elif category == PerformanceCategory.GOOD:
            if confidence == PerformanceConfidence.DECLINING:
                return "Performance is adequate. Recent decline requires monitoring."
        
        return None
    
    @staticmethod
    def _reason_combined(attendance: AttendanceData, performance: PerformanceData) -> Optional[str]:
        """Cross-domain reasoning."""
        # Both critical
        if attendance.is_at_risk and performance.category == PerformanceCategory.NEEDS_IMPROVEMENT:
            return "Multiple factors require intervention."
        
        # Attendance risk overriding good performance
        if attendance.risk_level == AttendanceRisk.CRITICAL and \
           performance.category == PerformanceCategory.GOOD:
            return "Performance is adequate. Attendance requires attention."
        
        # Performance risk despite good attendance
        if not attendance.is_at_risk and \
           performance.category == PerformanceCategory.NEEDS_IMPROVEMENT:
            return "Attendance is satisfactory. Learning outcomes require intervention."
        
        return None
    
    @staticmethod
    def generate_system_insight(total_students: int,
                               attendance_health: float,
                               at_risk_count: int,
                               avg_performance: float,
                               unstable_count: int) -> List[str]:
        """
        Generate system-level insights.
        Maximum 2 insights. Calm. Intentional.
        """
        insights = []
        
        # Attendance system reasoning
        if total_students > 0:
            risk_percentage = (at_risk_count / total_students) * 100
            
            if risk_percentage > 30:
                insights.append(f"Attendance intervention is required across {risk_percentage:.0f}% of cohort.")
            elif attendance_health < 80:
                insights.append("Attendance levels are below institutional threshold.")
        
        # Performance system reasoning
        if total_students > 0 and unstable_count > 0:
            instability_rate = (unstable_count / total_students) * 100
            
            if instability_rate > 25:
                insights.append("Performance stability requires systemic review.")
        
        # System health
        if not insights:
            if attendance_health >= 85 and avg_performance >= 70:
                return ["Academic metrics are within threshold."]
            else:
                return ["Monitoring active."]
        
        return insights[:2]  # Maximum 2 insights
    
    @staticmethod
    def calculate_risk_score(attendance: Optional[AttendanceData],
                           performance: Optional[PerformanceData]) -> int:
        """
        Calculate composite risk score (0-100).
        Higher score = higher risk.
        """
        score = 0
        
        if attendance:
            # Attendance component (0-50)
            att_percentage = attendance.attendance_percentage
            if att_percentage < 75:
                score += 50
            elif att_percentage < 80:
                score += 30
            elif att_percentage < 85:
                score += 15
        
        if performance:
            # Performance component (0-50)
            marks = performance.marks
            if marks < 40:
                score += 50
            elif marks < 50:
                score += 35
            elif marks < 60:
                score += 20
            elif marks < 70:
                score += 10
            
            # Confidence modifier
            if performance.confidence == PerformanceConfidence.DECLINING:
                score += 10
            elif performance.confidence == PerformanceConfidence.UNSTABLE:
                score += 5
        
        return min(100, score)
    
    @staticmethod
    def determine_risk_state(risk_score: int) -> str:
        """Convert risk score to state."""
        if risk_score >= 70:
            return "critical"
        elif risk_score >= 40:
            return "warning"
        else:
            return "stable"
