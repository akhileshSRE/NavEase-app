from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from app.models import KeyValue
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        key = request.form['key']
        value = request.form['value']
        if KeyValue.query.filter_by(key=key).first():
            flash('Key already exists')
        else:
            new_key_value = KeyValue(key=key, value=value)
            db.session.add(new_key_value)
            db.session.commit()
            flash('Key-value pair added')
    key_values = KeyValue.query.all()
    return render_template('dashboard.html', key_values=key_values)

@bp.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "ok"}), 200
