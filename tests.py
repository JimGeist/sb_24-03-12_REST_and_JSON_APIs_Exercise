from unittest import TestCase

from app import app
from models import db, Cupcake

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cupcakes_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()


CUPCAKE_DATA = {
    "flavor": "TestFlavor",
    "size": "TestSize",
    "rating": 5,
    "image": "http://test.com/cupcake.jpg"
}

CUPCAKE_DATA_2 = {
    "flavor": "TestFlavor2",
    "size": "TestSize2",
    "rating": 10,
    "image": "http://test.com/cupcake2.jpg"
}


class CupcakeViewsTestCase(TestCase):
    """Tests for views of API."""

    def setUp(self):
        """Make demo data."""

        Cupcake.query.delete()

        cupcake = Cupcake(**CUPCAKE_DATA)
        db.session.add(cupcake)
        db.session.commit()

        self.cupcake = cupcake

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_list_cupcakes(self):
        with app.test_client() as client:
            resp = client.get("/api/cupcakes")

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertEqual(data, {
                "cupcakes": [
                    {
                        "id": self.cupcake.id,
                        "flavor": "TestFlavor",
                        "size": "TestSize",
                        "rating": 5,
                        "image": "http://test.com/cupcake.jpg"
                    }
                ]
            })

    def test_get_cupcake(self):
        with app.test_client() as client:
            url = f"/api/cupcakes/{self.cupcake.id}"
            resp = client.get(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {
                "cupcake": {
                    "id": self.cupcake.id,
                    "flavor": "TestFlavor",
                    "size": "TestSize",
                    "rating": 5,
                    "image": "http://test.com/cupcake.jpg"
                }
            })

    def test_create_cupcake(self):
        with app.test_client() as client:
            url = "/api/cupcakes"
            resp = client.post(url, json=CUPCAKE_DATA_2)

            self.assertEqual(resp.status_code, 201)

            data = resp.json

            # don't know what ID we'll get, make sure it's an int & normalize
            self.assertIsInstance(data['cupcake']['id'], int)
            del data['cupcake']['id']

            self.assertEqual(data, {
                "cupcake": {
                    "flavor": "TestFlavor2",
                    "size": "TestSize2",
                    "rating": 10,
                    "image": "http://test.com/cupcake2.jpg"
                }
            })

            self.assertEqual(Cupcake.query.count(), 2)

    # CUPCAKE_DATA = {
    #     "flavor": "TestFlavor",
    #     "size": "TestSize",
    #     "rating": 5,
    #     "image": "http://test.com/cupcake.jpg"
    # }

    # CUPCAKE_DATA_2 = {
    #     "flavor": "TestFlavor2",
    #     "size": "TestSize2",
    #     "rating": 10,
    #     "image": "http://test.com/cupcake2.jpg"
    # }

    #         self.cupcake = cupcake

    def test_update_cupcake_nochanges(self):
        with app.test_client() as client:
            url = f"/api/cupcakes/{self.cupcake.id}"
            resp = client.patch(url, json=CUPCAKE_DATA)

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            # don't know what ID we'll get, make sure it's an int & normalize
            self.assertIsInstance(data['cupcake']['id'], int)
            del data['cupcake']['id']

            self.assertEqual(data, {
                "cupcake": {
                    "flavor": "TestFlavor",
                    "size": "TestSize",
                    "rating": 5.0,
                    "image": "http://test.com/cupcake.jpg"
                }
            })

    def test_update_cupcake_changes(self):
        with app.test_client() as client:
            url = f"/api/cupcakes/{self.cupcake.id}"
            resp = client.patch(url, json=CUPCAKE_DATA_2)

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            # don't know what ID we'll get, make sure it's an int & normalize
            self.assertIsInstance(data['cupcake']['id'], int)
            del data['cupcake']['id']

            self.assertEqual(data, {
                "cupcake": {
                    "flavor": "TestFlavor2",
                    "size": "TestSize2",
                    "rating": 10.0,
                    "image": "http://test.com/cupcake2.jpg"
                }
            })

    def test_update_cupcake_missing_values(self):
        CUPCAKE_DATA_NO_RATING = {
            "flavor": "TestFlavor",
            "size": "TestSize",
            "image": "http://test.com/cupcake.jpg"
        }
        with app.test_client() as client:
            url = f"/api/cupcakes/{self.cupcake.id}"
            resp = client.patch(url, json=CUPCAKE_DATA_NO_RATING)

            self.assertEqual(resp.status_code, 400)

            data = resp.json
            # An error will occur because update expects all fields regardless of
            #  whether they changed.
            self.assertEqual(
                data, {
                    "error": {
                        "message": "Update Error: All fields require a value. rating had a value of None. No updates occurred."
                    }
                })

    def test_update_cupcake_bad_value(self):
        CUPCAKE_DATA_BAD_RATING = {
            "flavor": "TestFlavor",
            "size": "TestSize",
            "rating": "ten",
            "image": "http://test.com/cupcake.jpg"
        }
        with app.test_client() as client:
            url = f"/api/cupcakes/{self.cupcake.id}"
            resp = client.patch(url, json=CUPCAKE_DATA_BAD_RATING)

            self.assertEqual(resp.status_code, 400)

            data = resp.json
            # An error will occur because we are trying to set a float to a string. And becaue I
            #  was a dumb-ass and put the id in the message, I need to break the string up since
            #  we may not know the id!
            self.assertIn(
                "Update Error: An error occurred while updating", data["error"]["message"])
            self.assertIn(
                ": TestFlavor. No updates occurred.", data["error"]["message"])

    def test_update_cupcake_invalid_id(self):

        with app.test_client() as client:
            cupcake_id = '2a'
            url = f"/api/cupcakes/{cupcake_id}"
            resp = client.patch(url, json=CUPCAKE_DATA_2)

            self.assertEqual(resp.status_code, 404)

            data = resp.json
            self.assertEqual(
                data, {
                    "error": {
                        "message": f"Update Error: Cupcake id='{cupcake_id}' was not an integer. No updates occurred."
                    }
                })

    def test_update_cupcake_id_not_found(self):

        with app.test_client() as client:
            cupcake_id = 200
            url = f"/api/cupcakes/{cupcake_id}"
            resp = client.patch(url, json=CUPCAKE_DATA_2)

            self.assertEqual(resp.status_code, 404)

            data = resp.json
            self.assertEqual(
                data, {
                    "error": {
                        "message": f"Update Error: Cupcake id={cupcake_id} was not found. No updates occurred."
                    }
                })

    def test_delete_cupcake_id_not_found(self):

        with app.test_client() as client:
            cupcake_id = 200
            url = f"/api/cupcakes/{cupcake_id}"
            resp = client.delete(url)

            self.assertEqual(resp.status_code, 404)

            data = resp.json
            self.assertEqual(
                data, {
                    "error": {
                        "message": f"Cupcake id={cupcake_id} was not found. No delete occurred. "
                    }
                })
            self.assertEqual(Cupcake.query.count(), 1)

    def test_delete_cupcake_invalid_id(self):

        with app.test_client() as client:
            cupcake_id = '3f'
            url = f"/api/cupcakes/{cupcake_id}"
            resp = client.delete(url)

            self.assertEqual(resp.status_code, 404)

            data = resp.json
            self.assertEqual(
                data, {
                    "error": {
                        "message": f"Cupcake id='{cupcake_id}' was not an integer. No delete occurred. "
                    }
                })
            self.assertEqual(Cupcake.query.count(), 1)

    def test_delete_cupcake(self):

        with app.test_client() as client:
            url = f"/api/cupcakes/{self.cupcake.id}"
            resp = client.delete(url)

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertEqual(
                data, {
                    "message": {
                        "deleted": {
                            'flavor': self.cupcake.flavor,
                            'id': self.cupcake.id,
                            'image': self.cupcake.image,
                            'rating': self.cupcake.rating,
                            'size': self.cupcake.size
                        }
                    }
                })
            self.assertEqual(Cupcake.query.count(), 0)
