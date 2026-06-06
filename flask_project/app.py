from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os

# Create the Flask application instance
app = Flask(__name__)

# Load sensitive configuration values from environment variables
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Database engine settings help maintain a stable PostreSQL connection on Render/Neon
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# Initialise SQLALchemy so the Flask app can communicate w/ the PostreSQL database
db = SQLAlchemy(app)

class User(db.Model):
    """Store registered healthcare users and their secure login details."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Passwords are stored as hashes, not plain text, for security
    password_hash = db.Column(db.String(255), nullable=False)

class Patient(db.Model):
    """Store patient discharge summary records and related clinical information."""

    id = db.Column(db.Integer, primary_key=True)

    # Basic patient identification details
    mrn = db.Column(db.String(30), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.String(20), nullable=False)

    # Hospital and clinical team details
    hospital_name = db.Column(db.String(120), nullable=False)
    ward = db.Column(db.String(80), nullable=False)
    discharging_physician = db.Column(db.String(120), nullable=False)
    physician_contact = db.Column(db.String(50), nullable=False)

    # Discharge summary content
    diagnosis = db.Column(db.String(200), nullable=False)
    discharge_date = db.Column(db.String(20), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    medications = db.Column(db.Text, nullable=False)
    follow_up = db.Column(db.Text, nullable=False)

    # Automatically records when the discharge summary was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AccountSettings(db.Model):
    """Store user account preferences and profile-related settings."""
    
    __tablename__ = "account_settings"

    id = db.Column(db.Integer, primary_key=True)

    # Creates a one-to-one relationship between a user and their account settings
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    receive_notifications = db.Column(db.Boolean, default=True)
    theme_preference = db.Column(db.String(30), default="Light")

    # Automatically updates the timestamp whenever settings are modified
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref("settings", uselist=False)
    )

def login_required(view):
    """Restrict access to authenticated users only."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view

@app.route("/")
def index():
    """Display the application's homepage."""

    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Create a new user account and initialize default account settings."""

    if request.method == "POST":

        # Collect and sanitize user input
        full_name = request.form["full_name"].strip()
        role = request.form["role"]
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Prevent duplicate email registrations
        if User.query.filter_by(email=email).first():
            flash("That email is already registered.", "danger")
            return redirect(url_for("register"))
        
        # Ensure password confirmation matches
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))
        
        # Create the new user account with a securely hashed password
        user = User(
            full_name=full_name,
            role=role,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        # Create default account settings for the new user
        settings = AccountSettings(user_id=user.id)
        db.session.add(settings)
        db.session.commit()
        
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate users and create a secure login session."""

    if request.method == "POST":

        # Retrieve login credentials from the form
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        # Search for a user account matching the provided email
        user = User.query.filter_by(email=email).first()

        # Verify the password hash before creating a session
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["full_name"] = user.full_name
            session["role"] = user.role
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    """Clear the current session and log the user out."""

    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    """Display all discharge summaries and allow patient searches."""

    # Retrieve the search term entered by the user
    search = request.args.get("search", "").strip()

    # Start with all patient records
    query = Patient.query

    # Filter records by patient name, MRN, or diagnosis
    if search:
        query = query.filter(
            (Patient.full_name.ilike(f"%{search}%")) |
            (Patient.mrn.ilike(f"%{search}%")) |
            (Patient.diagnosis.ilike(f"%{search}%"))
        )

    # Display the most recently created records first
    patients = query.order_by(Patient.created_at.desc()).all()
    return render_template("dashboard.html", patients=patients, search=search)

@app.route("/patients/new", methods=["GET", "POST"])
@login_required
def add_patient():
    """Create a new patient discharge summary record."""

    if request.method == "POST":
        try:

            # Create a new patient record using form data
            patient = Patient(
                mrn=request.form["mrn"].strip(),
                full_name=request.form["full_name"].strip(),
                dob=request.form["dob"],

                hospital_name=request.form["hospital_name"].strip(),
                ward=request.form["ward"].strip(),
                discharging_physician=request.form["discharging_physician"].strip(),
                physician_contact=request.form["physician_contact"].strip(),

                diagnosis=request.form["diagnosis"].strip(),
                discharge_date=request.form["discharge_date"],
                summary=request.form["summary"].strip(),
                medications=request.form["medications"].strip(),
                follow_up=request.form["follow_up"].strip()
            )

            # Save the discharge summary to the database
            db.session.add(patient)
            db.session.commit()

            flash("Discharge summary added.", "success")
            return redirect(url_for("dashboard"))

        except Exception as e:

            # Roll back changes if a database error occurs
            db.session.rollback()
            print(e)
            flash("Database error occurred. Please try again.", "danger")

    return render_template("patient_form.html", patient=None)

@app.route("/patients/<int:patient_id>")
@login_required
def patient_detail(patient_id):
    """Display the complete discharge summary for a selected patient."""

    # Retrieve the patient record or return a 404 error if not found
    patient = Patient.query.get_or_404(patient_id)
    return render_template("patient_detail.html", patient=patient)

@app.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    """Update an existing patient discharge summary record."""

    # Retrieve the selected patient or return a 404 error if it does not exist
    patient = Patient.query.get_or_404(patient_id)

    # Update patient details using submitted form data
    if request.method == "POST":
        patient.mrn = request.form["mrn"].strip()
        patient.full_name = request.form["full_name"].strip()
        patient.dob = request.form["dob"]
        patient.diagnosis = request.form["diagnosis"].strip()
        patient.discharge_date = request.form["discharge_date"]
        patient.summary = request.form["summary"].strip()
        patient.medications = request.form["medications"].strip()
        patient.follow_up = request.form["follow_up"].strip()
        patient.hospital_name = request.form["hospital_name"].strip()
        patient.ward = request.form["ward"].strip()
        patient.discharging_physician = request.form["discharging_physician"].strip()
        patient.physician_contact = request.form["physician_contact"].strip()

        # Save changes to the database
        db.session.commit()

        flash("Discharge summary updated.", "success")
        return redirect(url_for("patient_detail", patient_id=patient.id))

    return render_template("patient_form.html", patient=patient)

@app.route("/patients/<int:patient_id>/delete", methods=["POST"])
@login_required
def delete_patient(patient_id):
    """Delete a patient discharge summary record from the database."""

    # Retrieve the selected patient before deletion
    patient = Patient.query.get_or_404(patient_id)

    db.session.delete(patient)
    db.session.commit()

    flash("Record deleted.", "info")
    return redirect(url_for("dashboard"))

@app.route("/account-settings", methods=["GET", "POST"])
@login_required
def account_settings():
    """Allow users to update profile details, role, email, and password."""

    # Retrieve the currently logged-in user
    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":

        # Update basic account details
        user.full_name = request.form["full_name"].strip()
        user.role = request.form["role"]

        # Check that the new email is not already used by another account
        user.email = request.form["email"].strip().lower()
        new_email = request.form["email"].strip().lower()
        existing_user = User.query.filter_by(email=new_email).first()
        
        if existing_user and existing_user.id != user.id:
            flash("That email is already in use.", "danger")
            return redirect(url_for("account_settings"))
        
        user.email = new_email

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_new_password = request.form["confirm_new_password"]

        # Only update the password if the user entered a new one
        if new_password:
            if new_password != confirm_new_password:
                flash("New passwords do not match.", "danger")
                return redirect(url_for("account_settings"))
            
            # Verify the current password before saving a new password hash
            if not check_password_hash(user.password_hash, current_password):
                flash("Current password is incorrect.", "danger")
                return redirect(url_for("account_settings"))
                
            user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        
        # Keep session data consistent with any updated account information
        session["full_name"] = user.full_name
        session["role"] = user.role
        flash("Account settings updated.", "success")
        return redirect(url_for("account_settings"))

    return render_template("account_settings.html", user=user)

@app.cli.command("init-db")
def init_db():
    """Recreate all database tables for development or setup purposes."""

    db.drop_all()
    db.create_all()
    db.session.commit()

    print("Database initialized.")
    print("Users can now create their own accounts.")

# Ensure database tables exist when the app starts
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)