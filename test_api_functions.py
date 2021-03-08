""" Tests For API functions """

# run these tests like:
#
#    python -m unittest test_api_functions.py

import os
from unittest import TestCase
from flask import session,g
from sqlalchemy.exc import IntegrityError,InvalidRequestError
from models import db, User, Trip
from config_files import keys
from urllib.parse import urlparse, parse_qsl
from urllib.parse import urlencode
import requests
import googlemaps
from datetime import datetime
import numpy
import math
from app import app
import map_client

os.environ['DATABASE_URL'] = "postgresql:///test_caps"
GOOGLE_API_KEY = keys["GOOGLE_API_KEY"]
now = datetime.now()

# db.create_all()


class ApiFunctionsTestCase(TestCase):
    """Test views for Users"""

    def setUp(self):
        """Create test client, add sample data."""
        
        self.coordinates_list = [[42.9634,-85.6681],[41.7075,-86.8950],[41.8781,-87.6298]]
        self.waypoints = ["State Park","Ice Cream"]
        self.initial_coord = (42.9634,-85.6681)
        self.last_coord = (41.8781,-87.6298)
        # long copy and pasted google data result to use 
        self.nearby_places_data = [{'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 42.9544878, 'lng': -85.4886045}, 'viewport': {'northeast': {'lat': 42.95579032989272, 'lng': -85.48719497010727}, 'southwest': {'lat': 42.95309067010728, 'lng': -85.48989462989272}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/shopping-71.png', 'name': "Scooper's Ice Cream Shoppe", 'opening_hours': {'open_now': True}, 'photos': [{'height': 3456, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/116817238352139987816">Tim Krueger</a>'], 'photo_reference': 'ATtYBwL-fZR1dojdwfvscLmrr8CapQGd5YBadZ2VYJNLxwc9G1ZrnQPIAW0uFI2MwMjFAAmqSHwwqmBb_vHEdtqn4Sqh2SCNlgdO6Tuk9bFnrNv4geg8imeGnXa1gSMtgiYDMov6DgpY7FScUSWa8uABQ8AraTji9rRk-vYpHuva7hlieB6K', 'width': 4608}], 'place_id': 'ChIJc265W7dRGIgRyZ5tMyesmSY', 'plus_code': {'compound_code': 'XG36+QH Ada, Michigan', 'global_code': '86JPXG36+QH'}, 'price_level': 1, 'rating': 5.0, 'reference': 'ChIJc265W7dRGIgRyZ5tMyesmSY', 'scope': 'GOOGLE', 'types': ['food', 'point_of_interest', 'store', 'establishment'], 'user_ratings_total': 105, 'vicinity': '591 Ada Dr SE, Ada'}, {'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 42.8811019, 'lng': -85.60817779999999}, 'viewport': {'northeast': {'lat': 42.88252922989272, 'lng': -85.60671752010727}, 'southwest': {'lat': 42.87982957010728, 'lng': -85.60941717989272}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/shopping-71.png', 'name': 'Iorio Gelato @ Horrocks Market', 'opening_hours': {'open_now': True}, 'place_id': 'ChIJI04erkKzGYgRReFWhsoV-CY', 'plus_code': {'compound_code': 'V9JR+CP Grand Rapids, Michigan', 'global_code': '86JPV9JR+CP'}, 'rating': 4.3, 'reference': 'ChIJI04erkKzGYgRReFWhsoV-CY', 'scope': 'GOOGLE', 'types': ['food', 'point_of_interest', 'store', 'establishment'], 'user_ratings_total': 3, 'vicinity': '4455 Breton Rd SE, Grand Rapids'}, {'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 42.8685091, 'lng': -85.57026839999999}, 'viewport': {'northeast': {'lat': 42.86986267989272, 'lng': -85.56900882010727}, 'southwest': {'lat': 42.86716302010728, 'lng': -85.57170847989272}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/restaurant-71.png', 'name': "PJ's Pizza, Coffee & Ice Cream", 'opening_hours': {'open_now': False}, 'photos': [{'height': 1000, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/111286923329484073408">PJ&#39;s Pizza</a>'], 'photo_reference': 'ATtYBwIISgVfNrt3kb_QZJS47q9qaxCTfUoOVvn0hLqQZxfWYFM3gpE-wEd9aOMoF4NS_ygHC637GxNXy57z9FzE0_J3cPECthmeQlXRzv3aJi0dKgzlnEomSiPSdc1SucUMDjFqxvzFK4i_0U_IbE9Odpj4Ec3VoI-kX_QKxtohZNIx3Pnw', 'width': 1500}], 'place_id': 'ChIJsfQiOI5MGIgRFaTfrruXCYs', 'plus_code': {'compound_code': 'VC9H+CV Kentwood, Michigan', 'global_code': '86JPVC9H+CV'}, 'price_level': 1, 'rating': 4.4, 'reference': 'ChIJsfQiOI5MGIgRFaTfrruXCYs', 'scope': 'GOOGLE', 'types': ['meal_delivery', 'meal_takeaway', 'cafe', 'restaurant', 'food', 'point_of_interest', 'store', 'establishment'], 'user_ratings_total': 186, 'vicinity': '3836 52nd St SE, Kentwood'}]
        
        
    def tearDown(self):
        self.coordinates_list = []
        self.waypoints = []
        self.initial_coord = ()
        self.last_coord = ()
        self.nearby_places_data = []
    
    def test_sort_top_rated_locations(self):
        """ Tests the sort_top_rated_locations() function
        found in the map_client.py file
        This function takes in data from a nearbyplaces request to 
        Google API and returns an individual object nested in an array.
        Should return:
        [{'name':place['name'],'rating':place['rating'],'address':place['vicinity'],
          'lat':place['geometry']['location']['lat'],'lng':place['geometry']['location']['lng'],
          'icon':place['icon'],'place_id':place['place_id']}
        """
        top_rated = map_client.sort_top_rated_locations(self.nearby_places_data)
        
        self.assertEqual(top_rated,[{
            'name':"Scooper's Ice Cream Shoppe",'rating':5.0,
            'address':'591 Ada Dr SE, Ada','lat':42.9544878,'lng':-85.4886045,
            'icon':'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/shopping-71.png',
            'place_id':'ChIJc265W7dRGIgRyZ5tMyesmSY'
        }])
    
    def test_get_distance_between_two_coords(self):
        """ Tests the get_distance_between_two_coords() function found
            in the map_client.py file.
            This function takes in two coordinate pairs tuples (lat,lng) and (lat,lng)
            And returns the distance and duration to travel between them
            Returned dictionary is:
            {'distance':some number,'duration':some number}
            distance is a value in meters and durations is in seconds
        """
        distance_data = map_client.get_distance_between_two_coords(self.initial_coord,self.last_coord)
        
        self.assertEqual(distance_data['distance'],286331)
        self.assertEqual(distance_data['duration'],10104)
        
    def test_get_steps(self):
        """ Tests the get_steps() function in the map_client.py file.
          This function is used to calculate a number of steps to skip along 
          the path before checking for nearby places again. 
          It returns an int value.
        """
        steps = map_client.get_steps(self.initial_coord,self.last_coord,self.coordinates_list)
        
        self.assertEqual(steps,0)
        
    def test_iterate_over_waypoints(self):
        """ Tests the iterate_over_waypoints() function found in 
            the map_client.py file.
            This function takes in 4 manditory parameters and up to
            a total of 7 parameters.
            
            It iterates over each waypoint in a list of waypoint names
            The function returns an array of objects based on how many 
            waypoints were given.. so if two waypoints were given the array 
            would look like [{},{}] etc.
            
            If i was passed in as a parameter, the function would then
            also begin to check the previous objects that were stored prior
            to make sure it doesn't duplicate any values. This got messy, so
            I probably need to go back and look at better ways to do it!
            this also returns an array of objects based on the number of waypoints
            [{},{}] etc.
        """
        stored_objs = {0:[{'State Park':[{'name':'bobs burgers'}],'Ice Cream':[{'name':'Scoopers'}]}]}
        waypoints = self.waypoints
        coordinates = self.coordinates_list
        place_count = 0
        without_i_param = map_client.iterate_over_waypoints(stored_objs,waypoints,coordinates,place_count,initial_coord=self.initial_coord)
        data_should_be = {'address':"2215 Ottawa Beach Rd, Holland",
                          "name":"Holland State Park","lat":42.77926120000001,
                          "lng":-86.1989545,"rating":4.7,
                          "place_id":"ChIJS2NTTOr0GYgRbNa9Q_6WZ90",
                          "icon":"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/park-71.png"}
        self.assertEqual(without_i_param[0]['State Park'][0],data_should_be)
        
    def test_get_places_nearby_sorted(self):
        """ Tests the get_places_nearby_sorted() function found in the
            map_client.py file.
            This function takes in a nested array of lat,lng points
            [[lat,lng],[lat,lng]] etc and a list of waypoint names [name,name,name]
            
            Returns a dictionary of the top rated spots in each waypoint name
            Dictionary should look like this:
            {'0':[{'waypoint1':[{'name':name str,'rating':rating int,'lat':lat int,'lng':lng int}]}} etc...
        """
        json_data = map_client.get_places_nearby_sorted(self.coordinates_list,self.waypoints)
        
        self.assertEqual(type(json_data),dict)