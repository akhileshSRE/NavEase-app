from flask import Blueprint, request, jsonify, session
from app.models import KeyValue
from app import db
from app.decorators import login_required
from app.models import KeyValue, User, Organization, Team 
from sqlalchemy.orm import joinedload


bp = Blueprint('api', __name__)

@bp.route('/api/v1/url', methods=['GET'])
@login_required
def get_urls():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get personal key-values
    personal_kvs = KeyValue.query.filter_by(user_id=user.id, level='personal').all()

    # Get team key-values if user is in a team
    team_kvs = []
    if user.team_id:
        team_kvs = KeyValue.query.filter_by(team_id=user.team_id, level='team').all()

    # Get organization key-values if user is in an organization
    org_kvs = []
    if user.organization_id:
        org_kvs = KeyValue.query.filter_by(organization_id=user.organization_id, level='organization').all()

    # Combine all authorized key-values
    all_kvs = personal_kvs + team_kvs + org_kvs

    # Create response dictionary
    response = {}
    for kv in all_kvs:
        response[kv.key] = kv.value

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
        organization_id = data.get('organization_id')
        if not organization_id:
            return jsonify({"error": "Organization ID is required for organization level"}), 400
        new_key_value.organization_id = organization_id
        org = Organization.query.get(organization_id)
        org_name = org.name if org else 'N/A'
    elif level == 'team':
        team_id = data.get('team_id')
        if not team_id:
            return jsonify({"error": "Team ID is required for team level"}), 400
        new_key_value.team_id = team_id
        team = Team.query.get(team_id)
        team_name = team.name if team else 'N/A'
    else:
        return jsonify({"error": "Invalid level"}), 400
    
    db.session.add(new_key_value)
    db.session.commit()
    
    new_entry = {
        'key': new_key_value.key,
        'value': new_key_value.value,
        'level': new_key_value.level,
        'organization_name': org_name if level == 'organization' else None,
        'team_name': team_name if level == 'team' else None
    }
    
    return jsonify({"message": "Key-value pair added successfully", "newEntry": new_entry}), 201