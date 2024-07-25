from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from config import db, bcrypt
from sqlalchemy.orm import validates


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    
    recipes = db.relationship("Recipe", backref="user")

    @property
    def password_hash(self):
        raise AttributeError('password_hash is not readable')

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('Username must be provided')
        return username
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)    
    creator = db.relationship('User', backref='created_recipes')

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError('Title must be provided')
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if len(instructions) < 50:
            raise ValueError('Instructions must be at least 50 characters long')
        return instructions