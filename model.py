"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Represents user object"""
        return "<User ID: %s, Email: %s, Age: %d, Zipcode: %s>" % (self.user_id, self.email, self.age, self.zipcode)


# Put your Movie and Rating model classes here.
class Movie(db.Model):
    """Movie listed on ratings website."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        """Represents movie object"""
        return "<Movie ID: %s, Title: %s>" % (self.movie_id, self.title)


class Rating(db.Model):
    """Rating on ratings website."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    movie = db.relationship('Movie')
    user = db.relationship('User')

    def __repr__(self):
        """Represents user object"""
        return "<Rating ID: %d, Movie ID: %d, User ID: %d, Score: %d>" % (self.rating_id, self.movie_id, self.user_id, self.score)



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
