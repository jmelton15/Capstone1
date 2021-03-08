""" Tests For User Model"""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask import session,g
from sqlalchemy.exc import IntegrityError,InvalidRequestError
from models import db, User, Trip

os.environ['DATABASE_URL'] = "postgresql:///test_caps"

from app import app


db.create_all()



class UserModelTestCase(TestCase):
    """Test views for Users"""

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
        
        self.client = app.test_client()
        self.u1 = test_user
        self.id = test_user.id
        self.mu1 = test_member_user
        self.muID = test_member_user.id
        
        self.CURR_USER_KEY = "curr_user"
        self.MEMBER_STATUS = "member_status"
        self.Token = "secret"
        self.CSRF_HEADER = "HTTP_ANTI_CSRF_TOKEN"
        
        with self.client.session_transaction() as sess:
            sess[self.CURR_USER_KEY] = self.id
            sess[self.MEMBER_STATUS] = self.u1.member_status
            g.user = sess[self.CURR_USER_KEY]
            g.member = sess[self.MEMBER_STATUS]
           
    def tearDown(self):
        db.session.rollback()
    
    def test_authenticate_user(self):
        """ Tests authenticating a user inside the app
        """
        username = "TedTalks"
        password = "HashedPW15"
        email = "ttalks@gmail.com"
        user = User.register(username=username,password=password,email=email)
        db.session.commit()
        authenticated = user.authenticate("TedTalks","HashedPW15")
        bad_pass = user.authenticate("TedTalks","wrongpw")
        bad_user = user.authenticate("tedTalks","HashedPW15")
        
        self.assertEqual(authenticated,user)
        self.assertEqual(bad_pass,False)
        self.assertEqual(bad_user, False)
    
    def test_duplicate_username(self):
        """ Tests error thrown when duplicate username is found
        """
        email = "test7@test.com",
        username = "testuser6",
        password = "HASHED_PASSWORD8"

        user1 = User.register(username=username,password=password,email=email)
        db.session.commit()
        self.assertEqual(user1.username,"testuser6")
        with self.assertRaises(IntegrityError):
            User.register(username,password,email)
            db.session.commit()

    
    def test_update_user(self):
        """ Tests updating a users username
         The function validate_client_side_data() is tested in another file
         In order to get to the delete and update parts, that function needs to run.
        """
        user1 = User.query.filter_by(id=self.id).first()
        user1.username = "newUsername" 
        db.session.commit()
        user = User.query.filter_by(id=self.id).first()
        
        self.assertEqual(user.username,"newUsername")
    
    def test_delete_user(self):
        """ Tests deleting a user from the system
        """
        User.query.filter_by(id=self.id).delete()
        db.session.commit()
        user = User.query.filter(User.username=="test1").first()
        
        self.assertEqual(user,None)
        
        
    
    
   
        
            
            
            
            
           
        
    