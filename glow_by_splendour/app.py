import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Adjust the Python path to include the project root
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from glow_by_splendour.auth import auth
from glow_by_splendour.user_profile import profile
from glow_by_splendour.user_profile import quiz as skin_quiz
from glow_by_splendour.user_profile import tracking
from glow_by_splendour.user_profile import reminders as reminder_manager
from glow_by_splendour.routines import routine_generator
from glow_by_splendour.education import hub as education_hub
from glow_by_splendour.challenges import hydration_challenge # Import the challenge module
from datetime import date, datetime

app = Flask(__name__, template_folder='ui/templates')
app.secret_key = os.urandom(24) # For session management

# Define the path to the data directory relative to this file
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
auth.DATA_FILE = os.path.join(DATA_DIR, 'users.csv')


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('user_profile'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('user_profile'))
    error = None
    message = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        success, msg = auth.sign_up(username, email, password)
        if success:
            message = msg
            flash(message, 'success') # Using flash for messages
            return redirect(url_for('login'))
        else:
            error = msg
    return render_template('signup.html', error=error, message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('user_profile'))
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        success, msg, username, user_id = auth.login(email, password)
        if success:
            session['user_id'] = user_id
            session['username'] = username
            flash(msg, 'success')
            return redirect(url_for('user_profile'))
        else:
            error = msg
    return render_template('login.html', error=error)

@app.route('/profile')
def user_profile():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))
    
    # In a real app, you might fetch more user data here using profile.py
    # user_data = profile.get_user_profile_data(session['user_id'])
    skin_type = profile.get_skin_type(session['user_id'])
    user_badges_list = hydration_challenge.get_user_badges(session['user_id']) # Fetch badges
    return render_template('profile.html', username=session.get('username'), skin_type=skin_type, user_badges=user_badges_list)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/quiz', methods=['GET', 'POST'])
def take_quiz():
    if 'user_id' not in session:
        flash('Please log in to take the quiz.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        answers = {}
        for question in skin_quiz.quiz_questions:
            answer = request.form.get(question['id'])
            if not answer:
                flash('Please answer all questions.', 'error')
                return render_template('quiz.html', questions=skin_quiz.quiz_questions, error='Please answer all questions.')
            answers[question['id']] = answer
        
        determined_skin_type = skin_quiz.determine_skin_type(answers)
        profile.save_skin_type(session['user_id'], determined_skin_type)
        flash(f'Your skin type has been determined as: {determined_skin_type}', 'success')
        return redirect(url_for('user_profile'))

    # Check if user has already taken the quiz
    existing_skin_type = profile.get_skin_type(session['user_id'])
    if existing_skin_type:
        flash(f'You have already taken the quiz. Your skin type is: {existing_skin_type}. You can retake it if you wish.', 'info')
        
    return render_template('quiz.html', questions=skin_quiz.quiz_questions)

@app.route('/routines')
def view_routines():
    if 'user_id' not in session:
        flash('Please log in to view routines.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    skin_type = profile.get_skin_type(user_id)

    if not skin_type:
        flash('Please take the skin type quiz to get routine suggestions.', 'info')
        return redirect(url_for('take_quiz'))

    generated_am_routine = routine_generator.generate_routine(skin_type, "AM")
    generated_pm_routine = routine_generator.generate_routine(skin_type, "PM")
    
    saved_routines = profile.get_user_routines(user_id)

    return render_template('routines.html', 
                           skin_type=skin_type,
                           generated_am_routine=generated_am_routine,
                           generated_pm_routine=generated_pm_routine,
                           saved_routines=saved_routines)

# --- Progress Tracking Routes ---
@app.route('/tracking/log', methods=['GET', 'POST'])
def log_daily_entry():
    if 'user_id' not in session:
        flash('Please log in to track progress.', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    today_date_str = date.today().isoformat()
    entry_data = tracking.get_latest_log_entry_for_date(user_id, today_date_str) # For pre-filling

    if request.method == 'POST':
        log_date_str = request.form.get('log_date', today_date_str)
        # Validate date format if necessary, here assuming it's correct
        
        am_completed = request.form.get('am_completed') == 'true'
        pm_completed = request.form.get('pm_completed') == 'true'
        rating = request.form.get('rating')
        notes = request.form.get('notes', '')

        if not rating: # Basic validation
            flash('Skin rating is required.', 'error')
            # Re-populate entry_data for the selected date if different from today
            if log_date_str != today_date_str:
                 entry_data = tracking.get_latest_log_entry_for_date(user_id, log_date_str)
            else: # for today, we already have it
                # Update with current form values before re-rendering
                entry_data['am_completed'] = am_completed
                entry_data['pm_completed'] = pm_completed
                entry_data['notes'] = notes

            return render_template('log_entry.html', today_date=log_date_str, entry_data=entry_data)

        tracking.log_routine_adherence(user_id, log_date_str, am_completed, pm_completed)
        tracking.log_skin_condition(user_id, log_date_str, int(rating), notes)
        
        flash('Progress logged successfully for ' + log_date_str + '!', 'success')
        return redirect(url_for('view_progress'))

    # For GET request, or if POST fails validation and re-renders
    # If a date is passed in query params, load data for that date
    query_date_str = request.args.get('date', today_date_str)
    if query_date_str:
        try:
            # Validate query_date_str format
            datetime.strptime(query_date_str, '%Y-%m-%d')
            entry_data = tracking.get_latest_log_entry_for_date(user_id, query_date_str)
            today_date_str = query_date_str # Set the date picker to this date
        except ValueError:
            flash("Invalid date format in query.", "error")
            # entry_data remains for today_date_str

    return render_template('log_entry.html', today_date=today_date_str, entry_data=entry_data)


@app.route('/tracking/progress')
def view_progress():
    if 'user_id' not in session:
        flash('Please log in to view progress.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    skin_condition_logs = tracking.get_skin_condition_data(user_id)
    routine_adherence_logs = tracking.get_adherence_data(user_id)

    # Prepare data for charts
    skin_log_dates = [log['date'] for log in skin_condition_logs]
    skin_log_ratings = [log['rating'] for log in skin_condition_logs]
    
    adherence_log_dates = [log['date'] for log in routine_adherence_logs]
    # For bar chart, 1 for true, 0 for false
    adherence_am_counts = [1 if log['am_completed'] else 0 for log in routine_adherence_logs]
    adherence_pm_counts = [1 if log['pm_completed'] else 0 for log in routine_adherence_logs]

    return render_template('progress_view.html',
                           skin_condition_logs=skin_condition_logs,
                           routine_adherence_logs=routine_adherence_logs,
                           skin_log_dates=skin_log_dates,
                           skin_log_ratings=skin_log_ratings,
                           adherence_log_dates=adherence_log_dates,
                           adherence_am_counts=adherence_am_counts,
                           adherence_pm_counts=adherence_pm_counts)

# --- Reminder Routes ---
@app.route('/reminders', methods=['GET', 'POST'])
def manage_reminders():
    if 'user_id' not in session:
        flash('Please log in to manage reminders.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        am_reminder_time = request.form.get('am_reminder_time')
        am_is_active = request.form.get('am_is_active') == 'true'
        
        pm_reminder_time = request.form.get('pm_reminder_time')
        pm_is_active = request.form.get('pm_is_active') == 'true'

        if am_reminder_time: # Only save if a time is provided
            reminder_manager.set_reminder(user_id, "AM", am_reminder_time, am_is_active)
        else: # If time is cleared, consider it disabled
            reminder_manager.set_reminder(user_id, "AM", "", False)


        if pm_reminder_time: # Only save if a time is provided
            reminder_manager.set_reminder(user_id, "PM", pm_reminder_time, pm_is_active)
        else: # If time is cleared, consider it disabled
            reminder_manager.set_reminder(user_id, "PM", "", False)
            
        flash('Reminder settings saved successfully!', 'success')
        return redirect(url_for('manage_reminders'))

    current_reminders = reminder_manager.get_reminders(user_id)
    return render_template('reminders.html', reminders=current_reminders)

# --- Education Hub Routes ---
@app.route('/education')
def education_hub_main():
    search_query = request.args.get('search')
    if search_query:
        articles_to_display = education_hub.search_articles(search_query)
        if not articles_to_display:
            flash(f"No articles found matching '{search_query}'. Showing all articles instead.", 'info')
            articles_to_display = education_hub.get_all_articles()
    else:
        articles_to_display = education_hub.get_all_articles()
    
    return render_template('education/hub_main.html', articles=articles_to_display, search_query=search_query)

@app.route('/education/article/<article_id>')
def view_article(article_id):
    article = education_hub.get_article_by_id(article_id)
    if not article:
        flash('Article not found.', 'error')
        return redirect(url_for('education_hub_main'))
    return render_template('education/article_detail.html', article=article)

# --- Hydration Challenge Routes ---
@app.route('/challenges/hydration', methods=['GET'])
def view_hydration_challenge():
    if 'user_id' not in session:
        flash('Please log in to view challenges.', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    challenge_details_list = hydration_challenge.get_challenge_details()
    user_progress_data = hydration_challenge.get_user_challenge_progress(user_id)
    
    # Check if a badge was just awarded (e.g., via a query param or session flash)
    # For simplicity, we'll pass it directly if it's a result of a POST from this page.
    # A more robust way might use session flashing for badge award notifications.
    badge_awarded_this_session = session.pop('badge_awarded_hydration_glowup', False)

    return render_template('challenges/challenge_main.html',
                           challenge_details=challenge_details_list,
                           user_progress=user_progress_data,
                           badge_awarded_just_now=badge_awarded_this_session,
                           badge_name=hydration_challenge.BADGE_NAME)

@app.route('/challenges/hydration/log/<int:day_number>', methods=['POST'])
def log_hydration_challenge_day(day_number):
    if 'user_id' not in session:
        flash('Please log in to update challenge progress.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    completed_status_str = request.form.get('completed_status', 'false') # 'true' or 'false'
    completed_status = completed_status_str.lower() == 'true'

    daily_task = hydration_challenge.get_daily_task(day_number)
    if not daily_task:
        flash(f'Invalid challenge day: {day_number}.', 'error')
        return redirect(url_for('view_hydration_challenge'))

    hydration_challenge.log_challenge_progress(user_id, day_number, completed_status)
    
    if completed_status:
        flash(f'Day {day_number} marked as complete!', 'success')
        if hydration_challenge.award_badge_if_completed(user_id):
            # Using session to indicate a badge was just awarded for the GET request
            session['badge_awarded_hydration_glowup'] = True
            # The message will be shown on the main challenge page after redirect
    else:
        flash(f'Day {day_number} updated.', 'info')
        # If a day is unmarked, a previously awarded badge for this session flag should be cleared
        if 'badge_awarded_hydration_glowup' in session:
            del session['badge_awarded_hydration_glowup']


    return redirect(url_for('view_hydration_challenge'))


if __name__ == '__main__':
    # Ensure the data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Create users.csv if it doesn't exist
    if not os.path.exists(auth.DATA_FILE):
        with open(auth.DATA_FILE, 'w', newline='') as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(["user_id", "username", "email", "hashed_password"])
            
    app.run(debug=True)
