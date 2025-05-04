from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Correct import here
from datetime import datetime
import os



app = Flask(__name__)
app.secret_key = '2a34ds5f6yuisfjahsgy6tf'
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:\Users\caleb\OneDrive\Documents\GitHub\4320-Final-Project\reservations.db'
db = SQLAlchemy(app)

class Admin(db.Model):
    __tablename__ = 'admins'
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(100), nullable=False)

class Reserved(db.Model):
    
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    passengerName = db.Column(db.String(100), nullable=False)
    seatRow = db.Column(db.Integer, nullable=False)
    seatColumn = db.Column(db.Integer, nullable=False)
    eTicketNumber = db.Column(db.String(50), unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/adminInfo')
def adminInfo():
    reservations = Reserved.query.all()
    return render_template('adminInfo.html', reservations=reservations)

@app.route('/delete_reservation/<int:reservation_id>', methods=['POST'])
def delete_reservation(reservation_id):
    reservation = Reserved.query.get_or_404(reservation_id)
    db.session.delete(reservation)
    db.session.commit()
    return redirect(url_for('adminInfo'))

@app.route('/test_db')
def test_db():
    try:
        db_path = os.path.abspath('reservations.db')
        result = db.session.execute(text('SELECT * FROM admins')).fetchall()
        return f"Database path: {db_path}<br>Found {len(result)} admin(s): {result}"
    except Exception as e:
        return f"Database connection failed: {e}"

@app.route('/reserved')
def reserved():
    return render_template('ReservedSeat.html')

@app.route('/admin')
def admin():
    return render_template('Admin.html')

@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']

    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.password == password:
        return redirect(url_for('adminInfo'))
    else:
        incorrectInfo = "Incorrect Admin log in credentials"
        return render_template('Admin.html', message = incorrectInfo)

@app.route('/add_reservation', methods=['POST'])
def add_reservation():
    
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    seatRow = int(request.form['seatRow'])
    seatColumn = int(request.form['seatColumn'])

    existing_res = Reserved.query.filter_by(seatRow=seatRow, seatColumn=seatColumn).first()
    if existing_res:
        taken = "Seat has already been taken, please choose another"
        return render_template('ReservedSeat.html', message = taken)
    
    if seatRow < 0 or seatRow > 12 or seatColumn < 0 or seatColumn > 4:
        noExs = "Seat does not exist, please choose another"
        return render_template('ReservedSeat.html', message = noExs)

    passengerName = f"{firstName} {lastName}"

    new_res = Reserved(
        
            passengerName = passengerName,
            seatRow=seatRow,
            seatColumn=seatColumn,
            eTicketNumber = f"{firstName}{seatRow}{seatColumn}"

        )
    thanks = f"Your reservation has been taken, {firstName}"
    db.session.add(new_res)
    db.session.commit()

    return render_template('ReservedSeat.html', message = thanks)

if __name__ == '__main__':
   # with app.app_context():
   #     db.create_all()
    app.run(debug=True)
