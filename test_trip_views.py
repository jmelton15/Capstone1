""" Tests For Trip Views """

# run these tests like:
#
#    python -m unittest test_trip_views.py

import os
from unittest import TestCase
from flask import session,g
from sqlalchemy.exc import IntegrityError,InvalidRequestError
from models import db, User, Trip

os.environ['DATABASE_URL'] = "postgresql:///test_caps"

from app import app
app.config["WTF_CSRF_ENABLED"] = False

db.create_all()

class TripViewsTestCase(TestCase):
    """Test views for Users"""
    TESTING = True
    def setUp(self):
        """Create test client, add sample data."""
        Trip.query.delete()
        User.query.delete()
        
        test_user = User(
            username = "test1",
            password = "testHash",
            email = "test@gmail.com"
        )
        test_member_user = User(
            username= "member",
            password = "hashedTest",
            email= "mem@gmail.com",
            member_status = True
        )
        db.session.add(test_user)
        db.session.add(test_member_user)
        db.session.commit()
        self.u1 = test_user
        self.id = test_user.id
        self.mu1 = test_member_user
        self.muID = test_member_user.id
        
        test_trip = Trip.encrypt_and_store_trip_data(
            start_point = "Main",
            end_point = "New York City",
            waypoint_names = ["Best Ice Cream","bobs burgers"],
            waypoint_latlng = ["(34.5,-86.34)","(45.54,-65.65)"],
            photo="/static/images/default_trip.jpg",
            user_id=self.id
        )
        db.session.add(test_trip)
        db.session.commit()
        
        self.client = app.test_client()
        
        
        self.coordinates_list = [[42.9634,-85.6681],[41.7075,-86.8950],[41.8781,-87.6298]]
        self.waypoints = ["State Park","Ice Cream"]
        self.initial_coord = (42.9634,-85.6681)
        self.last_coord = (41.8781,-87.6298)
        # long copy and pasted google data result to use 
        self.nearby_places_data = [{'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 42.9544878, 'lng': -85.4886045}, 'viewport': {'northeast': {'lat': 42.95579032989272, 'lng': -85.48719497010727}, 'southwest': {'lat': 42.95309067010728, 'lng': -85.48989462989272}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/shopping-71.png', 'name': "Scooper's Ice Cream Shoppe", 'opening_hours': {'open_now': True}, 'photos': [{'height': 3456, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/116817238352139987816">Tim Krueger</a>'], 'photo_reference': 'ATtYBwL-fZR1dojdwfvscLmrr8CapQGd5YBadZ2VYJNLxwc9G1ZrnQPIAW0uFI2MwMjFAAmqSHwwqmBb_vHEdtqn4Sqh2SCNlgdO6Tuk9bFnrNv4geg8imeGnXa1gSMtgiYDMov6DgpY7FScUSWa8uABQ8AraTji9rRk-vYpHuva7hlieB6K', 'width': 4608}], 'place_id': 'ChIJc265W7dRGIgRyZ5tMyesmSY', 'plus_code': {'compound_code': 'XG36+QH Ada, Michigan', 'global_code': '86JPXG36+QH'}, 'price_level': 1, 'rating': 5.0, 'reference': 'ChIJc265W7dRGIgRyZ5tMyesmSY', 'scope': 'GOOGLE', 'types': ['food', 'point_of_interest', 'store', 'establishment'], 'user_ratings_total': 105, 'vicinity': '591 Ada Dr SE, Ada'}, {'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 42.8811019, 'lng': -85.60817779999999}, 'viewport': {'northeast': {'lat': 42.88252922989272, 'lng': -85.60671752010727}, 'southwest': {'lat': 42.87982957010728, 'lng': -85.60941717989272}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/shopping-71.png', 'name': 'Iorio Gelato @ Horrocks Market', 'opening_hours': {'open_now': True}, 'place_id': 'ChIJI04erkKzGYgRReFWhsoV-CY', 'plus_code': {'compound_code': 'V9JR+CP Grand Rapids, Michigan', 'global_code': '86JPV9JR+CP'}, 'rating': 4.3, 'reference': 'ChIJI04erkKzGYgRReFWhsoV-CY', 'scope': 'GOOGLE', 'types': ['food', 'point_of_interest', 'store', 'establishment'], 'user_ratings_total': 3, 'vicinity': '4455 Breton Rd SE, Grand Rapids'}, {'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 42.8685091, 'lng': -85.57026839999999}, 'viewport': {'northeast': {'lat': 42.86986267989272, 'lng': -85.56900882010727}, 'southwest': {'lat': 42.86716302010728, 'lng': -85.57170847989272}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/restaurant-71.png', 'name': "PJ's Pizza, Coffee & Ice Cream", 'opening_hours': {'open_now': False}, 'photos': [{'height': 1000, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/111286923329484073408">PJ&#39;s Pizza</a>'], 'photo_reference': 'ATtYBwIISgVfNrt3kb_QZJS47q9qaxCTfUoOVvn0hLqQZxfWYFM3gpE-wEd9aOMoF4NS_ygHC637GxNXy57z9FzE0_J3cPECthmeQlXRzv3aJi0dKgzlnEomSiPSdc1SucUMDjFqxvzFK4i_0U_IbE9Odpj4Ec3VoI-kX_QKxtohZNIx3Pnw', 'width': 1500}], 'place_id': 'ChIJsfQiOI5MGIgRFaTfrruXCYs', 'plus_code': {'compound_code': 'VC9H+CV Kentwood, Michigan', 'global_code': '86JPVC9H+CV'}, 'price_level': 1, 'rating': 4.4, 'reference': 'ChIJsfQiOI5MGIgRFaTfrruXCYs', 'scope': 'GOOGLE', 'types': ['meal_delivery', 'meal_takeaway', 'cafe', 'restaurant', 'food', 'point_of_interest', 'store', 'establishment'], 'user_ratings_total': 186, 'vicinity': '3836 52nd St SE, Kentwood'}]
        
        self.CURR_USER_KEY = "curr_user"
        self.MEMBER_STATUS = "member_status"
        self.Token = "secret"
        self.CSRF_HEADER = "anti-csrf-token"
        self.headers = {
                self.CSRF_HEADER:self.Token
            }
        
    def tearDown(self):
        db.session.rollback()
        
    def test_create_trip(self):
        """ Tests creating a trip
            This requires a post request json data from axios:
            {
                "points":array of points [[lat,lng],[lat,lng]],
                "waypoints": array of waypoint names
            }
        """
        with app.test_request_context():
            with self.client.session_transaction() as sess:
                sess[self.CURR_USER_KEY] = self.u1.id
                sess[self.MEMBER_STATUS] = self.MEMBER_STATUS
                sess['csrf_token'] = self.Token
                sess['free_trips'] = 5
                sess['saved_trips'] = 0
            g.user = sess[self.CURR_USER_KEY]
            g.member = sess[self.MEMBER_STATUS]
            json_data = {
                "points":self.coordinates_list,
                "waypoints":self.waypoints
            }
            resp = self.client.post(f"/users/{self.u1.id}/trip",
                                    headers=self.headers,
                                    json=json_data)
            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json["response"]["saved_trips"],0)
    
    def test_save_trip(self):
        """ Tests being able to save a trip to user travel journal
            The json_data object looks like this:
            {
                "start_point: some start point string,
                "end_point: some end point string,
                "waypoint_names": array of waypoint names,
                "waypoint_latlng": array of string tuples ['(lat,lng)',...],
                "photo": photo url string
            }
        """
        with app.test_request_context():
            with self.client.session_transaction() as sess:
                sess[self.CURR_USER_KEY] = self.u1.id
                sess[self.MEMBER_STATUS] = self.MEMBER_STATUS
                sess['csrf_token'] = self.Token
                sess['free_trips'] = 5
                sess['saved_trips'] = 0
            g.user = sess[self.CURR_USER_KEY]
            g.member = sess[self.MEMBER_STATUS]
            json_data = {
                "start_point":"grand rapids",
                "end_point":"chicago",
                "waypoint_names":['Bobs Burgers','Good Burger','Average-Joes'],
                "waypoint_latlng":['(34.54,-54.33)','(6.54,-66.45)','(54.23,-98.54)'],
                "photo":"someurltoencode"
            }
            post_resp = self.client.post(f"/users/{self.u1.id}/trips/save",
                                    headers=self.headers,
                                    json=json_data)
            self.assertEqual(post_resp.status_code,200)
            self.assertEqual(post_resp.json["response"]["ok"],"OK")
            
            get_resp = self.client.get(f"/users/{self.u1.id}/profile")
            profile_html = get_resp.get_data(as_text=True)            
            self.assertEqual(get_resp.status_code,200)
            self.assertIn("Bobs Burgers",profile_html)
            
            
            
            

        