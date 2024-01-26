from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timedelta
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
    age = db.Column(db.Float)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)    


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

@app.route('/<username>', methods=['GET', 'POST'])
def user_dashboard(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=username).first()

    if request.method == 'POST':
        calorie_intake = request.form.get('calorie_intake')
        exercise_duration = request.form.get('exercise_duration')
        sleep_hours = request.form.get('sleep_hours')
        water_consumed = request.form.get('water_consumed')
        '''
        health_metrics = HealthMetrics(
            user=user,
            calorie_intake=calorie_intake,
            exercise_duration=exercise_duration,
            sleep_hours=sleep_hours,
            water_consumed=water_consumed
        )

        db.session.add(health_metrics)
        db.session.commit()
        '''
    default_content = render_template('partials/health_metrics.html')
    return render_template('base.html', user=user, content = default_content)

@app.route('/update-account', methods=['POST'])
def update_account():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = User.query.filter_by(username=username).first()

    '''
    if user:
        age = request.form.get('age')
        height = request.form.get('height')
        weight = request.form.get('weight')
        calorie_intake_goal = request.form.get('calorie_intake_goal')
        exercise_goal = request.form.get('exercise_goal')
        sleep_goal = request.form.get('sleep_goal')
        water_intake_goal = request.form.get('water_intake_goal')

        user_health_goals = UserHealthGoals(
            user=user,
            age=age,
            height=height,
            weight=weight,
            goal_type_calorie=calorie_intake_goal,
            goal_type_exercise=exercise_goal,
            goal_type_sleep=sleep_goal,
            goal_type_water=water_intake_goal
        )

        db.session.add(user_health_goals)
        db.session.commit()
    '''
    #return redirect(url_for('user_dashboard', username=username))
    return render_template('partials/account_info.html')

@app.route('/submit-metric', methods=['POST'])
def submit_metric():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = User.query.filter_by(username=username).first()

    if user:
        date = request.form.get('date')
        calorie_intake = request.form.get('calorie_intake')
        exercise_duration = request.form.get('exercise')
        sleep_hours = request.form.get('sleep')
        water_consumed = request.form.get('water_intake')

        health_metrics = HealthMetrics(
            user=user,
            date=date,
            calorie_intake=calorie_intake,
            exercise_duration=exercise_duration,
            sleep_hours=sleep_hours,
            water_consumed=water_consumed
        )

        db.session.add(health_metrics)
        db.session.commit()

    return render_template('partials/health_metrics.html')

@app.route('/metrics', methods=['GET'])
def get_metrics():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = User.query.filter_by(username=username).first()

    if user:
        period = request.args.get('period')
        analytics_type = request.args.get('type')

        # Example: Retrieve metrics based on the selected parameters
        metrics_query = HealthMetrics.query.filter_by(user=user)

        # Additional filters based on the selected period (you may need to adjust this logic)
        if period == 'today':
            metrics_query = metrics_query.filter(HealthMetrics.date == datetime.today().date())
        elif period == 'yesterday':
            metrics_query = metrics_query.filter(HealthMetrics.date == (datetime.today() - timedelta(days=1)).date())
        elif period == 'last7days':
            metrics_query = metrics_query.filter(HealthMetrics.date >= (datetime.today() - timedelta(days=7)).date())
        elif period == 'lastmonth':
            metrics_query = metrics_query.filter(HealthMetrics.date >= (datetime.today() - timedelta(days=30)).date())

        # Additional filters based on the selected analytics type
        if analytics_type == 'me':
            metrics_query = metrics_query.filter(HealthMetrics.user == user)
        elif analytics_type == 'age':
            # Add logic for age-based analytics
            pass
        elif analytics_type == 'height':
            # Add logic for height-based analytics
            pass
        elif analytics_type == 'weight':
            # Add logic for weight-based analytics
            pass

        # Execute the query and get the results
        metrics = metrics_query.all()

        # Print the metrics to the console for debugging
        for metric in metrics:
            print(f"Metric: {metric}")

        # Pass the metrics data to the template for rendering
        return render_template('partials/metrics.html', metrics=metrics)

    return redirect(url_for('login'))

@app.route('/account')
def account():
    return render_template('partials/account.html')

@app.route('/health-metrics')
def health_metrics():
    return render_template('partials/health_metrics.html')

@app.route('/add-metric')
def add_metric():
    return render_template('partials/add_metric.html')

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.secret_key = 'totallyuniqueSecretKey' 
    app.run(debug=True, host='0.0.0.0', port=4000)