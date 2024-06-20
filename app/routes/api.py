from flask import Blueprint, request, jsonify, session
from app.models import KeyValue
from app import db
from app.decorators import login_required
from app.models import KeyValue, User, Organization, Team 

bp = Blueprint('api', __name__)

@bp.route('/api/v1/url', methods=['GET'])
@login_required
def get_urls():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    key_values = KeyValue.query.all()
    response = {kv.key: kv.value for kv in key_values}
    return jsonify(response), 200

@bp.route('/api/v1/update', methods=['POST'])
@login_required
def update_url():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    key_value = KeyValue.query.filter_by(key=data['key']).first()
    if key_value:
        key_value.value = data['value']
        db.session.commit()
        return jsonify({"message": "Key-value pair updated"}), 200
    return jsonify({"error": "Key not found"}), 404

@bp.route('/api/v1/delete', methods=['DELETE'])
@login_required
def delete_url():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    key_value = KeyValue.query.filter_by(key=data['key']).first()
    if key_value:
        db.session.delete(key_value)
        db.session.commit()
        return jsonify({"message": "Key-value pair deleted"}), 200
    return jsonify({"error": "Key not found"}), 404

@bp.route('/api/v1/add', methods=['POST'])
@login_required
def add_url():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    key = data.get('key')
    value = data.get('value')
    level = data.get('level')
    
    if not all([key, value, level]):
        return jsonify({"error": "Missing required fields"}), 400
    
    if KeyValue.query.filter_by(key=key).first():
        return jsonify({"error": "Key already exists"}), 409
    
    user = User.query.get(session['user_id'])
    new_key_value = KeyValue(key=key, value=value, level=level)
    
    if level == 'personal':
        new_key_value.user_id = user.id
    elif level == 'organization':
        new_key_value.organization_id = user.organization_id
    elif level == 'team':
        new_key_value.team_id = user.team_id
    else:
        return jsonify({"error": "Invalid level"}), 400
    
    db.session.add(new_key_value)
    db.session.commit()
    
    return jsonify({"message": "Key-value pair added successfully"}), 201