#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.json
        username = data.get('username')
        password = data.get('password')
        bio = data.get('bio')
        image_url = data.get('image_url')

        # Checking if required fields are provided
        if not (username and password):
            return {'message': 'Username and password are required'}, 422

        # Creatting a new user 
        new_user = User(username=username, bio=bio, image_url=image_url)
        new_user.password_hash = password  # Set the password hash

        # Adding the user to the databases    
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201

class CheckSession(Resource):
    def get(self):
        # Checking if user_id is in the session
        user_id = session.get('user_id')
        if user_id:
            # getting user data from the database
            user = User.query.get(user_id)
            if user:
                # Returning the user data in a dictionary
                return {
                    'id': user.id,
                    'username': user.username,
                    'bio': user.bio,
                    'image_url': user.image_url
                }, 200
        return {'message': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # Checking if username and password are provided
        if not (username and password):
            return {'message': 'Username and password are required'}, 400

        # getting the user in the database by username
        user = User.query.filter_by(username=username).first()

        # Checking if user exists and password is correct
        if user and user.authenticate(password):
            # Setting the user_id in the session
            session['user_id'] = user.id
            response = {
                'message': 'Login successful',
                'username': user.username
            }
            return response, 200
        else:
            response = {'message': 'Invalid username or password'}
            return response, 401
        
class Logout(Resource):
    def delete(self):
        try:
            # Checking if user_id is in the session
            user_id = session.get('user_id')
            if user_id:
                # Clearing the session to log out the user
                session.clear()
                return {'message': 'Logged out successfully'}, 200
            else:
                # if user is not logged in they are not authorised
                return {'message': 'Unauthorized'}, 401
        except KeyError:
            # if the user id is not in the session they are unauthorised
            return {'message': 'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        # Checking if user_id is in the session
        user_id = session.get('user_id')
        if user_id:
            # Getting all the recipes associated with the logged-in user
            recipes = Recipe.query.filter_by(user_id=user_id).all()
            
            # setting the recipe data
            recipe_data = []
            for recipe in recipes:
                recipe_data.append({
                    'title': recipe.title,
                    'instructions': recipe.instructions,
                    'minutes_to_complete': recipe.minutes_to_complete
                })
            return recipe_data, 200
        else:
            return {'message': 'Unauthorized'}, 401

    def post(self):
        # Checking if user_id is in the session
        user_id = session.get('user_id')
        if user_id:
            data = request.json
            
            # ensuring there is data input with the values
            if 'title' not in data or 'instructions' not in data or 'minutes_to_complete' not in data:
                return {'message': 'Invalid Recipes'}, 422
            
            # Creating a new recipe
            new_recipe = Recipe(
                title=data.get('title'),
                instructions=data.get('instructions'),
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=user_id
            )
            db.session.add(new_recipe)
            db.session.commit()
            
            
            response_data = {
                'title': new_recipe.title,
                'instructions': new_recipe.instructions,
                'minutes_to_complete': new_recipe.minutes_to_complete
            }
            return response_data, 201
        else:
            return {'message': 'Unauthorized'}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)