from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import User, Customer
from __init__ import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        sort_by = request.args.get('sort_by', 'organization')  # Default to sorting by organization
        sort_order = request.args.get('sort_order', 'asc')

        if sort_by == 'name':
            query = Customer.query.order_by(Customer.name.asc() if sort_order == 'asc' else Customer.name.desc())
        elif sort_by == 'lastname':
            query = Customer.query.order_by(Customer.lastname.asc() if sort_order == 'asc' else Customer.lastname.desc())
        elif sort_by == 'age':
            query = Customer.query.order_by(Customer.age.asc() if sort_order == 'asc' else Customer.age.desc())
        elif sort_by == 'insurance_premium':
            query = Customer.query.order_by(Customer.insurance_premium.asc() if sort_order == 'asc' else Customer.insurance_premium.desc())
        elif sort_by == 'organization':
            query = Customer.query.order_by(Customer.organization.asc() if sort_order == 'asc' else Customer.organization.desc())
        else:
            query = Customer.query.order_by(Customer.organization.asc())  # Fallback to default sort

        customers = query.all()
        users = User.query.all()

        return render_template('dashboard.html', user_id=session['user_id'], users=users, customers=customers, sort_by=sort_by, sort_order=sort_order)
    else:
        return redirect(url_for('login'))
    
@dashboard_bp.route('/customer/<int:customer_id>')
def customer_page(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return render_template('customer_page.html', customer=customer)


@dashboard_bp.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        organization = request.form['organization']

        name = name.upper() if name else ''
        lastname = lastname.upper() if lastname else ''
        organization = organization.upper() if organization else ''
        
        age = request.form['age']
        insurance_premium = request.form['insurance_premium']

        new_customer = Customer(name=name, lastname=lastname, age=age, insurance_premium=insurance_premium, organization=organization)
        db.session.add(new_customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('add_customer.html')


@dashboard_bp.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if request.method == 'POST':
        customer.name = request.form['name'].upper
        customer.lastname = request.form['lastname'].upper
        customer.age = request.form['age']
        customer.insurance_premium = request.form['insurance_premium']
        customer.organization = request.form['organization'].upper
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('edit_customer.html', customer=customer)

@dashboard_bp.route('/delete_customer/<int:customer_id>')
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully.', 'success')
    else:
        flash('Customer not found.', 'danger')
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/organization/<string:organization_name>')
def organization_page(organization_name):
    customers = Customer.query.filter_by(organization=organization_name).all()

    if not customers:
        flash(f"No customers found for organization: {organization_name}", 'danger')
        return redirect(url_for('dashboard.dashboard'))

    min_age = min(customer.age for customer in customers)
    max_age = max(customer.age for customer in customers)
    total_premium = sum(customer.insurance_premium for customer in customers)

    return render_template('organization_page.html', 
                           organization_name=organization_name, 
                           min_age=min_age, 
                           max_age=max_age, 
                           total_premium=total_premium, 
                           customers=customers)


@dashboard_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
