from flask import request, Blueprint, jsonify
from __init__ import db
from models import Customer

search_bp = Blueprint('search', __name__)

@search_bp.route('/customers', methods=['GET'])
def get_customers():
    query = Customer.query

    if 'name' in request.args:
        query = query.filter(Customer.name.ilike(f"%{request.args['name']}%"))

    if 'organization' in request.args:
        query = query.filter(Customer.organization.ilike(f"%{request.args['organization']}%"))

    if 'age_gt' in request.args:
        query = query.filter(Customer.age > int(request.args['age_gt']))

    if 'age_lt' in request.args:
        query = query.filter(Customer.age < int(request.args['age_lt']))

    if 'tag' in request.args:
        query = query.filter(Customer.tag.ilike(f"%{request.args['tag']}%"))

    customers = query.all()

    return jsonify([{
        'id': customer.id,
        'name': customer.name,
        'lastname': customer.lastname,
        'age': customer.age,
        'insurance_premium': customer.insurance_premium,
        'organization': customer.organization
    } for customer in customers])

@search_bp.route('/search_customers', methods=['GET'])
def search_customers():
    search_query = request.args.get('name', '').strip()
    query_parts = search_query.split()

    customer_query = Customer.query

    if len(query_parts) == 1:
        search_term = query_parts[0]
        customer_query = customer_query.filter(
            (Customer.id.ilike(f"%{search_term}%")) |
            (Customer.name.ilike(f"%{search_term}%")) |
            (Customer.lastname.ilike(f"%{search_term}%")) |
            (Customer.organization.ilike(f"%{search_term}%"))
        )
    elif len(query_parts) > 1:
        customer_query = customer_query.filter(
            (Customer.name.ilike(f"%{query_parts[0]}%")) &
            (Customer.lastname.ilike(f"%{query_parts[1]}%")) |
            (Customer.organization.ilike(f"%{search_query}%"))
        )

    if 'tag' in request.args:
        customer_query = customer_query.filter(Customer.tag.ilike(f"%{request.args['tag']}%"))

    customers = customer_query.order_by(Customer.name).all()

    organizations = db.session.query(Customer.organization).filter(
        Customer.organization.ilike(f"%{search_query}%")
    ).distinct().all()

    return jsonify({
        'customers': [{
            'id': customer.id,
            'name': customer.name,
            'lastname': customer.lastname,
            'organization': customer.organization
        } for customer in customers],
        'organizations': [{
            'organization': org.organization
        } for org in organizations]
    })
