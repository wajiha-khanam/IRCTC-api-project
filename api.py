
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask_jwt_extended import get_jwt_identity, jwt_required, JWTManager, create_access_token
from datetime import datetime, timedelta


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/railway_management'
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config['SECRET_KEY'] = 'railwayAPI'

db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.VARCHAR(300), nullable = False)
    role = db.Column(db.String(10), nullable = False)

    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

class Train(db.Model):
    __tablename__ = 'Train'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    source = db.Column(db.String(100), nullable = False)
    destination = db.Column(db.String(100), nullable = False)
    departure_time = db.Column(db.DateTime, nullable = False)
    arrival_time = db.Column(db.DateTime, nullable = False)
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable = False)

    def __init__(self, name, source, destination, departure_time, arrival_time, total_seats, available_seats, price):
        self.name =name
        self.source = source
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.total_seats = total_seats
        self.available_seats = available_seats
        self.price = price

class BookingDetails(db.Model):
    __tablename__ = 'Booking Details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('Train.id'), nullable=False)
    seats_booked = db.Column(db.Integer, nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, train_id, seats_booked, booking_time):
        self.user_id = user_id
        self.train_id = train_id
        self.seats_booked = seats_booked
        self.booking_time = datetime.utcnow()


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if User.query.filter_by(username = username).first():
        return jsonify ({'message' : 'User already exists .'}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, role=role)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username = username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid username or password'}),401

    token = create_access_token(identity=user.id, expires_delta=timedelta(hours=24))
    return jsonify({'token': token, 'role': user.role}), 200

def token_required():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({'message': 'Token is missing or invalid'}), 403

    current_user = User.query.filter_by(id=user_id).first()
    if not current_user:
        return jsonify({'message': 'User not found'}), 403

    return current_user


def admin_required(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You are not authorized to perform this action !'}), 403

@app.route('/admin/add_train', methods=['POST'])
def add_train():
    current_user = token_required()
    if not isinstance(current_user, User):
        return current_user
    auth_check = admin_required(current_user)
    if auth_check:
        return auth_check

    data = request.get_json()
    name = data.get('name')
    source = data.get('source')
    destination = data.get('destination')
    departure_time = data.get('departure_time')
    arrival_time = data.get('arrival_time')
    total_seats = data.get('total_seats')
    available_seats = data.get('available_seats')
    price = data.get('price')

    if not all([name, source, destination, departure_time, arrival_time, total_seats, available_seats, price]):
        return jsonify({'message': 'missing data for train creation'}), 400

    existing_train = Train.query.filter_by(name=name).first()
    if existing_train:
        return jsonify({'message': 'Train with this name already exists.'}), 409


    new_train = Train(
        name=name,
        source=source,
        destination=destination,
        departure_time=datetime.strptime(departure_time, '%Y-%m-%dT%H:%M:%S'),
        arrival_time=datetime.strptime(arrival_time, '%Y-%m-%dT%H:%M:%S'),
        total_seats=total_seats,
        available_seats=available_seats,
        price=price
    )
    db.session.add(new_train)
    db.session.commit()
    return jsonify({'message': 'Train added successfully!'}), 201


@app.route('/seat_availability', methods=['GET'])
def get_availability():
    source = request.args.get('source')
    destination = request.args.get('destination')

    trains = Train.query.filter_by(source=source, destination=destination).all()

    result = [{"train_name": train.name, "available_seats": train.available_seats} for train in trains]

    return jsonify(result), 200


@app.route('/book_seat', methods=['POST'])
@jwt_required()
def book_seat():
    data = request.get_json()
    train_id = data.get('train_id')
    seats_to_book = data.get('seats_to_book', 1)

    if not train_id:
        return jsonify({'error': 'Train ID is required!'}), 400

    current_user = token_required()
    if isinstance(current_user, dict):
        return current_user

    user_id = current_user.id

    train = Train.query.filter_by(id=train_id).with_for_update().first()
    if not train:
        return jsonify({'error': 'Train not found!'}), 404

    if train.available_seats <= 0:
        return jsonify({'error': 'No seats available on this train!'}), 400

    Train.available_seats -= seats_to_book
    booking = (BookingDetails(user_id=user_id, train_id=train_id, seats_booked=seats_to_book, booking_time=datetime.utcnow()))
    db.session.add(booking)
    db.session.commit()
    return jsonify({'message': f'{seats_to_book} seat(s) booked successfully!'}), 201


@app.route('/get_booking_details', methods=['GET'])
@jwt_required()
def get_booking_details():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({'message': 'Token is missing or invalid'}), 403

    bookings = BookingDetails.query.filter_by(user_id=user_id).all()
    if not bookings:
        return jsonify({'message': 'No bookings found for this user.'}), 404

    booking_details = []
    for booking in bookings:
        train = Train.query.get(booking.train_id)
        booking_details.append({
            'booking_id': booking.id,
            'train_name': train.name,
            'seats_booked': booking.seats_booked,
            'booking_time': booking.booking_time.isoformat(),
            'departure': train.departure_time.isoformat(),
            'arrival': train.arrival_time.isoformat()
        })
    return jsonify(booking_details), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)