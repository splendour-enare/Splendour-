# glow_by_splendour/user_profile/tracking.py
import csv
import os
from datetime import date

ROUTINE_LOGS_FILE = '/app/glow_by_splendour/data/routine_logs.csv'
SKIN_LOGS_FILE = '/app/glow_by_splendour/data/skin_logs.csv'
DATA_DIR = '/app/glow_by_splendour/data'

# Ensure data directory and log files exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(ROUTINE_LOGS_FILE):
    with open(ROUTINE_LOGS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "date", "am_completed", "pm_completed"])

if not os.path.exists(SKIN_LOGS_FILE):
    with open(SKIN_LOGS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "date", "rating", "notes"])

def log_routine_adherence(user_id, log_date, am_completed, pm_completed):
    """
    Logs or updates routine adherence for a specific date.
    If an entry for the user_id and date already exists, it's updated.
    """
    log_date_str = log_date.isoformat() if isinstance(log_date, date) else str(log_date)
    am_completed_str = str(am_completed).lower() # 'true' or 'false'
    pm_completed_str = str(pm_completed).lower() # 'true' or 'false'

    rows = []
    entry_found = False
    if os.path.exists(ROUTINE_LOGS_FILE):
        with open(ROUTINE_LOGS_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user_id'] == user_id and row['date'] == log_date_str:
                    row['am_completed'] = am_completed_str
                    row['pm_completed'] = pm_completed_str
                    entry_found = True
                rows.append(row)
    
    if not entry_found:
        rows.append({
            "user_id": user_id, 
            "date": log_date_str, 
            "am_completed": am_completed_str, 
            "pm_completed": pm_completed_str
        })

    with open(ROUTINE_LOGS_FILE, 'w', newline='') as f:
        fieldnames = ["user_id", "date", "am_completed", "pm_completed"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True

def log_skin_condition(user_id, log_date, rating, notes):
    """
    Logs or updates skin condition for a specific date.
    If an entry for the user_id and date already exists, it's updated.
    """
    log_date_str = log_date.isoformat() if isinstance(log_date, date) else str(log_date)
    
    rows = []
    entry_found = False
    if os.path.exists(SKIN_LOGS_FILE):
        with open(SKIN_LOGS_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user_id'] == user_id and row['date'] == log_date_str:
                    row['rating'] = rating
                    row['notes'] = notes
                    entry_found = True
                rows.append(row)

    if not entry_found:
        rows.append({
            "user_id": user_id,
            "date": log_date_str,
            "rating": rating,
            "notes": notes
        })
    
    with open(SKIN_LOGS_FILE, 'w', newline='') as f:
        fieldnames = ["user_id", "date", "rating", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True

def get_adherence_data(user_id):
    """Retrieves all routine adherence logs for a user, sorted by date."""
    logs = []
    if not os.path.exists(ROUTINE_LOGS_FILE):
        return logs
    with open(ROUTINE_LOGS_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id:
                # Convert boolean strings to actual booleans for easier use in templates/JS
                row['am_completed'] = row['am_completed'].lower() == 'true'
                row['pm_completed'] = row['pm_completed'].lower() == 'true'
                logs.append(row)
    return sorted(logs, key=lambda x: x['date'])

def get_skin_condition_data(user_id):
    """Retrieves all skin condition logs for a user, sorted by date."""
    logs = []
    if not os.path.exists(SKIN_LOGS_FILE):
        return logs
    with open(SKIN_LOGS_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id:
                row['rating'] = int(row['rating']) # Convert rating to int
                logs.append(row)
    return sorted(logs, key=lambda x: x['date'])

def get_latest_log_entry_for_date(user_id, log_date):
    """Retrieves the latest routine and skin log for a specific date for pre-filling the form."""
    log_date_str = log_date.isoformat() if isinstance(log_date, date) else str(log_date)
    latest_data = {
        "am_completed": False,
        "pm_completed": False,
        "rating": 0, # Or some default like 3
        "notes": ""
    }
    
    adherence_data = get_adherence_data(user_id)
    for log in adherence_data:
        if log['date'] == log_date_str:
            latest_data["am_completed"] = log['am_completed']
            latest_data["pm_completed"] = log['pm_completed']
            break
            
    skin_data = get_skin_condition_data(user_id)
    for log in skin_data:
        if log['date'] == log_date_str:
            latest_data["rating"] = log['rating']
            latest_data["notes"] = log['notes']
            break
            
    return latest_data
