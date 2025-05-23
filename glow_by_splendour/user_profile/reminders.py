# glow_by_splendour/user_profile/reminders.py
import csv
import os

USER_REMINDERS_FILE = '/app/glow_by_splendour/data/user_reminders.csv'
DATA_DIR = '/app/glow_by_splendour/data'

# Ensure data directory and log files exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(USER_REMINDERS_FILE):
    with open(USER_REMINDERS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "time_of_day", "reminder_time", "is_active"])

def set_reminder(user_id, time_of_day, reminder_time, is_active):
    """
    Sets or updates a reminder for a user.
    Each user can have at most one AM and one PM reminder.
    """
    is_active_str = str(is_active).lower() # 'true' or 'false'
    
    rows = []
    entry_found = False
    if os.path.exists(USER_REMINDERS_FILE):
        with open(USER_REMINDERS_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user_id'] == user_id and row['time_of_day'] == time_of_day:
                    row['reminder_time'] = reminder_time
                    row['is_active'] = is_active_str
                    entry_found = True
                rows.append(row)
    
    if not entry_found:
        rows.append({
            "user_id": user_id,
            "time_of_day": time_of_day, # "AM" or "PM"
            "reminder_time": reminder_time, # "HH:MM"
            "is_active": is_active_str
        })

    with open(USER_REMINDERS_FILE, 'w', newline='') as f:
        fieldnames = ["user_id", "time_of_day", "reminder_time", "is_active"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True

def get_reminders(user_id):
    """
    Retrieves a user's reminder settings.
    Returns a dict like: {"AM": {"reminder_time": "HH:MM", "is_active": True/False}, "PM": ...}
    """
    user_reminders = {}
    if not os.path.exists(USER_REMINDERS_FILE):
        return user_reminders
        
    with open(USER_REMINDERS_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id:
                user_reminders[row['time_of_day']] = {
                    "reminder_time": row['reminder_time'],
                    "is_active": row['is_active'].lower() == 'true'
                }
    return user_reminders

def get_active_reminders_for_time(current_time_str):
    """
    Placeholder function: Retrieves all active reminders matching the current time.
    In a real app, this would be used by a background scheduler.
    Args:
        current_time_str (str): Current time in "HH:MM" format.
    Returns:
        list of dicts: [{"user_id": ..., "time_of_day": ..., "reminder_time": ...}, ...]
    """
    due_reminders = []
    if not os.path.exists(USER_REMINDERS_FILE):
        return due_reminders

    with open(USER_REMINDERS_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['is_active'].lower() == 'true' and row['reminder_time'] == current_time_str:
                due_reminders.append({
                    "user_id": row['user_id'],
                    "time_of_day": row['time_of_day'],
                    "reminder_time": row['reminder_time']
                })
    # In a real scenario, you might log or dispatch notifications here.
    # For this task, we just return the list.
    if due_reminders:
        print(f"At {current_time_str}, these reminders are due: {due_reminders}")
        
    return due_reminders
