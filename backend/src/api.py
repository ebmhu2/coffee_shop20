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

# ROUTES
"""
    handles GET requests to retrieve all drinks
"""
@app.route('/drinks', methods=['GET'])
def get_drinks():
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


"""
    handles GET requests to GET /drinks-detail
"""
@app.route('/drinks-detail', methods=['GET'])
# require the 'get:drinks-detail' permission
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):
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


'''
    handles POST requests to create new drink
'''
@app.route('/drinks', methods=['POST'])
# require the 'post:drinks' permission
@requires_auth('post:drinks')
def post_drink(jwt):
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
            'drinks': [drink.long()]  # contain the drink.long() data representation
        })
    except:
        # abort unprocessable if exception
        abort(422)


'''
    handles PATCH request to update drinks
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
# require the 'patch:drinks' permission
@requires_auth('patch:drinks')
def update_drink(jwt, id):
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
            'drinks': [drink.long()]  # contain the drink.long() data representation
    })
    except:
        # 404 if no results found
        abort(404)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


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
'''
    error handlers for 422 unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
    error handlers for 404
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
    error handlers for 401
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


'''
    error handlers for 403
'''
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403


'''
    error handlers for AuthError
'''
@app.errorhandler(AuthError)
def process_auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response