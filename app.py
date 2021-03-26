"""Flask app for Cupcakes"""

from flask import Flask, jsonify, request, redirect, render_template, redirect, flash, session
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Cupcake, CUPCAKE_FIELDS, db_add_cupcake, db_update_cupcake, db_delete_cupcake
# from config import APP_KEY
# from forms import

app = Flask(__name__)

# Flask and SQL Alchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cupcakes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# app.config['SECRET_KEY'] = APP_KEY

# # debugtoolbar
# debug = DebugToolbarExtension(app)
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)


# API Routes

# GET /api/cupcakes
@app.route("/api/cupcakes")
def list_cupcakes_api():
    """ Get information about all cupcakes.

        JSON response: {cupcakes: [{id, flavor, size, rating, image}, ...]}.
    """
    cupcakes = Cupcake.query.all()
    serialized = [cupcake.serialize() for cupcake in cupcakes]

    return jsonify(cupcakes=serialized)


# GET /api/cupcakes/[cupcake-id]
@app.route("/api/cupcakes/<cupcake_id>")
def list_cupcake_api(cupcake_id):
    """ Get information about a single cupcake identified by cupcake_id.

        Do no coerce cupcake_id into an integer via <int:cupcake_id> because the route
        for a non-integer value does not exist and a 404 error results.

        JSON response: {cupcake: {id, flavor, size, rating, image}}.

        404 is raised when the cupcake identified by cupcake_id was not found or when
        cupcake_id is not an integer.

    """

    # only use cupcake_id for a db lookup when we know it is an integer
    if (cupcake_id.isnumeric()):
        cupcake = Cupcake.query.get(cupcake_id)
        if (cupcake):
            response_code = 200
            response_data = {
                "cupcake": cupcake.serialize()
            }

        else:
            response_code = 404
            response_data = {
                "error": {"message": f"Cupcake id={cupcake_id} was not found"}
            }

    else:
        response_code = 404
        response_data = {
            "error": {"message": f"Cupcake id='{cupcake_id}' was not an integer."}
        }

    return (jsonify(response_data), response_code)


# POST /api/cupcakes
@app.route("/api/cupcakes", methods=["POST"])
def create_cupcake_api():
    """ Create a cupcake with flavor, size, rating and image data from the body of
        the JSON request.

        Responds wtih
        201 on successful add with JSON Response {cupcake: {id, flavor, size, rating, image}} 
        400 on an error with JSON response {error: "An error occurred. Non-blank values 
          required for flavor, size, and rating. " } when required fields missing 
        400 on an error with JSON response {error: "An error occurred. " } when an unexpected
          error occurred.         

    """

    # print(
    #     f"\n\ncreate_cupcake_api: request.headers = {request.headers}", flush=True)

    cupcake_data = CUPCAKE_FIELDS

    for key in cupcake_data.keys():
        cupcake_data[key] = request.json.get(key, '')

    results = db_add_cupcake(cupcake_data)

    if (results["successful"]):
        # on success / okay, message contains serialized information for the new cupcake.
        response_data = {"cupcake": results["message"]}
        response_code = 201
    else:
        response_data = {"error": results["message"]}
        response_code = 400

    return (jsonify(response_data), response_code)


@app.route("/api/cupcakes/<cupcake_id>", methods=["PATCH"])
def update_cupcake_api(cupcake_id):
    """ Update a cupcake with flavor, size, rating and image data from the body of a 
          JSON request.

        Responds wtih
        200 on successful update with JSON Response {cupcake: {id, flavor, size, rating, image}} 

        400 when there was an issue found with the data.
        404 when the cupcake identified by cupcake_id was not found or when cupcake_id is 
          not an integer.
        For 40x errors, JSON Response is {error: {message: descriptive error message}}

    """

    # only use cupcake_id for a db lookup when we know it is an integer
    if (cupcake_id.isnumeric()):
        cupcake_data = CUPCAKE_FIELDS

        for key in cupcake_data.keys():
            cupcake_data[key] = request.json.get(key, None)

        results = db_update_cupcake(cupcake_id, cupcake_data)

        if (results["successful"]):
            # on success / okay, message contains serialized information for the new cupcake.
            response_data = {"cupcake": results["message"]}
        else:
            response_data = {"error": {"message": results["message"]}}

        response_code = results["response_code"]

    else:
        response_data = {
            "error": {"message": f"Update Error: Cupcake id='{cupcake_id}' was not an integer. No updates occurred."}
        }
        response_code = 404

    return (jsonify(response_data), response_code)


# DELETE /api/cupcakes/[cupcake-id]
@app.route("/api/cupcakes/<cupcake_id>", methods=["DELETE"])
def delete_cupcake_api(cupcake_id):
    #     This should raise a 404 if the cupcake cannot be found.

    #     Delete cupcake with the id passed in the URL. Respond with JSON like {message: "Deleted"}.
    """ Delete the single cupcake identified by cupcake_id.

        Do no coerce cupcake_id into an integer via <int:cupcake_id> because the route
        for a non-integer value does not exist and a different 404 error results!

        200 for successful update, JSON response is {message: Deleted {id, flavor, rating, size, image}}.

        400 is raised when an error occurred during the delete. No delete occurred.        

        404 is raised when the cupcake identified by cupcake_id was not found or when
        cupcake_id is not an integer.

        For 40x errors, JSON message data is {error: {message: description of error}}

    """

    # only use cupcake_id for a db lookup when we know it is an integer
    if (cupcake_id.isnumeric()):
        results = db_delete_cupcake(cupcake_id)
        response_code = results["response_code"]
        response_data = results["message"]

    else:
        response_code = 404
        response_data = {
            "error": {"message": f"Cupcake id='{cupcake_id}' was not an integer. No delete occurred. "}
        }

    return (jsonify(response_data), response_code)


# HTML Routes

# GET /api/cupcakes
@app.route("/")
def home_page():
    """ Render a template to an empty home page.
        JavaScript will take care of the rest.
    """

    return render_template("index.html")
