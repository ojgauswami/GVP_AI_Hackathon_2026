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


class PerformanceData:
    """Performance intelligence for a student."""
    
    def __init__(self, marks: float = 0.0):
        self.marks = max(0.0, min(100.0, marks))
        self._marks_history: List[float] = [self.marks] if marks > 0 else []
    
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
        if len(self._marks_history) < 2:
            return PerformanceConfidence.STABLE
        
        # Calculate variance and trend
        recent = self._marks_history[-3:] if len(self._marks_history) >= 3 else self._marks_history
        
        # Trend analysis
        if len(recent) >= 2:
            trend = recent[-1] - recent[0]
            
            # Check variance
            avg = sum(recent) / len(recent)
            variance = sum((x - avg) ** 2 for x in recent) / len(recent)
            std_dev = variance ** 0.5
            
            # High variance indicates instability
            if std_dev > 15:
                return PerformanceConfidence.UNSTABLE
            
            # Trend detection
            if trend > 10:
                return PerformanceConfidence.IMPROVING
            elif trend < -10:
                return PerformanceConfidence.DECLINING
        
        return PerformanceConfidence.STABLE
    
    def update_marks(self, marks: float):
        """Update performance with new marks."""
        marks = max(0.0, min(100.0, marks))
        self.marks = marks
        self._marks_history.append(marks)
        
        # Keep only last 5 records for trend analysis
        if len(self._marks_history) > 5:
            self._marks_history = self._marks_history[-5:]
    
    def get_trend_direction(self) -> str:
        """Get simple trend direction."""
        if len(self._marks_history) < 2:
            return "stable"
        
        trend = self._marks_history[-1] - self._marks_history[0]
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
    """Manages performance intelligence across students."""
    
    def __init__(self):
        self._performance_records: Dict[str, PerformanceData] = {}
    
    def initialize_performance(self, roll_number: str, marks: float = 0.0) -> PerformanceData:
        """Initialize performance for a student."""
        roll_number = roll_number.strip().upper()
        performance = PerformanceData(marks)
        self._performance_records[roll_number] = performance
        return performance
    
    def get_performance(self, roll_number: str) -> Optional[PerformanceData]:
        """Get performance data for student."""
        return self._performance_records.get(roll_number.strip().upper())
    
    def update_marks(self, roll_number: str, marks: float):
        """Update student marks."""
        roll_number = roll_number.strip().upper()
        if roll_number not in self._performance_records:
            self._performance_records[roll_number] = PerformanceData()
        
        self._performance_records[roll_number].update_marks(marks)
    
    def get_performance_distribution(self) -> Dict[str, int]:
        """Get distribution of students across performance categories."""
        distribution = {
            "good": 0,
            "average": 0,
            "needs_improvement": 0
        }
        
        for performance in self._performance_records.values():
            distribution[performance.category.value] += 1
        
        return distribution
    
    def get_overall_stability(self) -> Tuple[float, int, int]:
        """
        Calculate overall performance stability.
        Returns: (average_marks, unstable_count, total_count)
        """
        if not self._performance_records:
            return 0.0, 0, 0
        
        total_marks = 0.0
        unstable_count = 0
        
        for performance in self._performance_records.values():
            total_marks += performance.marks
            if performance.confidence in [PerformanceConfidence.UNSTABLE, 
                                         PerformanceConfidence.DECLINING]:
                unstable_count += 1
        
        avg_marks = total_marks / len(self._performance_records)
        return round(avg_marks, 2), unstable_count, len(self._performance_records)
    
    def get_struggling_students(self) -> List[str]:
        """Get roll numbers of students needing improvement."""
        return [
            roll_num for roll_num, performance in self._performance_records.items()
            if performance.category == PerformanceCategory.NEEDS_IMPROVEMENT
        ]
