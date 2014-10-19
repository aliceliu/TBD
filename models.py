from google.appengine.ext import db

class Recommendation(db.Model):
    from_user_name = db.StringProperty(required=True)
    to_user_name = db.StringProperty(required=True)
    business_name = db.StringProperty()
    status = db.StringProperty()

class User(db.Model):
    name = db.StringProperty(required=True)
    email = db.StringProperty()
    password = db.StringProperty()

class Friendship(db.Model):
    from_user_name = db.StringProperty(required=True)
    to_user_name = db.StringProperty(required=True)
