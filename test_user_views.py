import os 
from app import app, CURR_USER_KEY
from unittest import TestCase
from models import db, User, Message, Follows,Likes
from forms import UserProfileEditForm

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):
    def setUp(self):
        """create a user, add to session"""

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "test1@gmail.com","password",None)
        id1 = 111
        u1.id = id1
        u2 = User.signup("test2", "test2@gmail.com","password",None)
        id2 = 222
        u2.id = id2

        user1 = User.query.get(id1)
        user2 = User.query.get(id2)

        self.user1 = user1
        self.user2 = user2

        self.id1 = u1.id
        self.id2 = u2.id

        msg = Message(
            id=1234,
            text="happy friday",
            user_id=self.id2)
        self.msg = msg
        db.session.add(self.msg)   
        db.session.commit()


        self.client = app.test_client()
      
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_homepage(self):
        """test get request"""
        with app.test_client() as client:
            # import pdb
            # pdb.set_trace()
            res = client.get('/')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("<h1>What's Happening?</h1>", html)

    def test_signup(self):
        """test post request"""
        with app.test_client() as client:
            res = client.post('/signup',data={
                "username":"test",
                "password":"password",
                "email":"test@gmail.com"
            })
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 302)
            

    def test_login_get(self):
        """test login get request"""
        with app.test_client() as client:
            res = client.get('/login')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("<h2 class=\"join-message\">Welcome back.</h2>", html)

    def test_login_post(self):
        """test login post request"""
        with app.test_client() as client:
            res = client.post('/login',data={
                "username":"test1",
                "password":"password"
            })
            self.assertEqual(res.status_code,302)


    def test_logout_redirect(self):
        """test redirect"""
        with app.test_client() as client:
            res = client.get('/logout')
            self.assertEqual(res.status_code,302)
            self.assertEqual(res.location,'http://localhost/login')


    def test_logout_followed_redirect(self):
        """test redirection follow"""
        with app.test_client() as client:
            res = client.get('/logout', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

    def test_users_list(self):
        """test users list"""
        with app.test_client() as client:
            res = client.get('/users')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code,200)
            self.assertIn("<p>@test1</p>",html)

    def test_user_profile(self):
        """test a single user profile"""
        with app.test_client() as client:
            res = client.get(f'/users/{self.id1}')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code,200)
            self.assertIn("<h4 id=\"sidebar-username\">@test1</h4>",html)

    def test_user_following(self):
        """test user's following list"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.id1
               
            # user1 following user2
            follow = Follows(user_being_followed_id = self.id2, user_following_id = self.id1)
            res = client.get(f'/users/{self.id1}/following')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code,200)
            
    
    def test_user_followed_by(self):
        """test user's follower list"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.id1 

            # user2 following user1
            follow = Follows(user_being_followed_id = self.id1, user_following_id = self.id2)
            res = client.get(f'/users/{self.id1}/followers')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code,200)
            self.assertIn("<h4 id=\"sidebar-username\">@test1</h4>",html)

    def test_add_like(self):
        """test add_like views"""
        msg = Message(
            id=123,
            text="what a nice day",
            user_id=self.id2)
        db.session.add(msg)
        db.session.commit()

        # like = Likes(user_id=self.id1,message_id=self.mid)
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.id1 

            res = client.post('/users/add_like/123')
            self.assertEqual(res.status_code,302)

            likes = Likes.query.filter(Likes.message_id==123).all()
            self.assertEqual(len(likes),1)

            likes2 = Likes.query.filter(Likes.user_id==self.id1).all()
            self.assertEqual(len(likes2),1)

    def test_list_likes(self):
        """test listing likes"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.id1 
                user = User.query.get(self.id1)
            res = client.get(f'/users/{self.id1}/likes')
            html = res.get_data(as_text=True)
           
            self.assertEqual(res.status_code,200)
            self.assertIn("<h4 id=\"sidebar-username\">@test1</h4>",html)

    def test_unlike(self):
        """test unlike a message"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.id1
            res = client.post('/users/unlike/1234')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code,302)
            # import pdb
            # pdb.set_trace()
            self.assertEqual(res.location,'http://localhost/users/111')

    def test_add_a_follow(self):
        """test add a follow to a current user view"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.id1
            res = client.post(f'/users/follow/{self.id2}')
            self.assertEqual(res.status_code,302) 
            # import pdb
            # pdb.set_trace()
            self.assertEqual(res.location,'http://localhost/users/111/following')

    def test_stop_following(self):
        """test stop following view"""
        follow = Follows(user_being_followed_id=self.id2,user_following_id=self.id1)
        db.session.add(follow)
        db.session.commit()
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.id1
            res = client.post(f"/users/stop-following/{self.id2}")  
            self.assertEqual(res.status_code,302)  
            self.assertEqual(res.location,f'http://localhost/users/{self.id1}/following')  

    def test_delete_user(self):
        """test delete user view"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.id1

            res = client.post('/users/delete')
            self.assertEqual(res.status_code,302)
            self.assertEqual(res.location,f'http://localhost/signup')  