from flask import Blueprint, request, jsonify, session
from app.models import KeyValue
from app import db
from app.decorators import login_required
from app.models import KeyValue, User, Organization, Team 
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging


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

    if user.is_admin:
        # For admin, get all team and organization key-values
        team_kvs = KeyValue.query.filter_by(level='team').all()
        org_kvs = KeyValue.query.filter_by(level='organization').all()
    else:
        # Get team key-values for all teams the user is in
        user_team_ids = [team.id for team in user.teams]
        team_kvs = KeyValue.query.filter(KeyValue.level == 'team', KeyValue.team_id.in_(user_team_ids)).all()

        # Get organization key-values if user is in an organization
        org_kvs = []
        if user.organization_id:
            org_kvs = KeyValue.query.filter_by(organization_id=user.organization_id, level='organization').all()

    # Combine all authorized key-values
    all_kvs = personal_kvs + team_kvs + org_kvs
    logging.debug(all_kvs)
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
    data = request.json
    key = data.get('key')
    value = data.get('value')
    level = data.get('level')
    
    if not all([key, value, level]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        user = User.query.get(session['user_id'])
        
        # Check if key already exists
        if KeyValue.query.filter_by(key=key).first():
            return jsonify({"error": "This key already exists"}), 409
        
        if level == 'organization':
            organization_id = data.get('organization_id')
            if not organization_id:
                return jsonify({"error": "Organization ID is required for organization level"}), 400
            org = Organization.query.get(organization_id)
            if not org:
                return jsonify({"error": "Invalid organization ID"}), 400
            new_kv = KeyValue(key=key, value=value, level=level, organization_id=organization_id)
            db.session.add(new_kv)
            org_name = org.name
            team_names = None
        elif level == 'team':
            team_ids = data.get('team_ids', [])
            if not team_ids:
                return jsonify({"error": "Team IDs are required for team level"}), 400
            team_names = []
            for team_id in team_ids:
                team = Team.query.get(team_id)
                if team:
                    team_names.append(team.name)
                    team_kv = KeyValue(key=key, value=value, level=level, team_id=team_id)
                    db.session.add(team_kv)
            org_name = None
        else:  # personal level
            new_kv = KeyValue(key=key, value=value, level=level, user_id=user.id)
            db.session.add(new_kv)
            org_name = None
            team_names = None
        
        db.session.commit()
        
        new_entry = {
            'key': key,
            'value': value,
            'level': level,
            'organization_name': org_name,
            'team_names': team_names
        }
        
        return jsonify({"message": "Key-value pair added successfully", "newEntry": new_entry}), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"SQLAlchemyError: {str(e)}")
        return jsonify({"error": "An error occurred while saving the key-value pair"}), 500
    except Exception as e:
        db.session.rollback()
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    
@bp.route('/api/v1/check_key', methods=['POST'])
@login_required
def check_key():
    data = request.json
    key = data.get('key')

    exists = KeyValue.query.filter_by(key=key).first() is not None

    return jsonify({"exists": exists}), 200