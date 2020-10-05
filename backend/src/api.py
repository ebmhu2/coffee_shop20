# third-party imports
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

# local imports
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
 uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()


@app.route('/drinks', methods=['GET'])
def get_drinks():
    """
        handles GET requests to retrieve all drinks
    """
    try:
        # get all available drinks.
        all_drinks = Drink.query.order_by(Drink.id).all()

        # return success response in json format to view
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in all_drinks]
        })
    except:
        # abort 404 if no drinks found
        abort(404)


@app.route('/drinks-detail', methods=['GET'])
# require the 'get:drinks-detail' permission
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):
    """
        handles GET requests to GET /drinks-detail
    """
    try:
        # get all available drinks.
        all_drinks = [drink.long() for drink in Drink.query.all()]

        # return success response in json format to view
        return jsonify({
            'success': True,
            'drinks': all_drinks
        })
    except:
        # abort 404 if no drinks found
        abort(404)


@app.route('/drinks', methods=['POST'])
# require the 'post:drinks' permission
@requires_auth('post:drinks')
def post_drink(jwt):
    """
        handles POST requests to create new drink
    """
    try:
        # get data from front end
        data = request.get_json()
        if 'title' and 'recipe' not in data:
            abort(422)

        title = data['title']
        recipe_json = json.dumps(data['recipe'])

        # create a new row in the drinks table
        drink = Drink(title=title, recipe=recipe_json)
        drink.insert()

        # return success response in json format to view
        return jsonify({
            'success': True,
            'drinks': [drink.long()]  # contain the drink.long() data.
        })
    except:
        # abort unprocessable if exception
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
# require the 'patch:drinks' permission
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    """
        handles PATCH request to update drinks
    """
    try:
        # get the matching drink
        drink = Drink.query.get_or_404(id)

        # 404 error if <id> is not found
        if drink is None:
            abort(404)

        # get data from front end
        data = request.get_json()
        if 'title' in data:
            drink.title = data['title']

        if 'recipe' in data:
            drink.recipe = json.dumps(data['recipe'])

        # update the corresponding row for <id>
        drink.update()

        # return success response in json format to view
        return jsonify({
            'success': True,
            'drinks': [drink.long()]  # contain the drink.long() data
        })
    except:
        # 404 if no results found
        abort(404)


@app.route('/drinks/<int:id>', methods=['DELETE'])
# require the 'delete:drinks' permission
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    try:
        # get the matching drink
        drink = Drink.query.get_or_404(id)

        # 404 error if <id> is not found
        if drink is None:
            abort(404)

        # delete the corresponding row for <id>
        drink.delete()

        # return success response in json format to view
        return jsonify({
            'success': True,
            'delete': drink.id
        })
    except:
        # 404 if no results found
        abort(404)


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    """
        error handlers for 422 unprocessable entity
    """
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    """
        error handlers for 404
    """
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    """
        error handlers for 401
    """
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    """
        error handlers for 403
    """
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403


@app.errorhandler(AuthError)
def process_auth_error(error):
    """
        error handlers for AuthError
    """
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response