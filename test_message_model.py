"""message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages"""

    def setUp(self):
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "test1@gmail.com","password",None)
        id1 = 111
        u1.id = id1
      
        db.session.commit()
        user1 = User.query.get(id1)
        self.user1 = user1
        self.id1 = u1.id
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        message = Message(
            text="what a nice day",
            user_id=self.id1)

        self.assertEqual(message.text,"what a nice day")
        self.assertEqual(message.user_id,self.id1)

    def test_message_like(self):
        message = Message(
            text="what a nice day",
            user_id=self.id1)

        self.user1.likes.append(message)

        likes = Likes.query.filter(Likes.user_id==self.id1).all()
        self.assertEqual(len(likes),1)