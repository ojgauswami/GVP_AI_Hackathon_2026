"""
Performance Manager - Core Intelligence Layer
Manages academic performance intelligence with classification and confidence assessment.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum


class PerformanceCategory(Enum):
    """Performance classification categories."""
    GOOD = "good"                      # >= 75
    AVERAGE = "average"                # 50-74
    NEEDS_IMPROVEMENT = "needs_improvement"  # < 50


class PerformanceConfidence(Enum):
    """Performance confidence/stability states."""
    STABLE = "stable"        # Consistent performance
    UNSTABLE = "unstable"    # Fluctuating performance
    IMPROVING = "improving"  # Upward trend
    DECLINING = "declining"  # Downward trend



from core.database import db_session
from core.models import PerformanceModel, StudentModel
from sqlalchemy.orm.exc import NoResultFound

class PerformanceData:
    """Performance intelligence wrapper around DB model."""
    
    def __init__(self, model: PerformanceModel):
        self._model = model
    
    @property
    def marks(self) -> float:
        return self._model.marks
    
    @marks.setter
    def marks(self, value: float):
        self._model.marks = value
         
    @property
    def _marks_history(self) -> List[float]:
        # Return copy to avoid mutation issues, 
        # but locally we treat it as the source of truth
        return self._model.marks_history or []

    @_marks_history.setter
    def _marks_history(self, value: List[float]):
        self._model.marks_history = value

    @property
    def category(self) -> PerformanceCategory:
        """Classify performance based on marks."""
        if self.marks >= 75:
            return PerformanceCategory.GOOD
        elif self.marks >= 50:
            return PerformanceCategory.AVERAGE
        else:
            return PerformanceCategory.NEEDS_IMPROVEMENT
    
    @property
    def confidence(self) -> PerformanceConfidence:
        """Assess performance stability based on history."""
        history = self._marks_history
        if len(history) < 2:
            return PerformanceConfidence.STABLE
        
        # Calculate variance and trend
        recent = history[-3:] if len(history) >= 3 else history
        
        # Trend analysis
        if len(recent) >= 2:
            trend = recent[-1] - recent[0]
            
            # Check variance
            avg = sum(recent) / len(recent)
            variance = sum((x - avg) ** 2 for x in recent) / len(recent)
            std_dev = variance ** 0.5
            
            if std_dev > 15:
                return PerformanceConfidence.UNSTABLE
            
            if trend > 10:
                return PerformanceConfidence.IMPROVING
            elif trend < -10:
                return PerformanceConfidence.DECLINING
        
        return PerformanceConfidence.STABLE
    
    def update_marks(self, marks: float):
        """Update performance with new marks."""
        marks = max(0.0, min(100.0, marks))
        self.marks = marks
        
        # Update history securely
        history = list(self._marks_history)
        history.append(marks)
        
        if len(history) > 5:
            history = history[-5:]
            
        self._marks_history = history
    
    def get_trend_direction(self) -> str:
        """Get simple trend direction."""
        history = self._marks_history
        if len(history) < 2:
            return "stable"
        
        trend = history[-1] - history[0]
        if trend > 5:
            return "upward"
        elif trend < -5:
            return "downward"
        return "stable"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "marks": self.marks,
            "category": self.category.value,
            "confidence": self.confidence.value,
            "trend": self.get_trend_direction(),
            "history_size": len(self._marks_history)
        }


class PerformanceManager:
    """Manages performance intelligence across students with DB persistence."""
    
    def __init__(self):
        pass
    
    def initialize_performance(self, roll_number: str, marks: float = 0.0) -> PerformanceData:
        """Initialize performance for a student."""
        roll_number = roll_number.strip().upper()
        
        performance = db_session.query(PerformanceModel).filter_by(student_roll=roll_number).first()
        
        if not performance:
            # Init with empty history or single mark?
            history = [marks] if marks > 0 else []
            performance = PerformanceModel(student_roll=roll_number, marks=marks, marks_history=history)
            db_session.add(performance)
        else:
            performance.marks = marks
            # If re-initializing, maybe reset history? 
            # Original logic: _marks_history = [marks] if marks > 0 else []
            performance.marks_history = [marks] if marks > 0 else []
            
        db_session.commit()
        return PerformanceData(performance)
    
    def get_performance(self, roll_number: str) -> Optional[PerformanceData]:
        """Get performance data for student."""
        roll_number = roll_number.strip().upper()
        performance = db_session.query(PerformanceModel).filter_by(student_roll=roll_number).first()
        if performance:
            return PerformanceData(performance)
        return None
    
    def update_marks(self, roll_number: str, marks: float):
        """Update student marks."""
        data = self.get_performance(roll_number)
        if data:
            data.update_marks(marks)
            db_session.commit()
        else:
            self.initialize_performance(roll_number, marks)
    
    def get_performance_distribution(self) -> Dict[str, int]:
        """Get distribution of students across performance categories."""
        distribution = {
            "good": 0,
            "average": 0,
            "needs_improvement": 0
        }
        
        performances = db_session.query(PerformanceModel).all()
        for model in performances:
            data = PerformanceData(model)
            distribution[data.category.value] += 1
        
        return distribution
    
    def get_overall_stability(self) -> Tuple[float, int, int]:
        """
        Calculate overall performance stability.
        Returns: (average_marks, unstable_count, total_count)
        """
        performances = db_session.query(PerformanceModel).all()
        if not performances:
            return 0.0, 0, 0
            
        total_marks = 0.0
        unstable_count = 0
        
        for model in performances:
            data = PerformanceData(model)
            total_marks += data.marks
            if data.confidence in [PerformanceConfidence.UNSTABLE, 
                                 PerformanceConfidence.DECLINING]:
                unstable_count += 1
        
        avg_marks = total_marks / len(performances)
        return round(avg_marks, 2), unstable_count, len(performances)
    
    def get_struggling_students(self) -> List[str]:
        """Get roll numbers of students needing improvement."""
        performances = db_session.query(PerformanceModel).all()
        return [
            p.student_roll for p in performances
            if PerformanceData(p).category == PerformanceCategory.NEEDS_IMPROVEMENT
        ]
