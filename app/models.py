from . import db

# New association table for User-Team relationship
user_teams = db.Table('user_teams',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    password_reset = db.Column(db.Boolean, default=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    #team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    
    organization = db.relationship('Organization', back_populates='users')
    #team = db.relationship('Team', back_populates='users')
    teams = db.relationship('Team', secondary=user_teams, back_populates='users')
    key_values = db.relationship('KeyValue', back_populates='user')

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship('Organization', back_populates='teams')
    #users = db.relationship('User', back_populates='team')
    users = db.relationship('User', secondary=user_teams, back_populates='teams')
    key_values = db.relationship('KeyValue', back_populates='team')

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    users = db.relationship('User', back_populates='organization')
    teams = db.relationship('Team', back_populates='organization')
    key_values = db.relationship('KeyValue', back_populates='organization')

class KeyValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(150), nullable=False)
    value = db.Column(db.String(500), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)

    user = db.relationship('User', back_populates='key_values')
    organization = db.relationship('Organization', back_populates='key_values')
    team = db.relationship('Team', back_populates='key_values')

    __table_args__ = (
        db.UniqueConstraint('key', 'level', 'user_id', 'organization_id', 'team_id', name='uq_key_value'),
    )