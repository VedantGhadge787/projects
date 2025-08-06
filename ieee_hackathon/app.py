from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Doctor, Clinic
import bcrypt
import os
def emailcorrecting(email):
    return email.strip().lower()
def get_time(booking):
    return booking["time"]


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///doc_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

    if Clinic.query.count() == 0:
        default_clinics = [
            Clinic(name="Clinic 1", location="Mumbai"),
            Clinic(name="Clinic 2", location="Delhi"),
            Clinic(name="Clinic 3", location="Bangalore")
        ]
        db.session.add_all(default_clinics)
        db.session.commit()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    clinics = Clinic.query.all()

    if request.method == 'POST':
        email = emailcorrecting(request.form['username'])
        password = request.form['password'].encode('utf-8')
        role = request.form.get('role')
        clinic_id = request.form.get('clinic_id')
        doc_code = request.form.get('doc_code', '').strip()

        if User.query.filter_by(email=email).first() or Doctor.query.filter_by(email=email).first():
            flash("Email already registered under another role.")
            return redirect('/register')

        if role == 'patient' and doc_code:
            flash("Patients should not enter a doctor code.")
            return redirect('/register')

        if role == 'doctor' and doc_code != 'doc123':
            flash("Invalid doctor code.")
            return redirect('/register')

        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        if role == 'doctor':
            clinic = Clinic.query.get(int(clinic_id)) if clinic_id else None
            new_user = Doctor(
                email=email,
                password=hashed,
                clinic=clinic,
                all_time=['10', '11', '12', '14', '15', '16', '17', '18', '19', '20', '21', '22'],
                booked_time=[]
            )
        else:
            new_user = User(email=email, password=hashed)

        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully!")

        if role == 'doctor':
            return redirect('/login')
        else:
            session['user_id'] = new_user.id
            return redirect('/select_clinic')

    return render_template('register.html', clinics=clinics)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = emailcorrecting(request.form['username'])
        password = request.form['password'].encode('utf-8')

        doctor = Doctor.query.filter_by(email=email).first()
        user = User.query.filter_by(email=email).first()

        if doctor and bcrypt.checkpw(password, doctor.password):
            session['user_id'] = doctor.id
            session['role'] = 'doctor'
            flash("Login successful as Doctor!")
            return redirect('/doc_dashboard')

        elif user and bcrypt.checkpw(password, user.password):
            session['user_id'] = user.id
            session['role'] = 'patient'
            flash("Login successful as Patient!")
            return redirect('/select_clinic')

        else:
            flash("Invalid credentials.")
            return redirect('/login')

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session or session.get('role') != 'patient':
        flash("Unauthorized access.")
        return redirect('/login')

    clinic_id = request.args.get('clinic_id')
    if clinic_id:
        docs = Doctor.query.filter_by(clinic_id=int(clinic_id)).all()
    else:
        docs = Doctor.query.all()

    selected_doctor = None

    if request.method == 'POST':
        if 'doc_id' in request.form:
            doc_id = request.form['doc_id']
            selected_doctor = Doctor.query.get(int(doc_id))
        elif 'time' in request.form:
            time = request.form['time']
            patient = User.query.get(session['user_id'])
            doc_id = request.form['selected_doc_id']
            doctor = Doctor.query.get(int(doc_id))
            booked_slot_times = [slot['time'] for slot in doctor.booked_time]

            if any(slot['time'] == time for slot in doctor.booked_time):
                flash("Time slot already booked.")
            else:
                doctor.booked_time.append({"time": time, "patient_email": patient.email})
                db.session.commit()
                flash("Booking successful!")
                return redirect(url_for('dashboard', clinic_id=clinic_id, doc_id=doc_id))
    else:
        doc_id = request.args.get('doc_id')
        if doc_id:
            selected_doctor = Doctor.query.get(int(doc_id))
    booked_slot_times = []
    if selected_doctor:
        booked_slot_times = [slot['time'] for slot in selected_doctor.booked_time]
    return render_template('dashboard.html', docs=docs, selected_doctor=selected_doctor, booked_slot_times=booked_slot_times)

@app.route('/select_clinic')
def select_clinic():
    if 'user_id' not in session or session.get('role') != 'patient':
        flash("Unauthorized access.")
        return redirect('/login')

    clinics = Clinic.query.all()
    return render_template('clinic_selection.html', clinics=clinics)

@app.route('/doc_dashboard')
def doc_dashboard():
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash("Unauthorized access.")
        return redirect('/login')
    doctor = Doctor.query.get(session['user_id'])

    bookings = doctor.booked_time or []
    

    bookings.sort(key=get_time)

    return render_template('doc_dashboard.html', bookings=bookings, doctor=doctor)
@app.route('/clinic_select', methods=['POST'])
def go_to_doctor_page():
    clinic_id = request.form['clinic_id']
    return redirect(url_for('dashboard', clinic_id=clinic_id))

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect('/login')

@app.route('/appointments')
def appointments():
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash("Unauthorized access.")
        return redirect('/login')

    doctor = Doctor.query.get(session['user_id'])
    bookings = doctor.booked_time or []

    bookings.sort(key=get_time)

    return render_template('appointments.html', bookings=bookings)


if __name__ == '__main__':
    app.run(debug=True)
