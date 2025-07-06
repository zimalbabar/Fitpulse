from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import pandas as pd
from ml_model import predict_fitness
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime

from functions import generate_exercise_plan,bmi_category
from pymongo.errors import DuplicateKeyError


client = MongoClient("YOUR_MONGODB_URI_HERE")

db = client["FitPulse"]

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MongoDB setup
users_col = db["users"]
users_col.create_index("email", unique=True) 

logs_col = db["prevhealth_logs"]
logs_col.create_index([("user_id", 1), ("date", 1)], unique=True)

curr_logs_col = db["currenthealth_logs"]
curr_logs_col.create_index("user_id", unique=True, sparse=True)

workouts_col = db["workouts"]
workouts_col.create_index([("user_id", 1), ("timestamp", 1)])


@app.route('/')
def homepage():
    return render_template('homepage.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'gender': request.form['gender'],
            'age': int(request.form['age']),
            'goal': request.form['goal'],
            'password': generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        }
        try:
            user_id = users_col.insert_one(data).inserted_id
            session['user_id'] = str(user_id)
            session['name'] = data['name']
            return redirect(url_for('dashboard'))
        except DuplicateKeyError:
            flash("Email already registered. Try logging in.", "danger")
            return redirect(url_for('register'))

    return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_col.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['name'] = user['name']
            return redirect(url_for('dashboard'))

        flash("Invalid credentials")
    return render_template('lp.html')





@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))

    prediction = None
    exercise_plan = []
    bmi = None
    bmi_status = None

    if request.method == 'POST':
        try:
            steps = float(request.form['steps'])
            sleep = float(request.form['sleep'])
            calories = float(request.form['calories'])
            heart_rate = float(request.form['heart_rate'])
            water = float(request.form['water']) if request.form['water'] else None
            mood = request.form['mood']
            notes = request.form['notes']
            height_cm = float(request.form['height'])
            weight_kg = float(request.form['weight'])

            height_m = height_cm / 100
            bmi = round(weight_kg / (height_m ** 2), 2)
            bmi_status = bmi_category(bmi)


            prediction = predict_fitness(steps, sleep, calories, heart_rate, height_cm, weight_kg, bmi)


            user_id = session['user_id']

            # Get current log if it exists
            current_log = curr_logs_col.find_one({'user_id': user_id})

            if current_log:
    # Get the current counter or default to 1
                counter = current_log.get('log_counter', 1)
                current_log['log_counter'] = counter
                current_log['date'] = datetime.utcnow()  # Add this too
                logs_col.insert_one(current_log)
                curr_logs_col.delete_one({'_id': current_log['_id']})
                counter += 1
            else:
                counter = 1  # First log — still want to insert it

# Prepare new current log
            new_log = {
    'user_id': user_id,
    'steps': steps,
    'sleep': sleep,
    'calories': calories,
    'heart_rate': heart_rate,
    'water': water,
    'mood': mood,
    'notes': notes,
    'height': height_cm,
    'weight': weight_kg,
    'bmi': bmi,
    'bmi_status': bmi_status,
    'prediction': prediction,
    'log_counter': counter,
    'date': datetime.utcnow()  # Important!
}

# Insert new log into current collection
            curr_logs_col.insert_one(new_log)



            flash("Health data submitted!")

    
            exercise_plan = generate_exercise_plan(steps, sleep, calories,heart_rate,bmi)


        except Exception as e:
            flash(f"Error submitting data: {e}")

    return render_template("dashboard.html",
                            exercise_plan=exercise_plan,
                           prediction=prediction,
                           bmi=bmi,
                           bmi_status=bmi_status)



@app.route('/save_selected_workouts', methods=['POST'])
def save_selected_workouts():
    if 'user_id' not in session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))

    selected_workouts = request.form.getlist('selected_workouts')
    user_id = session['user_id']

    if selected_workouts:
        # Add a progress flag to each selected workout
        workout_entries = [{'name': workout, 'completed': False} for workout in selected_workouts]

        # Save to MongoDB
        workouts_col.insert_one({
            'user_id': user_id,
            'selected_workouts': workout_entries,
            'timestamp': datetime.now()
        })

        flash("Workout strategy saved successfully!")
    else:
        flash("No workouts selected.")

    return redirect(url_for('dashboard'))





@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))






@app.route('/workout_progress', methods=['GET', 'POST'])
def workout_progress():
    if 'user_id' not in session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Get all workout entries for user, sorted by timestamp descending (latest first)
    workouts = list(workouts_col.find({'user_id': user_id}).sort('timestamp', -1))

    if request.method == 'POST':

        
        # Handle update form submission
        for workout_entry in workouts:
            # Each workout doc has _id and list of selected_workouts
            # For each workout inside selected_workouts, get checkbox value by naming convention


            for idx, workout in enumerate(workout_entry['selected_workouts']):
                checkbox_name = f"{workout_entry['_id']}_{idx}"
                completed = checkbox_name in request.form

                if isinstance(workout, dict) and 'name' in workout:
                    filter_query = {'_id': workout_entry['_id'], f'selected_workouts.{idx}.name': workout['name']}
                else:
        # fallback if workout is just a string
                    filter_query = {'_id': workout_entry['_id'], f'selected_workouts.{idx}.name': workout}

                workouts_col.update_one(
        filter_query,
        {'$set': {f'selected_workouts.{idx}.completed': completed}}
    )


           
        flash("Workout progress updated!")
        return redirect(url_for('workout_progress'))
    


    return render_template('workout_progress.html', workouts=workouts)




if __name__ == '__main__':
    app.run(debug=True)
