"""Models for Cupcake app."""

from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.exc import NotNullViolation
# from sqlalchemy.exc import IntegrityError
# from psycopg2.errors import NotNullViolation

db = SQLAlchemy()

CUPCAKE_FIELDS = {
    "flavor": "",
    "size": "",
    "rating": "",
    "image": ""
}


def connect_db(app):
    """ Associate the flask application app with SQL Alchemy and
        initialize SQL Alchemy
    """
    db.app = app
    db.init_app(app)


# MODELS
class Cupcake(db.Model):
    """ Cupcake model for a cupcakes table in the cupcakes database. """

    __tablename__ = 'cupcakes'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    flavor = db.Column(db.String(64),
                       nullable=False)

    size = db.Column(db.String(64),
                     nullable=False)

    rating = db.Column(db.Float,
                       nullable=False)

    image = db.Column(db.Text,
                      nullable=False,
                      default='https://tinyurl.com/demo-cupcake')

    def __repr__(self):
        """Show cupcake information """

        return f"<Cupcake id:{self.id} flavor='{self.flavor}', size='{self.size}', rating={self.rating}, image='{self.image}' >"

    def serialize(self):
        """ Returns serialized dictionary with cupcake values. """

        serialized_dictionary = {
            'id': self.id,
            'flavor': self.flavor,
            'size': self.size,
            'rating': self.rating,
            'image': self.image
        }
        return serialized_dictionary


def db_add_cupcake(cupcake_spec_in):
    """ adds a cupcate to the cupcakes table """

    # print(
    #     f"\n\nMODEL db_add_cupcake: cupcake_spec = {cupcake_spec_in}", flush=True)

    # Take the values in cupcake_spec_in, move them into cupcake_spec and handle '' and strip()
    cupcake_spec = {}
    for key in cupcake_spec_in.keys():
        if (type(cupcake_spec_in[key]) == str):
            cupcake_spec[key] = cupcake_spec_in[key].strip()
            if (len(cupcake_spec[key]) == 0):
                cupcake_spec[key] = None
        else:
            cupcake_spec[key] = cupcake_spec_in[key]

    new_cupcake = Cupcake(**cupcake_spec)
    # new_cupcake = Cupcake(flavor=cupcake_spec["flavor"], size=cupcake_spec["size"],
    #                       rating=cupcake_spec["rating"], image=cupcake_spec["image"])

    try:
        db.session.add(new_cupcake)
        db.session.commit()

        results = {
            "message": new_cupcake.serialize()}
        results["successful"] = True

    except:
        # will check whether required values were provided.
        if ((cupcake_spec["flavor"] == None) or (cupcake_spec["size"] == None) or
                (cupcake_spec["rating"] == None)):
            msg_fields = f"flavor='{str(cupcake_spec['flavor'])}', size='{str(cupcake_spec['size'])}', rating={str(cupcake_spec['rating'])}."
            results = {
                "message": f"An error occurred. Non-blank values required for flavor, size, and rating. {msg_fields.replace('''None''', '')}"}

        else:
            results = {"message": "An error occurred."}

        results["successful"] = False

        db.session.rollback()

    return results


def change_occurred(from_vals, to_vals):
    """ Compares dictionary of from and to values to ensure a change occurred. 

        from_vals should contain the values from the database while to_vals should contain values from
        the form / api.

    """

    # print(
    #     f"\n\nMODEL: change_occurred: from: {from_vals} to: {to_vals}.", flush=True)

    results = {
        "changed": False,
        "message": ""
    }

    for key in from_vals.keys():
        try:
            # merely reference the to key will cause the KeyError when it does not exist.

            if (type(to_vals[key]) == str):
                # check if we have a non-blank value.
                if (len(to_vals[key]) == 0):
                    # all fields are required and cannot be blank. Stop Checking.
                    results["changed"] = False
                    results["message"] = f"Error: A non-blank value is required for {key}. No updates occurred."
                    # return. There is no need to continue checking
                    return results

            if (from_vals[key] != to_vals[key]):
                results["changed"] = True

        except KeyError:
            results["changed"] = False
            results["message"] = f"Error: required fields not provided. {key} was missing."
            # return. All from key fields are required
            return results

    # made it through the for loop, all keys in the from dictionary were found in the to dictionary
    #  and values were checked.
    return results


def db_update_cupcake(cupcake_id, cupcake_edits_in):
    """ Updates the cupcake when changes have occurred.

        cupcake_id is the id of the cupcake getting updated. cupcake edits is a dictionary 
        containing the updatable fields and values for the cupcake record update.

    """

    db_cupcake = Cupcake.query.get(cupcake_id)

    if (db_cupcake):

        # remove leading / trailing spaces and save into a new dictionary.
        cupcake_edits = {}
        for key in cupcake_edits_in.keys():
            # Check for None. All fields are required and cannot be None.
            if (cupcake_edits_in[key] == None):
                # we are done. All fields are required to have values. Return
                results = {
                    "message": f"Update Error: All fields require a value. {key} had a value of None. No updates occurred."}
                results["successful"] = False
                results["response_code"] = 400
                return results

            else:
                if (type(cupcake_edits_in[key]) == str):
                    cupcake_edits[key] = cupcake_edits_in[key].strip()

                else:
                    cupcake_edits[key] = cupcake_edits_in[key]

        # add in id before we check for changes across the entire record.
        cupcake_edits["id"] = int(cupcake_id)

        data_check = change_occurred(db_cupcake.serialize(), cupcake_edits)

        if (data_check["changed"]):

            db_cupcake.flavor = cupcake_edits["flavor"]
            db_cupcake.size = cupcake_edits["size"]
            db_cupcake.rating = cupcake_edits["rating"]
            db_cupcake.image = cupcake_edits["image"]

            try:
                # yes, we need a try to catch stuffing a sting into a float.
                db.session.commit()

                results = {
                    "message": db_cupcake.serialize(),
                    "successful": True,
                    "response_code": 200
                }
            except:
                db.session.rollback()

                results = {
                    "message": f"Update Error: An error occurred while updating {db_cupcake.id}: {db_cupcake.flavor}. No updates occurred.",
                    "successful": False,
                    "response_code": 400
                }

        else:
            if (len(data_check["message"]) == 0):
                # no changes and message is "". There were no data issues.
                results = {
                    "message": db_cupcake.serialize(),
                    "successful": True,
                    "response_code": 200
                }
            else:
                # An error occurred with the data while comparing in change_occurred.
                results = {
                    "message": f"Update Error: { data_check['message'] }",
                    "successful": False,
                    "response_code": 400
                }

    else:
        results = {
            "message": f"Update Error: Cupcake id={cupcake_id} was not found. No updates occurred.",
            "successful": False,
            "response_code": 404
        }

    return results


def db_delete_cupcake(cupcake_id):
    """ deletes a cupcate to the cupcakes table """

    del_cupcake = Cupcake.query.get(cupcake_id)

    if (del_cupcake):
        msg_historical = del_cupcake.serialize()

        db.session.delete(del_cupcake)

        try:
            db.session.commit()

            results = {
                "message": {
                    "message": {
                        "deleted": msg_historical
                    }
                },
                "successful": True,
                "response_code": 200
            }

        except:
            db.session.commit()

            results = {
                "message": {
                    "error": {
                        "message": f"An error occurred while deleting {str(msg_historical)}. No delete occurred. "
                    }
                },
                "successful": False,
                "response_code": 400
            }

    else:
        results = {
            "message": {"error": {"message": f"Cupcake id={cupcake_id} was not found. No delete occurred. "}},
            "successful": False,
            "response_code": 404
        }

    return results
