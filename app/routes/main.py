from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from app.models import KeyValue, User, Organization, Team
from app import db
from app.decorators import login_required
from werkzeug.security import generate_password_hash, check_password_hash

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
    
    if user.is_admin:
        org_key_values = KeyValue.query.filter_by(level='organization').all()
        team_key_values = KeyValue.query.filter_by(level='team').all()
    else:
        org_key_values = KeyValue.query.filter_by(organization_id=user.organization_id, level='organization').all()
        
        user_team_ids = [team.id for team in user.teams]
        team_key_values = KeyValue.query.filter(KeyValue.level == 'team', KeyValue.team_id.in_(user_team_ids)).all()
    
    for kv in org_key_values:
        kv.org_name = Organization.query.get(kv.organization_id).name if kv.organization_id else 'N/A'
    
    # Group team key-values by key
    team_kv_dict = {}
    for kv in team_key_values:
        if kv.key not in team_kv_dict:
            team_kv_dict[kv.key] = {
                'value': kv.value,
                'team_ids': set()
            }
        team_kv_dict[kv.key]['team_ids'].add(kv.team_id)
    
    # Fetch all teams for each key
    for key, data in team_kv_dict.items():
        all_team_kvs = KeyValue.query.filter_by(key=key, level='team').all()
        for team_kv in all_team_kvs:
            data['team_ids'].add(team_kv.team_id)
    
    # Convert the dictionary back to a list of objects with all team names
    team_key_values = []
    for key, data in team_kv_dict.items():
        team_names = [Team.query.get(team_id).name for team_id in data['team_ids'] if Team.query.get(team_id)]
        team_key_values.append({
            'key': key,
            'value': data['value'],
            'team_names': ', '.join(sorted(team_names))  # Sort team names for consistent display
        })
    
    organizations = Organization.query.all()
    teams = Team.query.all()
    
    return render_template('dashboard.html', 
                           personal_key_values=personal_key_values,
                           team_key_values=team_key_values,
                           org_key_values=org_key_values,
                           user=user,
                           organizations=organizations,
                           teams=teams)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        if 'update_profile' in request.form:
            user.first_name = request.form['first_name']
            user.last_name = request.form['last_name']
            user.email = request.form['email']
            db.session.commit()
            flash('Profile updated successfully', 'success')
        elif 'change_password' in request.form:
            if check_password_hash(user.password, request.form['current_password']):
                if request.form['new_password'] == request.form['confirm_password']:
                    user.password = generate_password_hash(request.form['new_password'])
                    db.session.commit()
                    flash('Password changed successfully', 'success')
                else:
                    flash('New passwords do not match', 'error')
            else:
                flash('Current password is incorrect', 'error')
        return redirect(url_for('main.profile'))
    
    # Ensure the user's organization and teams are loaded
    user = User.query.options(db.joinedload(User.organization), db.joinedload(User.teams)).get(session['user_id'])
    return render_template('profile.html', user=user)


@bp.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "ok"}), 200
