""" Tests For User views"""

# run these tests like:
#
#    python -m unittest test_user_views.py


import os
from unittest import TestCase
from flask import session,g
from sqlalchemy.exc import IntegrityError,InvalidRequestError
from models import db, User, Trip

os.environ['DATABASE_URL'] = "postgresql:///test_caps"

from app import app
app.config["WTF_CSRF_ENABLED"] = False

db.create_all()


class UserViewsTestCase(TestCase):
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
        
        self.client = app.test_client()
        self.u1 = test_user
        self.id = test_user.id
        self.mu1 = test_member_user
        self.muID = test_member_user.id
        
        self.CURR_USER_KEY = "curr_user"
        self.MEMBER_STATUS = "member_status"
        self.Token = "secret"
        self.CSRF_HEADER = "anti-csrf-token"
        self.headers = {
                self.CSRF_HEADER:self.Token
            }
           
    def tearDown(self):
        db.session.rollback()
    
    def test_show_user_profile(self):
        """ Test displaying the user profile, but only 
            when user is logged in or in session
        """
        with app.test_request_context():
            with self.client.session_transaction() as sess:
                sess[self.CURR_USER_KEY] = self.u1.id
                sess[self.MEMBER_STATUS] = self.MEMBER_STATUS
            g.user = sess[self.CURR_USER_KEY]
            g.member = sess[self.MEMBER_STATUS]
            resp = self.client.get(f"/users/{self.id}/profile")
            html = resp.get_data(as_text=True)    
            self.assertEqual(resp.status_code,200)
            self.assertIn("Hello, test1",html)

    def test_update_username(self):
        """ Test updating a username
        """
        with app.test_request_context():
            with self.client.session_transaction() as sess:
                sess[self.CURR_USER_KEY] = self.u1.id
                sess[self.MEMBER_STATUS] = self.MEMBER_STATUS
                sess['csrf_token'] = self.Token
            g.user = sess[self.CURR_USER_KEY]
            g.member = sess[self.MEMBER_STATUS]
            json = {
                "new_username":"broman"
            }
            
            resp = self.client.patch(f"/users/{self.id}/profile",
                                     headers=self.headers,
                                     json=json)
            
            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json["response"]["ok"],"OK")
    
    def test_delete_user(self):
        """ Tests a user deleting their account
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
            
            resp = self.client.delete(f"/users/{self.id}/profile",
                                     headers=self.headers)
            
            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json["response"]["alert"],"Account Successfully Deleted. You're Welcome Back Anytime!")
            
               