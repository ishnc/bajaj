import pandas as pd
import numpy as np
import re

def track_absent_sessions(student_data):
    student_data['session_date'] = pd.to_datetime(student_data['attendance_date'])
    student_data.sort_values(by=['student_id', 'session_date'], inplace=True)
    
    student_data['absent_indicator'] = student_data['status'] == 'Absent'
    student_data['session_group'] = (student_data['absent_indicator'] != student_data['absent_indicator'].shift()).cumsum()
    
    absent_sessions = student_data[student_data['absent_indicator']]
    absent_sessions['session_length'] = absent_sessions.groupby('session_group')['session_date'].transform('size')
    
    long_absences = absent_sessions[absent_sessions['session_length'] > 3]
    
    absence_summary = long_absences.groupby('student_id').agg(
        absence_start_date=('session_date', 'min'),
        absence_end_date=('session_date', 'max'),
        total_absent_days=('session_date', 'size')
    ).reset_index()

    return absence_summary

attendance_records = pd.DataFrame({
    'student_id': [101, 101, 101, 101, 101, 102, 102, 102, 102, 102, 103, 103, 103, 103, 103, 103, 103, 104, 104, 104, 104],
    'attendance_date': ['2024-03-01', '2024-03-02', '2024-03-03', '2024-03-04', '2024-03-05', '2024-03-02', '2024-03-03', '2024-03-04', '2024-03-05', '2024-03-06', '2024-03-05', '2024-03-06', '2024-03-07', '2024-03-08', '2024-03-09', '2024-03-10', '2024-03-11', '2024-03-01', '2024-03-02', '2024-03-03', '2024-03-04'],
    'status': ['Absent', 'Absent', 'Absent', 'Absent', 'Present', 'Absent', 'Absent', 'Absent', 'Absent', 'Absent', 'Absent', 'Absent', 'Absent', 'Absent', 'Absent', 'Absent', 'Absent', 'Present', 'Present', 'Present', 'Present']
})

attendance_records['attendance_date'] = pd.to_datetime(attendance_records['attendance_date'])
absence_summary = track_absent_sessions(attendance_records)
print(absence_summary)

def validate_parent_email(email):
    regex_pattern = r'^[a-zA-Z][a-zA-Z0-9_]*@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'
    return bool(re.match(regex_pattern, email))

def combine_student_data(absence_report, student_details):
    merged_data = pd.merge(absence_report, student_details, on='student_id', how='left')
    
    merged_data['is_valid_email'] = merged_data['parent_email'].apply(validate_parent_email)
    
    merged_data['email_notification'] = np.where(
        merged_data['is_valid_email'], 
        merged_data.apply(lambda row: f"Dear Parent, your child {row['student_name']} was absent from {row['absence_start_date']} to {row['absence_end_date']} for {row['total_absent_days']} days. Please ensure their attendance improves.", axis=1), 
        ''
    )
    
    final_report = merged_data[['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days', 'parent_email', 'email_notification']]
    return final_report

student_information = pd.DataFrame({
    'student_id': [101, 102, 103, 104, 105],
    'student_name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown', 'David Lee', 'Eva White'],
    'parent_email': ['alice_parent@example.com', 'bob_parent@example.com', 'invalid_email.com', 'invalid_email.com', 'eva_white@example.com']
})

final_output = combine_student_data(absence_summary, student_information)
print(final_output)
