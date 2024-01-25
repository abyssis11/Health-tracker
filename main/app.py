from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime
from flask import flash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    health_metrics = db.relationship('HealthMetrics', backref='user', lazy=True)

class HealthMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    calorie_intake = db.Column(db.Float)
    exercise_duration = db.Column(db.Float)
    sleep_hours = db.Column(db.Float)
    water_consumed = db.Column(db.Float)

class UserHealthGoals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    goal_type_calorie = db.Column(db.Float)
    goal_type_exercise = db.Column(db.Float)
    goal_type_sleep = db.Column(db.Float)
    goal_type_water = db.Column(db.Float) 


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()

        if existing_user:
            error_message = 'Error: Username already exists'
            flash(error_message)
            return redirect(url_for("register"))
        else:
            new_user = User(
                username=username,
                email=email,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()

            # Redirect to the user's dashboard after successful registration
            return redirect(url_for('user_dashboard', username=username))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['username'] = username  # Store username in session
            return redirect(url_for('user_dashboard', username=username))
        else:
            error_message = 'Error: Username or password is incorrect.'
            flash(error_message)
            return redirect(url_for("login"))

    # If it's a GET request or login fails, render the login template
    return render_template('login.html')

@app.route('/health_metrics/<username>', methods=['GET', 'POST'])
def user_dashboard(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=username).first()

    if request.method == 'POST':
        calorie_intake = request.form.get('calorie_intake')
        exercise_duration = request.form.get('exercise_duration')
        sleep_hours = request.form.get('sleep_hours')
        water_consumed = request.form.get('water_consumed')

        health_metrics = HealthMetrics(
            user=user,
            calorie_intake=calorie_intake,
            exercise_duration=exercise_duration,
            sleep_hours=sleep_hours,
            water_consumed=water_consumed
        )

        db.session.add(health_metrics)
        db.session.commit()

    return render_template('partials/health_metrics.html', user=user)

@app.route('/add_metric_page', methods=['GET'])
def add_metric_page():
    return render_template('partials/add_metric.html')


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.secret_key = 'totallyuniqueSecretKey' 
    app.run(debug=True, host='0.0.0.0', port=4000)