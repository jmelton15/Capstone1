from config_files import keys
import os
import random
import json
from flask import Flask, request,render_template,redirect,flash,session,flash,g,jsonify
from flask_mail import Mail, Message
from jinja2 import Environment, PackageLoader, select_autoescape
from urllib.parse import urlparse, parse_qsl
from urllib.parse import urlencode
import requests
import secrets
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from models import db, connect_db,User,Trip
from forms import RouteForm,LoginForm,EditUsername,SignUpForm,PasswordResetForm,EmailConfirmationForm
from flask_bcrypt import Bcrypt
from map_client import get_places_nearby_sorted

CURR_USER_KEY = "curr_user"
MEMBER_STATUS = "member_status"
CSRF_TOKEN_KEY = None
 

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///dtri_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY',"SUPERSECRETKEY")
env = Environment(
    loader=PackageLoader('app', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY',"DefaultValue") 
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER','smtp.gmail.com')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT',587)
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', True)
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', False)
# app.config['MAIL_SUPPRESS_SEND'] = os.environ.get('MAIL_SUPPRESS_SEND')
app.config['MAIL_DEBUG'] = True
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)
connect_db(app)
# db.create_all()

######################################################################
# Session handling for logged in users 
@app.before_request
def add_user_and_token_to_g():
    """If we're logged in, add curr user to Flask global."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        g.member = session[MEMBER_STATUS]
    else:
        g.user = None
        g.member = None

def store_free_trips_and_saved_trips(user):
    """ Handles getting how many free trips a user has left to make
        As well as how many saved trips they have.
    """
    session["free_trips"] = user.free_trips
    session["saved_trips"] = user.saved_trips
            
def do_login(user):
    """Log in user."""
    session[MEMBER_STATUS] = user.member_status
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session['csrf_token']
        del session['free_trips']
        del session['saved_trips']
        del session[CURR_USER_KEY]
        del session[MEMBER_STATUS]

###############################################################################
# Homepage, About Us, and error handling

@app.errorhandler(404)
def page_not_found(e):
    flash('The Path or Route You Tried Accessing Is Not Valid',"alert-danger")
    flash('If You Have Not Created An Account Yet, Please Do So Here','alert-primary')
    return redirect("/")

@app.route('/')
def reroute_from_root():
    """Shows Homepage and a video or image of how the site works
    """
    if not g.user:
        return redirect('/login')
    else:
        return redirect('/main')


@app.route("/main")
def show_main_page():
    """ Shows main page if user is logged in already, instead of login page
    """
    return render_template("main_page.html")

@app.route('/about')
def show_about_page():
    """ Shows the About-Us page
    """
    return render_template("about_us.html")

###################################################################################
# User routes

@app.route('/register', methods=["GET", "POST"])
def signup_user():
    """Handles signing up a user. 
    If validated credentials in form, then user is added to database
    and user is added to session
    otherwise, redirected with a flash message
    """

    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'alert-danger')
            return render_template('register_user.html', form=form)

        do_login(user)
        store_free_trips_and_saved_trips(user)

        return redirect("/")
    else:
        return render_template('register_user.html', form=form)
    

@app.route('/login', methods=["GET", "POST"])
def login_user():
    """Handle logging in a user"""
    if not g.user:
        form = LoginForm()

        if form.validate_on_submit():
            user = User.authenticate(form.username.data,
                                    form.password.data)

            if user:
                do_login(user)
                erase_pass_token(user)
                store_free_trips_and_saved_trips(user)
                flash(f"Hello, {user.username}!", "alert-success")
                return redirect(f"/users/{user.id}/profile")

            flash("Invalid credentials.", 'alert-danger')
        return render_template('login_main_page.html', form=form,csrf_token=session['csrf_token'])
    else:
        return redirect("/main")


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("You Have Successfully Logged Out. See You Later!","alert-success")
    return redirect("/login")


@app.route('/users/<int:user_id>/profile')
def show_user_profile(user_id):
    """ Handle showing the user profile and options for deleting/editing profile
    """
    if not g.user:
        flash("Unauthorized Access. This Is Not Your Account", "alert-primary")
        redirect("/login")
    user = User.query.get_or_404(user_id) 
    form = EditUsername()
    trips = user.trips
    decoded_trips = [trip.decrypt_trip_data() for trip in trips]
    return render_template("user_profile/user_details.html",user=user,form=form,trips=decoded_trips)
    

@app.route('/users/<int:user_id>/profile',methods=["PATCH","DELETE"])
def update_or_delete_user(user_id):
    """ Handles either updating a user's username or deleting the user
    """

    if not g.user:
        flash("Unauthorized Access. This Is Not Your Account", "alert-primary")
        redirect("/login")
    if validate_client_side_data(request.headers):
        if request.method == "DELETE":
            User.query.filter_by(id=user_id).delete()
            db.session.commit()
            do_logout()
            response = {
                "alert":"Account Successfully Deleted. You're Welcome Back Anytime!"
            }
            return jsonify(response=response)
        if request.method == "PATCH":
            user = User.query.get_or_404(user_id)
            user.username = request.json.get('new_username',user.username)
            try:
                db.session.commit()
            except IntegrityError:
                return jsonify(response={"error":"Username Already Exists. Try Another"})
            response = {
                "ok":'OK'
            }
            return jsonify(response=response)
    else:
        flash("You Cannot Do That","alert-primary")
        return redirect("/main")



###################################################################################
# Trip Deletion Route

@app.route('/users/<int:user_id>/trips/<int:trip_id>',methods=["DELETE"])
def delete_trip(user_id,trip_id):
    """ Handles deleting a trip based on user_id and trip_id
    """
    if not g.user:
        flash("Unauthorized Access.", "alert-primary")
        redirect("/login")
    if validate_client_side_data(request.headers):
        user = User.query.get_or_404(user_id)
        Trip.query.filter_by(id=trip_id).delete()
        if not g.member:
            session["saved_trips"] -= 1
            user.saved_trips = session["saved_trips"]
        db.session.commit()
        response = {
            "alert":"Trip Successfully Deleted. Now You Have Space For Another Trip!"
        }
        return jsonify(response=response) 
    return redirect(f"/users/{user_id}/profile") 
        
            
               
###################################################################################
# Map Interaction Routes  
    
@app.route('/users/<int:user_id>/trip',methods=["GET","POST"])
def show_create_trip(user_id):
    """ Handles displaying and creating a trip for a non-member and a member-user that is logged-in
        If a non-member: page will not have a a button for saving a trip and will only allow one trip
        If a member: Page will have a button for saving trips 
        as well as allow the user To create more than one trip
    """
    if not g.user:
        flash("You Are Not Registered. In Order To Create A Trip, You Must Create An Account First.","alert-info")
        return redirect("/register")
    
    user = User.query.get_or_404(user_id)
    
    if request.method == "POST":
        if validate_client_side_data(request.headers):
            response = {
                "member_status":g.member,
                "saved_trips":user.saved_trips,
            }
            if not g.member:
                if has_free_trips():
                    top_rated_waypoints = get_trip_request_data(request.json)
                    session["free_trips"] -= 1
                    user.free_trips = session["free_trips"]
                    db.session.commit()
                    response["top_rated_waypoints"] = top_rated_waypoints
                    return jsonify(response=response)
                flash('You Are Not A Member And Have Used Your Free Trips',"alert-danger")
                return redirect(f'/users/{user_id}/trip')
            top_rated_waypoints = get_trip_request_data(request.json)
            response["top_rated_waypoints"] = top_rated_waypoints
            return jsonify(response=response)
        flash('Incorrect Form ID. Form Not Validated',"alert-danger")
        return redirect(f'/users/{user_id}/trip')
    
    return render_template("maps/create_trip_form.html",csrf_token=session['csrf_token'],member_status=g.member,has_trips=has_free_trips(),user=user)


@app.route("/users/<int:user_id>/trips/save",methods=["POST"])
def save_trip_for_user(user_id):
    """ Handles processing a request to save user's trip details.
        Will make sure request is valid and that the user is authorized.
        Sends a response back to the client-side of "OK" if it is successful.
        Otherwise, redirects back
    """
    if not g.user:
        flash("You Are Not Authorized.","alert-primary")
        return redirect("/login")
    
    if validate_client_side_data(request.headers):
        user = User.query.get_or_404(user_id)
        response = {
            "ok":'OK'
        }
        if not g.member:
            if can_save_trip() == True:
                session["saved_trips"] += 1
                user.saved_trips = session["saved_trips"]
                save_trip_data(request.json,user_id)
                return jsonify(response=response)
            flash("You Cannot Save Anymore Trips.","alert-danger")
            return redirect(f'/users/{user_id}/trip')
        user.saved_trips += 1
        save_trip_data(request.json,user_id)
        return jsonify(response=response)
    flash("Could Not Validate Data.","alert-danger")
    return redirect(f'/users/{user_id}/trip')

@app.route('/users/<int:user_id>/trips/<int:trip_id>/show',methods=["GET"])
def remake_saved_trip(user_id,trip_id):
    """ Handles remaking a user's saved trip on the map for them to see again
    """
    if not g.user:
        flash("This is not your trip. Please Login or Create an Account","alert-primary")
        return redirect("/login")
    trip = Trip.query.get_or_404(trip_id)
    if trip:
        decoded_trip_obj = trip.decrypt_trip_data()
        return render_template("/user_profile/show_saved_trip.html",trip=trip,trip_info=json.dumps(decoded_trip_obj))
    flash("Unable To Find Trip","alert-primary")
    return redirect('/main')
            
    
########################################################################################
## FUNCTIONS FOR MAP INTERACTION ##

def get_trip_request_data(request_data):
    """ Handles gathering request data from a posted trip on the client side
        And then runs it through the get_places_nearby_sorted function 
        and returns the top_rated_waypoints results
    """
    path_points = request_data["points"]
    waypoints = request_data["waypoints"]
    return get_places_nearby_sorted(path_points,waypoints) 

def save_trip_data(request_data,user_id):
    """ Handles gathering request data when a user saves their trip details.
        This will encrypt their trip details and store the encrypted data in the  
        database for later access
    """
    # sp and ep should be regular strings
    start_point = request_data["start_point"]
    end_point = request_data["end_point"]
    waypoint_names = request_data['waypoint_names'] # names of every waypoint
    waypoint_addresses = request_data['waypoint_addresses']
    waypoint_latlng = request_data["waypoint_latlng"] # This should be string tuples ["(lat,lng)","(lat,lng)"]
    photo = request_data["photo"]
    
    saved_trip = Trip.encrypt_and_store_trip_data(start_point,end_point,waypoint_names,waypoint_addresses,waypoint_latlng,
                                                  photo,user_id)
    
    if saved_trip:
        db.session.commit()
        
        
####################################################################################
## PASSWORD RESET ROUTE ##       

@app.route("/password/forgot",methods=["GET","POST"])
def send_password_reset():
    """ Handles showing email authentication page to recieve verification token
       As well as sending the verification token to the user using twilio-mail service API
    """
    form = EmailConfirmationForm()
    if form.validate_on_submit():
        email = form.email.data
        user = verify_email(email)
        if user:
            token = secrets.token_urlsafe(32)
            url = os.environ.get('URL','http://127.0.0.1:5000/password?reset=') + token
            body = f"""Hello, This Is The Password Reset Link You Requested From 'Down To The Route Of It'.
                        Click the link below to be redirected to the password reset page:\n 
                    {url}"""
            subject = "Down To The Route Of It - Password Reset Link" 
            msg = Message(recipients=[email],body=body,subject=subject)
            mail.send(msg)
            user.reset_token = token
            db.session.commit()
            flash("Code Has Been Sent and Should Be In Your Email Shortly","alert-success")
            return redirect("/password/forgot")
        else:
            flash("User Not Found, Check The Email You Entered","alert-danger")
            return redirect("/register")
    return render_template("email_confirmation.html",form=form)

@app.route("/password",methods=["GET","POST"])
def show_reset_password_form():
    """ Handles showing the reset password form as well as handling resetting the user's password
        if the user is verified via request token
    """
    token = request.args.get('reset')
    user = verify_token(token)
    if user:
        form = PasswordResetForm()
        if form.validate_on_submit():
            new_pass = form.password.data
            User.reset_password(new_pass,user)
            flash("Password Has Successfully Been Reset!","alert-success")
            erase_pass_token(user)
            return redirect("/login")
        return render_template("password_reset_page.html",form=form)        
####################################################################################
## FUNCTIONS FOR VERIFYING and DELETEING PASSWORD RESET INFORMATION ##

def verify_email(email):
    """ function used for verifying users email is in the database system
    """
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    else:
        return False
    
def verify_token(token):
    """ function for verifying the token in a query string
        for password reset
    """
    user = User.query.filter_by(reset_token=token).first()
    if user:
        return user
    else:
        return False
    
def erase_pass_token(user):
    """ erases password reset token on users account
    """
    user.reset_token = None 
    db.session.commit()

####################################################################################
## CSRF-TOKEN VALIDATION AND FREE-TRIP VALIDATION ##

def validate_client_side_data(request_headers):
    """ function for validating and securily checking form data from client side
    """
    csrf_token = request_headers["anti-csrf-token"]
    if csrf_token == session['csrf_token']:
        return True
    else:
        return False
    
def has_free_trips():
    """ Checks session data to see if user has free trips remaining
    """
    if session["free_trips"] > 0:
        return True
    else:
        return False

def can_save_trip():
    """ Checks if a user can still save a trip.
        This check is in place to only allow members to save more than 1 trip
    """
    if session["saved_trips"] >= 2:
        return False
    else:
        return True
    
##########################################################################################
# Custom Filters For Jinja Environment

@app.template_filter('random_15')
def random_fifteen(waypoints):
    """ Gives back 15 random occurrences from a list of waypoints.
        If there are 15 or less elements in the list to begin,
        it just returns the list.
        For this app, this will be used to return random waypoints on the user's travel journal
        in a method to overflow the page with waypoints when there are more than 15
    """
    if len(waypoints) <= 15:
        return waypoints
    else: 
        random.shuffle(waypoints)
        return waypoints[:15]
 

          