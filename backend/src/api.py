from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id.desc()).all()
        short_repr = [ drink.short() for drink in drinks ]

        return jsonify({
            'success': True,
            'message': 'Drinks fetched Successfully',
            'drinks': short_repr
        })
    except:
        abort(400)
        

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(user):
    try:
        drinks = Drink.query.order_by(Drink.id.desc()).all()

        long_repr = [ drink.long() for drink in drinks ]

        return jsonify({
            'success': True,
            'message': 'Drink fetched successfully',
            'drinks': long_repr
        })

    except:
        abort(400)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(user):
    data = request.get_json()
    title = data.get('title')
    recipe = data.get('recipe')

    try:
        if data is None:
            return jsonify({
                'success': False,
                'message': 'Please provide Coffee'
            })
        else:
            if title is None:
                return jsonify({
                    'success': False,
                    'message': 'Please provide coffee title'
                })
            if recipe is None:
                return jsonify({
                    'success': False,
                    'message': 'Please provide coffee recipe'
                })
            
            formatted_recipe = json.dumps(recipe)
            newCoffee = Drink(title=title, recipe=formatted_recipe)

            if bool(Drink.query.filter_by(title=title).first()):
                return jsonify({
                    'success': False,
                    'message': f'A coffee with the title {title} already exist, change your title'
                })
            
            newCoffee.insert()

            return jsonify({
                'success': True,
                'message': 'Drink added successfully',
                'drinks': [ newCoffee.long() ]
            })
    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(user,drink_id):
    data = request.get_json()

    title = data.get('title')
    recipe = data.get('recipe')
    formatted_recipe = json.dumps(recipe)

    try:
        drink = Drink.query.filter_by(id=drink_id).first()
        if drink is None:
            abort(404)
        
        drink.title = title
        drink.recipe = formatted_recipe
        drink.insert()

        return jsonify({
            'success': True,
            'message': 'Drink updated successfully',
            'drinks': [ drink.long() ]
        })
        
    except:
        abort(400)


@requires_auth('delete:drinks')
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
def delete_drink(drink_id):
    try:
        drink = Drink.query.filter_by(id=drink_id).first()
        if drink == None:
            return jsonify({
            'success': False,
            'message': 'Drink not found',
        })
        drink.delete()
        return jsonify({
            'success': True,
            'message': 'Drink deleted successfully',
            'deleted': drink.id
        })
    except Exception as e:
        print(str(e))
        abort(400)



@app.errorhandler(400)
def badrequest(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request, Please check your request.'
    }), 400

@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify(error.error)

@app.errorhandler(404)
def notfound(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Item not found, check the item id again.'
    }), 404

@app.errorhandler(405)
def methodnotallowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method not Allowed, check your request method.'
    }), 405

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable, check your request."
    }), 422

@app.errorhandler(500)
def servererror(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Server Error, please contact the backend person"
    }), 500
