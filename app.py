from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Secret Key for Sessions
app.secret_key = 'your_secret_key_here'  # Make sure to set this to something unique!

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'  # Change if using PostgreSQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'brandmwenja@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'zhoz chgx girp yswp'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'  # Optional: set a default sender

mail = Mail(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# User Model (for login and signup)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# ContactMessage Model (for storing contact form messages)
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Ensure the query works on the User model

# Routes
@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    return render_template('index.html')  # Show home page only if logged in

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message_text = request.form['message']

        # Store the message in the database
        new_message = ContactMessage(name=name, email=email, message=message_text)
        db.session.add(new_message)
        db.session.commit()

        # Send email notification
        msg = Message(subject=f"New Message from {name}",
                      sender=app.config['MAIL_USERNAME'],  # Ensures sender matches your Gmail account
                      recipients=['brandmwenja@gmail.com'],
                      body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_text}")
        mail.send(msg)

        return render_template('thank_you.html', name=name)

    return render_template('contact.html')

@app.route('/portfolio/project1')
def project1():
    return render_template('project1.html',
                           title="Global Diplomacy Project",
                           description="Detailed explanation of the Global Diplomacy Project...",
                           image="images/project 1.webp")  # Add image path

@app.route('/portfolio/project2')
def project2():
    return render_template('project2.html',
                           title="Global Diplomacy Project",
                           description="Detailed explanation of the Global Diplomacy Project...",
                           image="images/project 2.webp")  # Add image path

@app.route('/portfolio/project3')
def project3():
    return render_template('project3.html',
                           title="Global Diplomacy Project",
                           description=" This project analyzes the role of diplomacy in fostering peaceful international relations. It explores key diplomatic strategies used by global powers and the impact of diplomatic negotiations on global stability. The project also examines how diplomacy can address major global challenges such as conflict resolution, economic partnerships, and international treaties.",
                           image="images/project 3.webp")  # Add image path

# Login Route (login page)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form  # Check if "Remember Me" is selected

        # Check if user exists
        user = User.query.filter_by(email=email).first()

        if user:
            # Check if the password is correct
            if check_password_hash(user.password, password):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('index'))  # Redirect to home page after successful login
            else:
                flash('Invalid password. Please try again.', 'danger')
        else:
            flash('No user found with this email. Please sign up first.', 'danger')

    return render_template('login.html')

# Home Route (after successful login)
@app.route('/index')
@login_required  # Protect this route so only logged-in users can access it
def index():
    return render_template('index.html')  # This is where you can show the user after login

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Logout Route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))  # Redirect to login after logout

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures database tables are created
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=True)


