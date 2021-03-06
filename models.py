from google.appengine.ext import db

class Recommendation(db.Model):
    from_user_name = db.StringProperty(required=True)
    to_user_name = db.StringProperty(required=True)
    business_name = db.StringProperty()
    status = db.StringProperty()
    category = db.StringProperty()
    yelp_url = db.StringProperty()
    image_url = db.StringProperty()
    comment = db.TextProperty()

class User(db.Model):
    name = db.StringProperty(required=True)
    email = db.StringProperty()
    password = db.StringProperty()

class Friendship(db.Model):
    from_user_name = db.StringProperty(required=True)
    to_user_name = db.StringProperty(required=True)

class Invitee(db.Model):
    email = db.StringProperty(required=True)
