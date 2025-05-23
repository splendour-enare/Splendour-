import csv
import os

USER_SKINDATA_FILE = '/app/glow_by_splendour/data/user_skindata.csv'
USER_ROUTINES_FILE = '/app/glow_by_splendour/data/user_routines.csv'

# Ensure the data directory and relevant CSV files exist when this module is loaded
DATA_DIR = os.path.dirname(USER_SKINDATA_FILE)
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(USER_SKINDATA_FILE):
    with open(USER_SKINDATA_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "skin_type"])

if not os.path.exists(USER_ROUTINES_FILE):
    with open(USER_ROUTINES_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        # user_id, routine_name, time_of_day, step_number, step_name, product_name
        writer.writerow(["user_id", "routine_name", "time_of_day", "step_number", "step_name", "product_name"])


def get_user_profile_data(user_id):
    """
    Placeholder function to get user profile data.
    """
    return {}

def save_skin_type(user_id, skin_type):
    """Saves or updates the user's skin type in user_skindata.csv."""
    rows = []
    user_found = False
    if os.path.exists(USER_SKINDATA_FILE):
        with open(USER_SKINDATA_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user_id'] == user_id:
                    row['skin_type'] = skin_type
                    user_found = True
                rows.append(row)
    
    if not user_found:
        rows.append({'user_id': user_id, 'skin_type': skin_type})

    with open(USER_SKINDATA_FILE, 'w', newline='') as f:
        fieldnames = ['user_id', 'skin_type']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True

def get_skin_type(user_id):
    """Retrieves the user's skin type from user_skindata.csv."""
    if not os.path.exists(USER_SKINDATA_FILE):
        return None
        
    with open(USER_SKINDATA_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id:
                return row['skin_type']
    return None

# --- Routine Management Functions ---

def save_user_routine(user_id, routine_name, time_of_day, routine_steps):
    """
    Saves a user's customized routine.
    routine_steps is a list of dicts: [{"step_name": "...", "product_name": "..."}]
    This function will overwrite any existing routine with the same user_id and routine_name.
    """
    all_routines = []
    # Read existing routines, excluding the one being saved/updated
    if os.path.exists(USER_ROUTINES_FILE):
        with open(USER_ROUTINES_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not (row['user_id'] == user_id and row['routine_name'] == routine_name and row['time_of_day'] == time_of_day) :
                    all_routines.append(row)
    
    # Add the new/updated routine steps
    for i, step in enumerate(routine_steps):
        all_routines.append({
            "user_id": user_id,
            "routine_name": routine_name,
            "time_of_day": time_of_day,
            "step_number": i + 1,
            "step_name": step["step_name"],
            "product_name": step["product_suggestion"] # or product_name if customized
        })

    # Write everything back
    with open(USER_ROUTINES_FILE, 'w', newline='') as f:
        fieldnames = ["user_id", "routine_name", "time_of_day", "step_number", "step_name", "product_name"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_routines)
    return True


def get_user_routines(user_id):
    """
    Retrieves all saved routines for a given user.
    Returns a dict of routines, e.g., 
    { 
        "My AM Routine": {"AM": [{"step_number": 1, "step_name": "...", "product_name": "..."}, ...]},
        "My PM Routine": {"PM": [...]} 
    }
    """
    user_routines = {}
    if not os.path.exists(USER_ROUTINES_FILE):
        return user_routines
        
    with open(USER_ROUTINES_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id:
                routine_name = row['routine_name']
                time_of_day = row['time_of_day']
                
                if routine_name not in user_routines:
                    user_routines[routine_name] = {}
                if time_of_day not in user_routines[routine_name]:
                    user_routines[routine_name][time_of_day] = []
                
                user_routines[routine_name][time_of_day].append({
                    "step_number": int(row['step_number']),
                    "step_name": row['step_name'],
                    "product_name": row['product_name']
                })
    
    # Sort steps by step_number
    for name, times in user_routines.items():
        for time, steps in times.items():
            user_routines[name][time] = sorted(steps, key=lambda x: x['step_number'])
            
    return user_routines
