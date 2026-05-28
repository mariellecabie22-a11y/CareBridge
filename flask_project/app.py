from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///carebridge.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(30), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    diagnosis = db.Column(db.String(200), nullable=False)
    discharge_date = db.Column(db.String(20), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    medications = db.Column(db.Text, nullable=False)
    follow_up = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        role = request.form["role"]
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("That email is already registered.", "danger")
            return redirect(url_for("register"))

        user = User(
            full_name=full_name,
            role=role,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

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
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    search = request.args.get("search", "").strip()
    query = Patient.query

    if search:
        query = query.filter(
            (Patient.full_name.ilike(f"%{search}%")) |
            (Patient.mrn.ilike(f"%{search}%")) |
            (Patient.diagnosis.ilike(f"%{search}%"))
        )

    patients = query.order_by(Patient.created_at.desc()).all()
    return render_template("dashboard.html", patients=patients, search=search)

@app.route("/patients/new", methods=["GET", "POST"])
@login_required
def add_patient():
    if request.method == "POST":
        patient = Patient(
            mrn=request.form["mrn"].strip(),
            full_name=request.form["full_name"].strip(),
            dob=request.form["dob"],
            diagnosis=request.form["diagnosis"].strip(),
            discharge_date=request.form["discharge_date"],
            summary=request.form["summary"].strip(),
            medications=request.form["medications"].strip(),
            follow_up=request.form["follow_up"].strip()
        )
        db.session.add(patient)
        db.session.commit()
        flash("Discharge summary added.", "success")
        return redirect(url_for("dashboard"))

    return render_template("patient_form.html", patient=None)

@app.route("/patients/<int:patient_id>")
@login_required
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template("patient_detail.html", patient=patient)

@app.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == "POST":
        patient.mrn = request.form["mrn"].strip()
        patient.full_name = request.form["full_name"].strip()
        patient.dob = request.form["dob"]
        patient.diagnosis = request.form["diagnosis"].strip()
        patient.discharge_date = request.form["discharge_date"]
        patient.summary = request.form["summary"].strip()
        patient.medications = request.form["medications"].strip()
        patient.follow_up = request.form["follow_up"].strip()
        db.session.commit()
        flash("Discharge summary updated.", "success")
        return redirect(url_for("patient_detail", patient_id=patient.id))

    return render_template("patient_form.html", patient=patient)

@app.route("/patients/<int:patient_id>/delete", methods=["POST"])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash("Record deleted.", "info")
    return redirect(url_for("dashboard"))

@app.cli.command("init-db")
def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

    print("Database initialized.")
    print("Users can now create their own accounts.")

if __name__ == "__main__":
    app.run(debug=True)