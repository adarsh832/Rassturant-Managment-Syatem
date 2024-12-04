from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import MenuItem, Order, OrderItem, User, Reservation, CustomerOrder, Table
from app import db
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
from flask import abort
from sqlalchemy import inspect

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def dashboard():
    # Get dashboard statistics
    active_orders = Order.query.filter_by(status='pending').count()
    customer_orders = CustomerOrder.query.filter_by(status='paid').count()
    menu_items = MenuItem.query.count()
    
    # Get table status
    tables = Table.query.order_by(Table.table_number).all()
    available_tables = Table.query.filter_by(status='available').count()
    
    # Get orders by status
    pending_orders = Order.query.filter_by(status='pending').all()
    preparing_orders = Order.query.filter_by(status='preparing').all()
    completed_orders = Order.query.filter_by(status='completed').all()
    
    # Calculate revenue
    today_orders = Order.query.filter(
        Order.timestamp >= date.today()
    ).all()
    
    today_customer_orders = CustomerOrder.query.filter(
        CustomerOrder.timestamp >= date.today()
    ).all()
    
    restaurant_revenue = sum(
        item.menu_item.price * item.quantity
        for order in today_orders
        for item in order.items
    )
    
    customer_revenue = sum(order.total_amount for order in today_customer_orders)
    total_revenue = restaurant_revenue + customer_revenue
    
    # Get payment status for orders
    unpaid_orders = CustomerOrder.query.filter_by(payment_status='pending').count()
    paid_orders = CustomerOrder.query.filter_by(payment_status='completed').count()
    
    return render_template('dashboard.html',
                         active_orders=active_orders,
                         customer_orders=customer_orders,
                         today_revenue="{:.2f}".format(total_revenue),
                         menu_items=menu_items,
                         tables=tables,
                         available_tables=available_tables,
                         total_tables=len(tables),
                         pending_orders=pending_orders,
                         preparing_orders=preparing_orders,
                         completed_orders=completed_orders,
                         unpaid_orders=unpaid_orders,
                         paid_orders=paid_orders)

@main.route('/menu')
@login_required
def menu():
    menu_items = MenuItem.query.all()
    return render_template('menu.html', menu_items=menu_items)

@main.route('/menu/add', methods=['POST'])
@login_required
def add_menu_item():
    if not current_user.is_admin:
        flash('Only administrators can add menu items')
        return redirect(url_for('main.menu'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    price = float(request.form.get('price'))
    category = request.form.get('category')
    
    item = MenuItem(name=name, description=description, 
                   price=price, category=category)
    db.session.add(item)
    db.session.commit()
    
    flash('Menu item added successfully!')
    return redirect(url_for('main.menu'))

@main.route('/orders')
@login_required
def orders():
    orders = Order.query.order_by(Order.timestamp.desc()).all()
    menu_items = MenuItem.query.all()
    return render_template('orders.html', orders=orders, menu_items=menu_items)

@main.route('/create-order', methods=['POST'])
@login_required
def create_order():
    table_number = request.form.get('table_number')
    items = request.form.getlist('items[]')
    quantities = request.form.getlist('quantities[]')
    
    if not table_number or not items:
        flash('Invalid order data')
        return redirect(url_for('main.orders'))
    
    order = Order(table_number=table_number, status='pending')
    db.session.add(order)
    db.session.flush()
    
    for item_id, quantity in zip(items, quantities):
        quantity = int(quantity)
        if quantity > 0:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=int(item_id),
                quantity=quantity
            )
            db.session.add(order_item)
    
    try:
        db.session.commit()
        flash('Order created successfully!')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating order: {str(e)}')
    
    return redirect(url_for('main.orders'))

@main.route('/update-order-status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    if status in ['pending', 'preparing', 'ready', 'served', 'cancelled']:
        order.status = status
        db.session.commit()
        flash('Order status updated!')
    return redirect(url_for('main.orders'))

@main.route('/delete-menu-item/<int:item_id>', methods=['POST'])
@login_required
def delete_menu_item(item_id):
    if not current_user.is_admin:
        flash('Only administrators can delete menu items')
        return redirect(url_for('main.menu'))
    
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Menu item deleted successfully!')
    return redirect(url_for('main.menu'))

@main.route('/staff')
@login_required
def staff_list():
    if not current_user.is_admin:
        abort(403)
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('staff/list.html', users=users)

@main.route('/staff/add', methods=['GET', 'POST'])
@login_required
def add_staff():
    if not current_user.is_admin:
        abort(403)
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('main.add_staff'))
            
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            name=name,
            role=role,
            email=email,
            phone=phone,
            is_admin=(role == 'admin')
        )
        
        db.session.add(user)
        db.session.commit()
        flash('Staff member added successfully!')
        return redirect(url_for('main.staff_list'))
        
    return render_template('staff/add.html')

@main.route('/staff/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_staff(user_id):
    if not current_user.is_admin:
        abort(403)
        
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.role = request.form.get('role')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.is_active = 'is_active' in request.form
        user.is_admin = (request.form.get('role') == 'admin')
        
        if request.form.get('password'):
            user.password_hash = generate_password_hash(request.form.get('password'))
            
        db.session.commit()
        flash('Staff member updated successfully!')
        return redirect(url_for('main.staff_list'))
        
    return render_template('staff/edit.html', user=user)

@main.route('/staff/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_staff(user_id):
    if not current_user.is_admin:
        abort(403)
        
    if user_id == current_user.id:
        flash('Cannot delete your own account!')
        return redirect(url_for('main.staff_list'))
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Staff member deleted successfully!')
    return redirect(url_for('main.staff_list'))

@main.route('/reservations')
@login_required
def reservations():
    upcoming = Reservation.query.filter(
        Reservation.date >= date.today()
    ).order_by(Reservation.date, Reservation.time).all()
    
    past = Reservation.query.filter(
        Reservation.date < date.today()
    ).order_by(Reservation.date.desc(), Reservation.time.desc()).limit(10).all()
    
    return render_template('reservations/list.html', 
                         upcoming_reservations=upcoming,
                         past_reservations=past)

@main.route('/reservations/add', methods=['GET', 'POST'])
@login_required
def add_reservation():
    if request.method == 'POST':
        # Convert date and time strings to Python objects
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        
        reservation = Reservation(
            customer_name=request.form.get('customer_name'),
            customer_email=request.form.get('customer_email'),
            customer_phone=request.form.get('customer_phone'),
            date=datetime.strptime(date_str, '%Y-%m-%d').date(),
            time=datetime.strptime(time_str, '%H:%M').time(),
            number_of_guests=int(request.form.get('number_of_guests')),
            table_number=request.form.get('table_number'),
            special_requests=request.form.get('special_requests'),
            status='confirmed'
        )
        
        db.session.add(reservation)
        db.session.commit()
        flash('Reservation added successfully!')
        return redirect(url_for('main.reservations'))
        
    return render_template('reservations/add.html', datetime=datetime)

@main.route('/reservations/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    
    if request.method == 'POST':
        reservation.customer_name = request.form.get('customer_name')
        reservation.customer_email = request.form.get('customer_email')
        reservation.customer_phone = request.form.get('customer_phone')
        reservation.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        reservation.time = datetime.strptime(request.form.get('time'), '%H:%M').time()
        reservation.number_of_guests = int(request.form.get('number_of_guests'))
        reservation.table_number = request.form.get('table_number')
        reservation.special_requests = request.form.get('special_requests')
        reservation.status = request.form.get('status')
        
        db.session.commit()
        flash('Reservation updated successfully!')
        return redirect(url_for('main.reservations'))
        
    return render_template('reservations/edit.html', reservation=reservation, datetime=datetime)

@main.route('/reservations/cancel/<int:id>', methods=['POST'])
@login_required
def cancel_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    reservation.status = 'cancelled'
    db.session.commit()
    flash('Reservation cancelled successfully!')
    return redirect(url_for('main.reservations'))

@main.route('/database/tables')
@login_required
def view_tables():
    if not current_user.is_admin:
        abort(403)
        
    inspector = inspect(db.engine)
    tables = {}
    
    for table_name in inspector.get_table_names():
        records = db.session.execute(db.select(db.Model.metadata.tables[table_name])).all()
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        table_data = []
        for record in records:
            table_data.append(dict(zip(columns, record)))
        tables[table_name] = table_data
    
    return render_template('database/view.html', tables=tables)

@main.route('/update-customer-order/<int:order_id>', methods=['POST'])
@login_required
def update_customer_order_status(order_id):
    if not current_user.is_admin:
        flash('Only administrators can update order status')
        return redirect(url_for('main.dashboard'))
    
    order = CustomerOrder.query.get_or_404(order_id)
    status = request.form.get('status')
    
    if status in ['preparing', 'delivered']:
        order.status = status
        db.session.commit()
        flash('Order status updated successfully!')
    
    return redirect(url_for('main.dashboard'))

@main.route('/manage-tables', methods=['GET', 'POST'])
@login_required
def manage_tables():
    if not current_user.is_admin:
        flash('Only administrators can manage tables')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        table_number = int(request.form.get('table_number'))
        capacity = int(request.form.get('capacity'))
        
        # Check if table number already exists
        existing_table = Table.query.filter_by(table_number=table_number).first()
        if existing_table:
            flash('Table number already exists')
            return redirect(url_for('main.manage_tables'))
        
        table = Table(
            table_number=table_number,
            capacity=capacity,
            status='available'
        )
        db.session.add(table)
        db.session.commit()
        
        flash('Table added successfully!')
        return redirect(url_for('main.manage_tables'))
    
    tables = Table.query.order_by(Table.table_number).all()
    return render_template('manage_tables.html', tables=tables)

@main.route('/update-table-status/<int:table_id>', methods=['POST'])
@login_required
def update_table_status(table_id):
    table = Table.query.get_or_404(table_id)
    status = request.json.get('status')
    
    if status in ['available', 'occupied', 'reserved']:
        table.status = status
        db.session.commit()
        return jsonify({'success': True})
        
    return jsonify({'success': False}), 400