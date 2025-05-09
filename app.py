from flask import Flask, render_template, request, redirect, url_for #, session --> never used
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime
import os
import random
import string


app = Flask(__name__)
app.secret_key = '2a34ds5f6yuisfjahsgy6tf'
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///reservations.db' # idrk if we need it at the root level too, to scared to delete it
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


def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix


def calculate_total_sales():
    reservations = Reserved.query.all()
    cost_matrix = get_cost_matrix()
    total_sales = 0
    
    for res in reservations:
        row_idx = res.seatRow - 1
        col_idx = res.seatColumn - 1
        
        if 0 <= row_idx < 12 and 0 <= col_idx < 4:
            total_sales += cost_matrix[row_idx][col_idx]
    
    return total_sales


def generate_seating_chart():
    seating_chart = [[None for _ in range(4)] for _ in range(12)]
    
    reservations = Reserved.query.all()
    for res in reservations:
        row_idx = res.seatRow - 1 
        col_idx = res.seatColumn - 1
        
        if 0 <= row_idx < 12 and 0 <= col_idx < 4:
            seating_chart[row_idx][col_idx] = res.passengerName
    
    return seating_chart


def generate_reservation_code(first_name, last_name):
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    code = f"{first_name[0]}{last_name[0]}{random_part}"
    return code


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/adminInfo')
def adminInfo():
    reservations = Reserved.query.all()
    seating_chart = generate_seating_chart()
    total_sales = calculate_total_sales()
    cost_matrix = get_cost_matrix()
    
    return render_template(
        'adminInfo.html', 
        reservations=reservations, 
        seating_chart=seating_chart,
        total_sales=total_sales,
        cost_matrix=cost_matrix
    )


@app.route('/delete_reservation/<int:reservation_id>', methods=['POST'])
def delete_reservation(reservation_id):
    reservation = Reserved.query.get_or_404(reservation_id)
    db.session.delete(reservation)
    db.session.commit()
    return redirect(url_for('adminInfo'))

@app.route('/reserved')
def reserved():
    seating_chart = generate_seating_chart()
    cost_matrix = get_cost_matrix()
    return render_template('ReservedSeat.html', seating_chart=seating_chart, cost_matrix=cost_matrix)


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
        seating_chart = generate_seating_chart()
        cost_matrix = get_cost_matrix()
        return render_template('ReservedSeat.html', message=taken, seating_chart=seating_chart, cost_matrix=cost_matrix)
    
    if seatRow < 1 or seatRow > 12 or seatColumn < 1 or seatColumn > 4:
        noExs = "Seat does not exist, please choose another"
        seating_chart = generate_seating_chart()
        cost_matrix = get_cost_matrix()
        return render_template('ReservedSeat.html', message=noExs, seating_chart=seating_chart, cost_matrix=cost_matrix)

    passengerName = f"{firstName} {lastName}"
    eTicket = generate_reservation_code(firstName, lastName)

    new_res = Reserved(
        passengerName=passengerName,
        seatRow=seatRow,
        seatColumn=seatColumn,
        eTicketNumber=eTicket
    )
    
    db.session.add(new_res)
    db.session.commit()

    cost_matrix = get_cost_matrix()
    seat_price = cost_matrix[seatRow-1][seatColumn-1]
    
    thanks = f"Thank you for your reservation, {firstName}! Your e-ticket number is {eTicket}."
    confirmation = f"You've reserved seat Row {seatRow}, Column {seatColumn} for ${seat_price}."
    
    seating_chart = generate_seating_chart()
    
    return render_template('ReservedSeat.html', 
                           message=thanks, 
                           confirmation=confirmation,
                           eTicket=eTicket,
                           seating_chart=seating_chart,
                           cost_matrix=cost_matrix)


if __name__ == '__main__':
    #with app.app_context():
       # db.create_all() # not making a new db every time
    app.run(debug=True)