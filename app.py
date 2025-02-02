from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'  # Change to PostgreSQL for Render
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Email Configuration (Replace with actual credentials)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')  # Use environment variable
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')  # Use environment variable

mail = Mail(app)

# Database Model
class MessageDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message_text = request.form['message']

        # Save message to the database
        new_message = MessageDB(name=name, email=email, message=message_text)
        db.session.add(new_message)
        db.session.commit()

        # Send Email Notification
        msg = Message(subject=f"New Message from {name}",
                      sender=email,
                      recipients=['geoginah.pr@example.com'],
                      body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_text}")
        mail.send(msg)

        return render_template('thank_you.html', name=name)

    return render_template('contact.html')

if __name__ == '__main__':
    db.create_all()  # Create database tables
    app.run(debug=True)
