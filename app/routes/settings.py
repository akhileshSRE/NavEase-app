from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import User, Organization, Team
from app.decorators import login_required, admin_required
from app import db
from werkzeug.security import generate_password_hash

bp = Blueprint('settings', __name__)

@bp.route('/settings/users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        organization_id = request.form['organization']
        team_id = request.form['team']
        user = User(username=username, email=email, first_name=first_name, last_name=last_name,
                    password=generate_password_hash(password), organization_id=organization_id, team_id=team_id)
        db.session.add(user)
        db.session.commit()
        flash('User added successfully.')
        return redirect(url_for('settings.manage_users'))

    users = User.query.all()
    organizations = Organization.query.all()
    teams = Team.query.all()
    return render_template('settings/manage_users.html', users=users, organizations=organizations, teams=teams)

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
    return render_template('settings/manage_organizations.html', organizations=organizations)

@bp.route('/settings/teams', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_teams():
    if request.method == 'POST':
        name = request.form['name']
        organization_id = request.form['organization']
        team = Team(name=name, organization_id=organization_id)
        db.session.add(team)
        db.session.commit()
        flash('Team added successfully.')
        return redirect(url_for('settings.manage_teams'))

    teams = Team.query.all()
    organizations = Organization.query.all()
    return render_template('settings/manage_teams.html', teams=teams, organizations=organizations)
