from config_files import keys
from urllib.parse import urlparse, parse_qsl
from urllib.parse import urlencode
import requests
import googlemaps
from datetime import datetime
import numpy
import math

GOOGLE_API_KEY = keys["GOOGLE_API_KEY"]

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
now = datetime.now()

def get_latlng(address):
    """ Takes in a human-readable address and returns the lat,lng data
    """
    geocode_result = gmaps.geocode(address)
    return geocode
# geocode_result = get_latlng('1700 Madison St.')
# print(geocode_result[0]['geometry']['location']['lat'],geocode_result[0]['geometry']['location']['lng'])

def get_directions(start,stop,mode="driving",departure_time=now):
    """ Gets directions data from google maps
    """
    
    directions_result = gmaps.directions("Sydney Town Hall",
                                    "Parramatta, NSW",
                                    mode="driving",
                                    departure_time=now)
    return directions_result


def get_places_nearby_sorted(coordinates, waypoints):
    """ Takes in a nested array of lat,lng points [[lat,lng],[lat,lng]] etc. and an array
        of waypoints. 
        This function also calls the check_distance function to determine the distance between coordinates
            This allows the function to not return too many repeated data points
        
        Returns a dictionary of the top rated spots in each category along the route
        The dictionary looks like:
        {'0':[{'waypoint1':{'name':name str,'rating':rating int,'lat':lat int,'lng':lng int}}],1:[{place:{}}]} etc...
    """
    updated_wp_json_data = {}
    group_number = 0
    initial_coord = (coordinates[0][0],coordinates[0][1])
    last_coord = (coordinates[len(coordinates)-1][0],coordinates[len(coordinates)-1][1])
    steps = get_steps(initial_coord,last_coord,coordinates)
    
    iterated_data = iterate_over_waypoints(updated_wp_json_data,waypoints,coordinates,group_number,initial_coord=initial_coord)
    updated_wp_json_data[0] = iterated_data
    
    for i in range(1,len(coordinates)):
        if i != (steps * (group_number+1)):   
            continue
        iterated_data = iterate_over_waypoints(updated_wp_json_data,waypoints,coordinates,group_number,i=i)
        group_number += 1 
        updated_wp_json_data[group_number] = iterated_data
     
    return updated_wp_json_data
 
  
def iterate_over_waypoints(stored_objs,waypoints,coordinates,group_number,i=None,initial_coord=None):
    """ Iterates over each waypoint and checks the nearby places to that waypoint
        Returns an array of objects to add to the json formatted object
        The place_count is in place here to index each object in the array of objects 
        that is in stored_objs
    """        
    object_array = []   
    place_count = 0
    if i != None:
        for place in waypoints: 
            details = gmaps.places_nearby(location=(coordinates[i][0],coordinates[i][1]),radius=50000,keyword=place)['results']
            top_rated = sort_top_rated_locations(details)
            if not top_rated:
                continue
            obj = {place:top_rated} # {place:{object:}}
            # print("#################################")
            # print(obj)
            # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            # print(group_number) 
            # print(place_count)
            # print(stored_objs[group_number]) 
            if len(stored_objs[group_number]) > place_count and stored_objs[group_number][place_count].get(place) and obj[place]['name'] == stored_objs[group_number][place_count][place]['name']:
                continue  
            place_count += 1       
            object_array.append(obj)  
        return object_array   ## [{place:{object}},{place:{obj}}]
    else:   
        for place in waypoints: 
            details = gmaps.places_nearby(location=initial_coord,radius=50000,keyword=place)['results']
            top_rated = sort_top_rated_locations(details)
            obj = {place:top_rated}
            object_array.append(obj)  
        return object_array
                
def get_steps(initial_coord,last_coord,coordinates):
    """ Takes in a starting point and end point coordinate, calculates
        a stops/distance ratio (step_ratio) and then returns a number of 
        steps based on that ratio percentage. The number of steps is how many 
        points to skip before checking nearby places again
    """
    total_distance = get_distance_between_two_coords(initial_coord,last_coord)['distance']
    converted_array_length = len(coordinates) * 1609
    step_ratio = (converted_array_length/total_distance)*100
    if step_ratio > 20 and step_ratio < 50:
        return math.floor(len(coordinates)/8)
    elif step_ratio > 50:
        return math.floor(len(coordinates)/5)
    else:
        return math.floor(len(coordinates)/14)
    
def get_distance_between_two_coords(start,stop):
    """ Takes in two coordinates (lat,lng) and (lat,lng) and checks the distance between them
        Returns the distance value and time to travel. 
        Instead of returning true/false, I opened this function to be used for 
        all distance data
        returned data object looks like this:
        {'distance':value in meters,'duration':value in seconds}
        #{'elements':[{'distance':{'text':'km','value':num},'duration':{'text':hours mins,'value':num}}]}
    """
    distance_data = gmaps.distance_matrix(start,stop)
    return {'distance':distance_data['rows'][0]['elements'][0]['distance']['value'], #returns distance in meters
            'duration':distance_data['rows'][0]['elements'][0]['duration']['value']}  #returns duration in seconds

def sort_top_rated_locations(data):
    """ Takes data from nearby_places search results and returns the top rated place
        in the search category that is nearby.
        Returns: {name,rating,lat,lng,icon,place_id} object
        if there isn't anything it finds, then it returns None
    """
    if data and data != []:
        d = data[0] 
        if d.get('rating') and d['rating'] != 0:
            top_rated = {'name':d['name'],'rating':d['rating'],'address':d['vicinity'],
                        'lat':d['geometry']['location']['lat'],'lng':d['geometry']['location']['lng'],
                        'icon':d['icon'],'place_id':d['place_id']}
            return top_rated
    return None
 
 
def extract_ids(search_result):
    """ Takes a search result and returns the place_ids of all the results
    """
    ids = []
    for place in search_result:
        ids.append(place['place_id'])
    return ids


def lat_lng(search_result):
    """ Generator function that returns one lat,lng tuple at a time from 
        places search results
        Can be used to send back individual waypoints to JavaScript
    """
    for place in search_result:
#       [(place['geometry']['location']['lat'],place['geometry']['location']['lng']) for place in r]
        lat = place['geometry']['location']['lat']
        lng = place['geometry']['location']['lng']
        yield (lat,lng)
