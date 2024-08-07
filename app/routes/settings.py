from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User, Organization, Team
from app.decorators import login_required, admin_required
from app import db
from werkzeug.security import generate_password_hash

bp = Blueprint('settings', __name__)

@bp.route('/settings', methods=['GET'])
@login_required
@admin_required
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    return render_template('settings.html', user=user)

@bp.route('/settings/users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            username = request.form.get('username')
            email = request.form.get('email')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            password = request.form.get('password')
            organization_id = request.form.get('organization')
            team_ids = request.form.getlist('teams')
            
            if not all([username, email, first_name, last_name, password, organization_id]):
                flash('All fields are required.', 'error')
            else:
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=generate_password_hash(password),
                    organization_id=organization_id
                )
                for team_id in team_ids:
                    team = Team.query.get(team_id)
                    if team:
                        user.teams.append(team)
                db.session.add(user)
                db.session.commit()
                flash('User added successfully.', 'success')
        
        elif action == 'update_org':
            user_id = request.form.get('user_id')
            organization_id = request.form.get('organization')
            user = User.query.get(user_id)
            if user:
                user.organization_id = organization_id
                db.session.commit()
                flash('User organization updated successfully.', 'success')
        
        elif action == 'update_teams':
            user_id = request.form.get('user_id')
            team_ids = request.form.getlist('teams')
            user = User.query.get(user_id)
            if user:
                user.teams = []
                for team_id in team_ids:
                    team = Team.query.get(team_id)
                    if team:
                        user.teams.append(team)
                db.session.commit()
                flash('User teams updated successfully.', 'success')
        
        elif action == 'delete':
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash('User deleted successfully.', 'success')
        
        return redirect(url_for('settings.manage_users'))

    users = User.query.all()
    organizations = Organization.query.all()
    teams = Team.query.all()
    user = User.query.get(session['user_id'])
    return render_template('settings/manage_users.html', users=users, organizations=organizations, teams=teams, user=user)

@bp.route('/settings/organizations', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_organizations():
    if request.method == 'POST':
        name = request.form['name']
        organization = Organization(name=name)
        db.session.add(organization)
        db.session.commit()
        flash('Organization added successfully.')
        return redirect(url_for('settings.manage_organizations'))

    organizations = Organization.query.all()
    user = User.query.get(session['user_id'])
    return render_template('settings/manage_organizations.html', organizations=organizations, user=user)

@bp.route('/settings/teams', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_teams():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            organization_id = request.form.get('organization')
            
            if not all([name, organization_id]):
                flash('All fields are required.', 'error')
            else:
                team = Team(name=name, organization_id=organization_id)
                db.session.add(team)
                db.session.commit()
                flash('Team added successfully.', 'success')
        
        elif action == 'delete':
            team_id = request.form.get('team_id')
            team = Team.query.get(team_id)
            if team:
                db.session.delete(team)
                db.session.commit()
                flash('Team deleted successfully.', 'success')
            else:
                flash('Team not found.', 'error')
        
        return redirect(url_for('settings.manage_teams'))

    teams = Team.query.all()
    organizations = Organization.query.all()
    user = User.query.get(session['user_id'])
    return render_template('settings/manage_teams.html', teams=teams, organizations=organizations, user=user)