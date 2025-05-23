import csv
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

DATA_FILE = '/app/glow_by_splendour/data/users.csv'

def sign_up(username, email, password):
    """Registers a new user."""
    if not username or not email or not password:
        return False, "All fields are required."

    # Check if user already exists
    with open(DATA_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] == username or row['email'] == email:
                return False, "Username or email already exists."

    user_id = str(uuid.uuid4())
    hashed_password = generate_password_hash(password)

    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, email, hashed_password])
    return True, "Signup successful!"

def login(email, password):
    """Logs in an existing user."""
    if not email or not password:
        return False, "Email and password are required."

    with open(DATA_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['email'] == email:
                if check_password_hash(row['hashed_password'], password):
                    return True, "Login successful!", row['username'], row['user_id']
                else:
                    return False, "Invalid password.", None, None
        return False, "Email not found.", None, None

def get_user_by_id(user_id):
    """Retrieves a user by their ID."""
    with open(DATA_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id:
                return row
    return None
