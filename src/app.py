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
        marks = data.get('marks')
        if marks is None or marks == '':
            marks = 0
        
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
        if 'marks' in data and data['marks'] != '':
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

@app.route('/api/data/export', methods=['GET'])
def export_data():
    """Export all student data to JSON."""
    students = student_manager.get_all_students()
    export_list = []
    
    for student in students:
        attendance = attendance_manager.get_attendance(student.roll_number)
        performance = performance_manager.get_performance(student.roll_number)
        
        data = {
            'roll_number': student.roll_number,
            'name': student.name,
            'semester': student.semester,
            'attendance': attendance.to_dict() if attendance else None,
            'performance': performance.to_dict() if performance else None
        }
        export_list.append(data)
        
    return jsonify(export_list)

@app.route('/api/data/import', methods=['POST'])
def import_data():
    """Import student data from JSON."""
    try:
        items = request.get_json()
        if not items or not isinstance(items, list):
            return jsonify({'error': 'Invalid format, expected list'}), 400
            
        success_count = 0
        errors = []
        
        for i, item in enumerate(items):
            try:
                # Basic validation
                if not all(k in item for k in ('roll_number', 'name', 'semester')):
                    continue
                
                try:
                    student_manager.add_student(item['roll_number'], item['name'], int(item['semester']))
                except ValueError:
                    student_manager.update_student(item['roll_number'], name=item['name'], semester=int(item['semester']))
                
                # Attendance
                att = item.get('attendance')
                if att:
                    attendance_manager.set_attendance(
                        item['roll_number'],
                        int(att.get('total_lectures', 0)),
                        int(att.get('attended_lectures', 0))
                    )
                
                # Performance
                perf = item.get('performance')
                if perf:
                    marks = float(perf.get('marks', 0))
                    performance_manager.update_marks(item['roll_number'], marks)
                
                success_count += 1
            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")
                
        return jsonify({'success': True, 'imported': success_count, 'errors': errors})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/upload', methods=['POST'])
def upload_csv():
    """Import students from CSV file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be CSV'}), 400
            
        import csv
        import io
        
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        success_count = 0
        errors = []
        
        for i, row in enumerate(csv_input):
            try:
                clean_row = {k.strip().lower(): v for k, v in row.items() if k}
                
                def get_val(keys, default=None):
                    for k in keys:
                        if k in clean_row:
                            return clean_row[k]
                    return default
                
                roll = get_val(['roll number', 'roll_number', 'roll', 'id'])
                name = get_val(['name', 'student name', 'fullname'])
                sem = get_val(['semester', 'sem'])
                
                if not (roll and name and sem):
                    raise ValueError("Missing required fields")
                
                try:
                    student_manager.add_student(roll, name, int(sem))
                except ValueError:
                    student_manager.update_student(roll, name=name, semester=int(sem))
                
                total = int(get_val(['total lectures', 'total_lectures', 'total'], 0))
                attended = int(get_val(['attended lectures', 'attended_lectures', 'attended'], 0))
                attendance_manager.set_attendance(roll, total, attended)
                
                marks = get_val(['marks', 'score', 'percentage', 'grade'])
                if marks:
                    performance_manager.update_marks(roll, float(marks))
                    
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {i+1}: {str(e)}")
        
        return jsonify({'success': True, 'imported': success_count, 'errors': errors})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from core.database import init_db, db_session

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
