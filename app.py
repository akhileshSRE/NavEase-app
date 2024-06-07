from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app)  # Enable CORS for all routes
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    password_reset = db.Column(db.Boolean, default=False)

class KeyValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(150), unique=True, nullable=False)
    value = db.Column(db.String(500), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin'), is_admin=True, password_reset=False)
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return jsonify({'redirect': url_for('dashboard')}), 200
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            if user.is_admin and not user.password_reset:
                return jsonify({'redirect': url_for('reset_password')}), 200
            return jsonify({'redirect': url_for('dashboard')}), 200
        return jsonify({'message': 'Invalid username or password'}), 401
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        new_password = request.form['password']
        user.password = generate_password_hash(new_password)
        user.password_reset = True
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('reset_password.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
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

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "ok"}), 200

@app.route('/api/v1/url', methods=['GET'])
def get_urls():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    key_values = KeyValue.query.all()
    response = {kv.key: kv.value for kv in key_values}
    return jsonify(response), 200

@app.route('/api/v1/update', methods=['POST'])
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

@app.route('/api/v1/delete', methods=['DELETE'])
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

if __name__ == '__main__':
    app.run(debug=True)
