"""
Academic Intelligence Engine - Orchestration Layer
Flask application serving as minimal bridge between intelligence and interface.
"""

from flask import Flask, render_template, request, jsonify
from core.student_manager import StudentManager
from core.attendance_manager import AttendanceManager
from core.performance_manager import PerformanceManager
from core.ai_logic import AIInsightEngine

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Core intelligence instances
student_manager = StudentManager()
attendance_manager = AttendanceManager()
performance_manager = PerformanceManager()
ai_engine = AIInsightEngine()


@app.route('/')
def index():
    """Main intelligence interface."""
    return render_template('dashboard.html')


@app.route('/api/students', methods=['GET'])
def get_students():
    """Retrieve all students with intelligence data."""
    students = student_manager.get_all_students()
    
    students_data = []
    for student in students:
        attendance = attendance_manager.get_attendance(student.roll_number)
        performance = performance_manager.get_performance(student.roll_number)
        
        # Generate AI insight
        insight = ai_engine.generate_student_insight(student, attendance, performance)
        risk_score = ai_engine.calculate_risk_score(attendance, performance)
        risk_state = ai_engine.determine_risk_state(risk_score)
        
        student_dict = student.to_dict()
        student_dict['attendance'] = attendance.to_dict() if attendance else None
        student_dict['performance'] = performance.to_dict() if performance else None
        student_dict['ai_insight'] = insight
        student_dict['risk_score'] = risk_score
        student_dict['risk_state'] = risk_state
        
        students_data.append(student_dict)
    
    return jsonify(students_data)


@app.route('/api/students', methods=['POST'])
def add_student():
    """Add new student with validation."""
    try:
        data = request.get_json()
        
        roll_number = data.get('roll_number')
        name = data.get('name')
        semester = data.get('semester')
        
        if not all([roll_number, name, semester]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create student
        student = student_manager.add_student(roll_number, name, int(semester))
        
        # Initialize attendance and performance
        total_lectures = data.get('total_lectures', 0)
        attended_lectures = data.get('attended_lectures', 0)
        marks = data.get('marks', 0)
        
        attendance = attendance_manager.initialize_attendance(
            student.roll_number, 
            int(total_lectures), 
            int(attended_lectures)
        )
        
        performance = performance_manager.initialize_performance(
            student.roll_number,
            float(marks)
        )
        
        # Generate insight
        insight = ai_engine.generate_student_insight(student, attendance, performance)
        risk_score = ai_engine.calculate_risk_score(attendance, performance)
        risk_state = ai_engine.determine_risk_state(risk_score)
        
        response = student.to_dict()
        response['attendance'] = attendance.to_dict()
        response['performance'] = performance.to_dict()
        response['ai_insight'] = insight
        response['risk_score'] = risk_score
        response['risk_state'] = risk_state
        
        return jsonify(response), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal error'}), 500


@app.route('/api/students/<roll_number>', methods=['PUT'])
def update_student(roll_number):
    """Update student data."""
    try:
        data = request.get_json()
        
        student = student_manager.get_student(roll_number)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Update basic info if provided
        if 'name' in data or 'semester' in data:
            student_manager.update_student(
                roll_number,
                name=data.get('name'),
                semester=data.get('semester')
            )
        
        # Update attendance if provided
        if 'total_lectures' in data and 'attended_lectures' in data:
            attendance_manager.set_attendance(
                roll_number,
                int(data['total_lectures']),
                int(data['attended_lectures'])
            )
        
        # Update performance if provided
        if 'marks' in data:
            performance_manager.update_marks(roll_number, float(data['marks']))
        
        # Retrieve updated data
        attendance = attendance_manager.get_attendance(roll_number)
        performance = performance_manager.get_performance(roll_number)
        
        insight = ai_engine.generate_student_insight(student, attendance, performance)
        risk_score = ai_engine.calculate_risk_score(attendance, performance)
        risk_state = ai_engine.determine_risk_state(risk_score)
        
        response = student.to_dict()
        response['attendance'] = attendance.to_dict() if attendance else None
        response['performance'] = performance.to_dict() if performance else None
        response['ai_insight'] = insight
        response['risk_score'] = risk_score
        response['risk_state'] = risk_state
        
        return jsonify(response)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal error'}), 500


@app.route('/api/students/<roll_number>', methods=['DELETE'])
def delete_student(roll_number):
    """Remove student from system."""
    success = student_manager.remove_student(roll_number)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': 'Student not found'}), 404


@app.route('/api/system/pulse', methods=['GET'])
def system_pulse():
    """Get system-wide intelligence metrics."""
    total_students = student_manager.student_count()
    
    # Attendance health
    att_health, at_risk, _ = attendance_manager.get_overall_health()
    
    # Performance stability
    avg_perf, unstable, _ = performance_manager.get_overall_stability()
    
    # Performance distribution
    perf_dist = performance_manager.get_performance_distribution()
    
    # System insights
    insights = ai_engine.generate_system_insight(
        total_students,
        att_health,
        at_risk,
        avg_perf,
        unstable
    )
    
    return jsonify({
        'total_students': total_students,
        'attendance_health': att_health,
        'students_at_risk': at_risk,
        'average_performance': avg_perf,
        'unstable_students': unstable,
        'performance_distribution': perf_dist,
        'system_insights': insights
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
