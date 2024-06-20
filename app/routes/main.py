from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from app.models import KeyValue, User, Organization, Team
from app import db
from app.decorators import login_required

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    
    personal_key_values = KeyValue.query.filter_by(user_id=user.id, level='personal').all()
    team_key_values = KeyValue.query.filter_by(team_id=user.team_id, level='team').all()
    org_key_values = KeyValue.query.filter_by(organization_id=user.organization_id, level='organization').all()
    
    return render_template('dashboard.html', 
                           personal_key_values=personal_key_values,
                           team_key_values=team_key_values,
                           org_key_values=org_key_values)


@bp.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "ok"}), 200
