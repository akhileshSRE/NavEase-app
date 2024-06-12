from flask import Blueprint, request, jsonify, session
from app.models import KeyValue
from app import db

bp = Blueprint('api', __name__)

@bp.route('/api/v1/url', methods=['GET'])
def get_urls():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    key_values = KeyValue.query.all()
    response = {kv.key: kv.value for kv in key_values}
    return jsonify(response), 200

@bp.route('/api/v1/update', methods=['POST'])
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
