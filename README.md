# Restaurant Management System

A comprehensive web-based restaurant management system built with Flask that helps restaurant owners and staff manage their daily operations efficiently.

## Features

### 1. Dashboard
- View active orders
- Track daily revenue
- Monitor menu items
- See recent orders

### 2. Menu Management
- Add new menu items
- Set prices and descriptions
- Categorize items (Starters, Main Course, Desserts, etc.)
- Delete menu items

### 3. Order Management
- Create new orders
- Select table numbers
- Choose multiple items with quantities
- Track order status (pending, preparing, ready, served, cancelled)
- Update order status in real-time

### 4. Reservation System
- Book tables for customers
- Manage upcoming and past reservations
- Handle special requests
- Track table assignments

### 5. Staff Management (Admin Only)
- Add/Edit staff members
- Assign roles (admin, staff, kitchen)
- Manage staff access
- Track staff information

### 6. Database Viewer (Admin Only)
- View all database tables
- Monitor system data

## Installation

1. Clone the repository:
git clone <repository-url>
cd restaurant-management

2. Create a virtual environment:
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate

3. Install required packages:
pip install -r requirements.txt

4. Run the application:
python run.py

5. Access the system at: http://127.0.0.1:5000

## Default Login Credentials
- Username: admin
- Password: admin123

## Project Structure
restaurant_management/
├── app/
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── menu.html
│   │   ├── orders.html
│   │   ├── login.html
│   │   ├── reservations/
│   │   ├── staff/
│   │   └── database/
│   ├── models.py
│   ├── routes.py
│   └── auth.py
├── config.py
├── requirements.txt
└── run.py

## Technologies Used
- Flask (Python web framework)
- SQLAlchemy (Database ORM)
- Flask-Login (Authentication)
- Bootstrap 5 (Frontend styling)
- SQLite (Database)
- Jinja2 (Template engine)

## User Roles

### Admin
- Full access to all features
- Can manage staff members
- Can view database tables
- Can modify menu items
- Can access all reports

### Staff
- Can manage orders
- Can handle reservations
- Can view menu items
- Can update order status

### Kitchen Staff
- Can view and update order status
- Can view menu items
- Can mark orders as prepared

## Support
For support, please contact: [your-email]