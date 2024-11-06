"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        # User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()
        
        
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "test1@gmail.com","password",None)
        id1 = 111
        u1.id = id1
        u2 = User.signup("test2", "test2@gmail.com","password",None)
        id2 = 222
        u2.id = id2

      
        db.session.commit()

        user1 = User.query.get(id1)
        user2 = User.query.get(id2)

        self.user1 = user1
        self.user2 = user2

        self.id1 = u1.id
        self.id2 = u2.id

        self.client = app.test_client()


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )


        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        self.assertEqual(len(u.likes),0)
        self.assertEqual(u.email, "test@test.com")
        self.assertEqual(u.username,"testuser")
        self.assertEqual(u.bio,None)
        self.assertEqual(u.location,None)
        self.assertEqual(u.header_image_url,'/static/images/warbler-hero.jpg')
        self.assertEqual(u.image_url,'/static/images/default-pic.png')
        self.assertEqual(u.__repr__(),f"<User #{u.id}: testuser, test@test.com>")
    
        
    def test_user_following(self):
        """Test the is_following function"""
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user1.following),1)
        self.assertEqual(len(self.user1.followers),0)
        self.assertEqual(len(self.user2.following),0)
        self.assertEqual(len(self.user2.followers),1)
        self.assertTrue(self.user1.is_following(self.user2))
       
        self.assertFalse(self.user2.is_following(self.user1))
        

    def test_user_followed_by(self):
        """Test the is_follow_by function"""
        self.user1.following.append(self.user2)
        db.session.commit()
        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    def test_user_valid_sign_up(self):
        """Test user signup function"""
        test3 = User.signup("test3","test3@gmail.com","password",None)
        db.session.commit()
        user = User.query.get(test3.id)
        self.assertTrue(user)

    def test_user_Invalid_sign_up(self):
        """Test user invalid signup causing an error"""
        self.assertRaises(TypeError, User.signup, ("test3","test3@gmail.com",None,None))
   
    def test_user_authenticate(self):
        """Test valid authentication"""
        user = User.authenticate("test1","password")
        self.assertTrue(user)

    
