# glow_by_splendour/challenges/hydration_challenge.py
import csv
import os
from datetime import date

CHALLENGE_PROGRESS_FILE = '/app/glow_by_splendour/data/challenge_progress.csv'
USER_BADGES_FILE = '/app/glow_by_splendour/data/user_badges.csv'
DATA_DIR = '/app/glow_by_splendour/data'

CHALLENGE_NAME = "hydration_glowup"
BADGE_NAME = "Hydration Champion"
TOTAL_CHALLENGE_DAYS = 7

# Ensure data directory and CSV files exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(CHALLENGE_PROGRESS_FILE):
    with open(CHALLENGE_PROGRESS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "challenge_name", "day_number", "completed_status", "date_completed"])

if not os.path.exists(USER_BADGES_FILE):
    with open(USER_BADGES_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "badge_name", "date_awarded"])


hydration_challenge_days = [
    {
        "day_number": 1,
        "task_description": "Drink 8 glasses (approx. 2 liters) of water throughout the day.",
        "educational_tip": "Proper hydration starts from within! Water is essential for skin cell function and overall plumpness."
    },
    {
        "day_number": 2,
        "task_description": "Apply a hydrating face mask tonight. Look for ingredients like hyaluronic acid, glycerin, or aloe vera.",
        "educational_tip": "Face masks can provide an intense boost of hydration to the skin's surface, helping to soothe and moisturize."
    },
    {
        "day_number": 3,
        "task_description": "Moisturize your skin AM and PM using a product suitable for your skin type. Focus on gentle application.",
        "educational_tip": "Consistent moisturizing strengthens your skin's barrier, preventing water loss and protecting from irritants."
    },
    {
        "day_number": 4,
        "task_description": "Eat at least 3 servings of water-rich fruits or vegetables (e.g., cucumber, watermelon, oranges, berries).",
        "educational_tip": "Your diet plays a role in skin hydration. Water-rich foods contribute to your overall hydration levels."
    },
    {
        "day_number": 5,
        "task_description": "Avoid dehydrating drinks like excessive coffee or sugary sodas today. Opt for herbal tea or infused water instead.",
        "educational_tip": "Some beverages can have a diuretic effect, leading to water loss. Choose hydrating alternatives."
    },
    {
        "day_number": 6,
        "task_description": "Use a hydrating serum (e.g., containing hyaluronic acid or glycerin) before your moisturizer in AM and PM.",
        "educational_tip": "Serums are concentrated formulas that can deliver hydration deeper into the skin than moisturizers alone."
    },
    {
        "day_number": 7,
        "task_description": "Take a lukewarm (not hot!) shower or bath. Apply moisturizer to damp skin immediately after.",
        "educational_tip": "Hot water can strip your skin of natural oils. Applying moisturizer to damp skin helps lock in moisture effectively."
    }
]

def get_challenge_details():
    """Returns the full 7-day challenge structure."""
    return hydration_challenge_days

def get_daily_task(day_number):
    """Returns the task and tip for a specific day."""
    for day_info in hydration_challenge_days:
        if day_info["day_number"] == day_number:
            return day_info
    return None

def log_challenge_progress(user_id, day_number, completed_status):
    """Stores user's completion status for a challenge day."""
    today_str = date.today().isoformat()
    completed_status_bool = str(completed_status).lower() == 'true' # Ensure boolean stored correctly later

    rows = []
    entry_found = False
    if os.path.exists(CHALLENGE_PROGRESS_FILE):
        with open(CHALLENGE_PROGRESS_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user_id'] == user_id and \
                   row['challenge_name'] == CHALLENGE_NAME and \
                   int(row['day_number']) == int(day_number):
                    row['completed_status'] = completed_status_bool
                    row['date_completed'] = today_str if completed_status_bool else "" # Update date only if completed
                    entry_found = True
                rows.append(row)
    
    if not entry_found:
        rows.append({
            "user_id": user_id,
            "challenge_name": CHALLENGE_NAME,
            "day_number": day_number,
            "completed_status": completed_status_bool,
            "date_completed": today_str if completed_status_bool else ""
        })

    with open(CHALLENGE_PROGRESS_FILE, 'w', newline='') as f:
        fieldnames = ["user_id", "challenge_name", "day_number", "completed_status", "date_completed"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True

def get_user_challenge_progress(user_id, challenge_name=CHALLENGE_NAME):
    """
    Retrieves a user's progress for a specific challenge.
    Returns a dictionary like: {day_number: {"completed_status": True/False, "date_completed": "YYYY-MM-DD"}, ...}
    """
    progress = {}
    if not os.path.exists(CHALLENGE_PROGRESS_FILE):
        return progress
        
    with open(CHALLENGE_PROGRESS_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id and row['challenge_name'] == challenge_name:
                progress[int(row['day_number'])] = {
                    "completed_status": row['completed_status'].lower() == 'true',
                    "date_completed": row['date_completed']
                }
    return progress

def award_badge_if_completed(user_id, challenge_name=CHALLENGE_NAME):
    """
    Checks if a user has completed all days of the challenge. If so, awards a badge.
    Returns True if badge awarded, False otherwise.
    """
    user_progress = get_user_challenge_progress(user_id, challenge_name)
    
    completed_days_count = 0
    for day_num in range(1, TOTAL_CHALLENGE_DAYS + 1):
        if user_progress.get(day_num, {}).get("completed_status", False):
            completed_days_count += 1
            
    if completed_days_count == TOTAL_CHALLENGE_DAYS:
        # Check if badge already awarded
        if os.path.exists(USER_BADGES_FILE):
            with open(USER_BADGES_FILE, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_id'] == user_id and row['badge_name'] == BADGE_NAME:
                        return False # Badge already awarded

        # Award badge
        with open(USER_BADGES_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["user_id", "badge_name", "date_awarded"])
            # If file was empty, write header first (check if file size is 0 is a way)
            f.seek(0, os.SEEK_END) # Go to end of file
            if f.tell() == 0: # Check if file is empty
                 writer.writeheader() # Write header if file is empty
            writer.writerow({
                "user_id": user_id,
                "badge_name": BADGE_NAME,
                "date_awarded": date.today().isoformat()
            })
        return True # Badge awarded
    return False # Challenge not fully completed

def get_user_badges(user_id):
    """Retrieves all badges earned by a user."""
    badges = []
    if not os.path.exists(USER_BADGES_FILE):
        return badges
    with open(USER_BADGES_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id:
                badges.append({
                    "badge_name": row['badge_name'],
                    "date_awarded": row['date_awarded'],
                    # Assuming badge images are named consistently like 'Badge Name_badge.png'
                    "image_url": f"/static/images/badges/{row['badge_name'].replace(' ', '_').lower()}_badge.png"
                })
    return badges
