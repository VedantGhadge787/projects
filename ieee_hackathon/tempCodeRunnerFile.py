@app.route('/register', methods=['GET', 'POST'])
def register():
    role = request.form.get('role') if request.method == 'POST' else None  

    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password'].encode('utf-8')
        clinic_id = request.form.get('clinic_id') 
        doc_code = request.form.get('doc_code', '')

        if role == 'doctor' and doc_code != 'doc123':
            flash("Invalid doctor code.")
            return redirect('/register')

        if User.query.filter_by(email=email).first():
            flash("User already exists.")
            return redirect('/register')
        
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        if role == 'doctor' and doc_code == 'doc123':
            clinic = Clinic.query.get(int(clinic_id)) if clinic_id else None
            new_user = Doctor(
                email=email,
                password=hashed,
                role=role,
                clinic=clinic,
                all_time=['10', '11', '12', '14', '15', '16', '17', '18', '19', '20', '21', '22'],
                booked_time=[]
            )
        else:
            new_user = User(email=email, password=hashed, role=role)

        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully!")

        if role == 'doctor':
            return redirect('/login')
        else:
            session['user_id'] = new_user.id
            session['role'] = new_user.role
            return redirect('/select_clinic')

    clinics = Clinic.query.all()
    return render_template('register.html', clinics=clinics, role=role)