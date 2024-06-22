from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('main.dashboard'))
        return render_template('login.html')
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            if user.is_admin and not user.password_reset:
                return jsonify({'redirect': url_for('auth.reset_password')}), 200
            return jsonify({'redirect': url_for('main.dashboard')}), 200
        return jsonify({'message': 'Invalid username or password'}), 401
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))

@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        new_password = request.form['password']
        user.password = generate_password_hash(new_password)
        user.password_reset = True
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('reset_password.html')
