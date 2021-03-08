from flask import Flask, request,render_template,redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from config_files import keys
from sqlalchemy.dialects import postgresql

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """[connect to database]
    """
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model/class for users table creation and methods for users
    """
    __tablename__ = "users"
    
    @classmethod
    def register(cls,username,password,email):
        """register class method for creating a User (registering a new User)
            With a secure and encrypted password that can be stored
        Args:
            username ([type]): [description]
            pwd ([type]): [password]
            email ([type]): [description]
            first_name ([type]): [first_name]
            last_name([type]): [last_name]
        Returns:
            A User object with encrypted password for database storage
        """
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        
        user = User(username=username,password=hashed_utf8,email=email)
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls,username,pwd):
        """validate a an attempted login is allowed and in the database
            and that the password is correct for that user
        Args:
            username ([type]): [description]
            pwd ([type]): [password]
        Returns:
            the user from User query if valid, otherwise false
        """
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password,pwd):
            return user
        else:
            return False
    
    @classmethod
    def reset_password(cls,new_pass,user):
        """ encrypts the new password a user created and stores it as their new password 
        """
        hashed = bcrypt.generate_password_hash(new_pass)
        hashed_utf8 = hashed.decode("utf8")
        user.password = hashed_utf8
        db.session.commit()
    
    
    def __repr__(self): 
        """show info about User objects
        """
        u = self
        return f"<User username={u.username}>"
    
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String,nullable=False,unique=True)
    password = db.Column(db.String,nullable=False)
    email = db.Column(db.String,unique=True)
    member_status = db.Column(db.Boolean,server_default='f',nullable=True)
    free_trips = db.Column(db.Integer, default=5,nullable=True)
    saved_trips = db.Column(db.Integer,default=0,nullable=True)
    reset_token = db.Column(db.String,nullable=True,unique=True)
    
    trips = db.relationship('Trip',backref='user',cascade="all, delete")

class Trip(db.Model):
    """ Trip model/class that handles setting up the trips table in the database
        This table will store data about a user's saved trip and allow them to see
        their past created trips
    """ 
    __tablename__ = "trips"
    
    @classmethod
    def encrypt_and_store_trip_data(cls,start_point,end_point,waypoint_names,waypoint_latlng,photo,user_id):
        """ Classmethod for encrypting trip data to store in the Database.
            Uses AES Cipher.
        """
        key = keys['CIPHER_KEY']
        iv = keys['IV']
        sp_data = start_point.encode()
        ep_data = end_point.encode()
        wp_name_data = [wp.encode() for wp in waypoint_names]
        wp_latlng_data = [wp.encode() for wp in waypoint_latlng] 
        cipher = AES.new(key, AES.MODE_GCM, iv)
        enc_sp = cipher.encrypt(pad(sp_data, 16))
        enc_ep = cipher.encrypt(pad(ep_data, 16))
        enc_wp_names = [cipher.encrypt(pad(wp, 16)) for wp in wp_name_data]
        enc_wp_latlng = [cipher.encrypt(pad(wp, 16)) for wp in wp_latlng_data]
        
        trip = Trip(start_point=enc_sp,end_point=enc_ep,waypoint_names=enc_wp_names,waypoint_latlng=enc_wp_latlng,
                    photo=photo,user_id=user_id)
        db.session.add(trip)
        return trip

    def decrypt_trip_data(self):
        """ Method for decrypting trip data of a Trip object to be accessed in the app
            Returns a dictionary:
            {'start_point':start_point,'end_point':end_point,'waypoints':waypoints}
        """
        key = keys['CIPHER_KEY']
        iv = keys['IV']
        cipher = AES.new(key,AES.MODE_GCM,iv)
        dec_sp = unpad(cipher.decrypt(self.start_point), 16)
        dec_ep = unpad(cipher.decrypt(self.end_point), 16)
        dec_wp_name = [unpad(cipher.decrypt(wp), 16).decode() for wp in self.waypoint_names]
        dec_wp_latlng = [unpad(cipher.decrypt(wp), 16).decode() for wp in self.waypoint_latlng]
        return {'id':self.id,'start_point':dec_sp.decode(),'end_point':dec_ep.decode(), 
                'waypoint_names':dec_wp_name,'photo':self.photo,
                'waypoint_latlng':dec_wp_latlng} # waypoints are returned as bytes still [b'(lat,lng)',...]
     
    def __repr__(self):  
        """show info about Trip objects
        """
        t = self
        return f"<Trip start_point={t.start_point} | end_point={t.end_point}>"
    
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    start_point = db.Column(db.LargeBinary,nullable=False) 
    end_point = db.Column(db.LargeBinary,nullable=False)
    waypoint_names = db.Column(db.ARRAY(db.LargeBinary,zero_indexes=True),nullable=False)
    waypoint_latlng = db.Column(db.ARRAY(db.LargeBinary,zero_indexes=True),nullable=True)
    photo = db.Column(db.String, nullable=True, server_default="/static/images/default_trip.jpg")
    user_id = db.Column(db.Integer,db.ForeignKey("users.id",ondelete="CASCADE"),nullable=False)


     