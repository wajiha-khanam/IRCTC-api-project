# Railway Management API
 This is a Flask-based Railway Management API that allows users to register, log in, check train seat availability, book seats, and view their booking details. Admins can add new trains to the system.
## Features
* User Authentication: JWT-based authentication for users and admin.
* Train Management: Admin can add new trains.
* Availability: Users can view available seats on specific routes.
* Booking: Users can book seats on trains.
* Booking Details: Users can view their booking history.
## Technologies Used
* Flask (Python Web Framework)
* PostgreSQL (Database)
* SQLAlchemy (ORM)
* JWT (Authentication)
* Pycharm (Development IDE)
## **Setup Instructions**
## Prerequisites
* Python 3.10
* PostgreSQL installed and running
## API Endpoints
### 1. Register a User
* URL: /register
* Method: POST
* Description: Registers a new user.
* Payload:
{
  "username": "user123",
  "password": "password123",
  "role": "user" }
## 2. Login a User
* URL: /login
* Method: POST
* Description: Logs in the user and returns a JWT token.
* Payload:
{
  "username": "user123",
  "password": "password123" }
## 3. Add a Train (Admin Only)
* URL: /admin/add_train
* Method: POST
* Description: Admin can add a new train.
* Payload:
{
  "name": "Train A",
  "source": "Station A",
  "destination": "Station B",
  "departure_time": "2024-09-24T10:00:00",
  "arrival_time": "2024-09-24T14:00:00",
  "total_seats": 100,
  "available_seats": 100,
  "price": 50.00 }
## 4. Check Seat Availability
* URL: /seat_availability
* Method: GET
* Description: View seat availability for a specific train route.
* Params:
(source: The departure station. 
destination: The destination station.)
## 5. Book a Seat
* URL: /book_seat
* Method: POST
* JWT Required: Yes
* Description: Book seats on a train.
* Payload:
{
  "train_id": 1,
  "seats_to_book": 2 }
## 6. View Booking Details
* URL: /get_booking_details
* Method: GET
* JWT Required: Yes
* Description: View the booking history of the user.
