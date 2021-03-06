"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy

from correlation import pearson

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
    email = db.Column(db.String(64), nullable=True, unique=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Represents user object"""
        return "<User ID: %s, Email: %s>" % (self.user_id, self.email)

    @classmethod
    def get_user_by_id(cls,user_id):

        user = User.query.filter_by(user_id=user_id).first()

        return user

    def similarity(self, other):
        """Return Pearson rating for user compared to other user."""

        user_ratings = {}
        paired_ratings = []

        for rating in self.ratings:
            user_ratings[rating.movie_id] = rating

        for rating in other.ratings:
            other_user_rating = user_ratings.get(rating.movie_id)
            if other_user_rating:
                paired_ratings.append(( other_user_rating.score, rating.score))

        if paired_ratings:
            return pearson(paired_ratings)

        else:
            return 0.0

    def predict_rating(self, movie):
        """Predict user's rating of a movie."""

        other_ratings = movie.ratings

        similarities = [(self.similarity(rating.user), rating)
                       for rating in other_ratings]

        similarities.sort(reverse=True)

        positive_similarities = [(sim, rating) for sim, rating \
                                in similarities if sim > 0]

        negative_similarities = [(sim, rating) for sim, rating \
                                in similarities if sim < 0]

        if not positive_similarities and not negative_similarities:
            return None

        numerator = sum([r.score * sim for sim, r in positive_similarities]) \
                    + sum([((r.score - 6) * sim) for sim, r in negative_similarities])

        denominator = sum([abs(sim) for sim, rating in similarities])

        predicted_rating = numerator/denominator

        return predicted_rating


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

    @classmethod
    def get_movie_by_id(cls, movie_id):

        movie = Movie.query.filter_by(movie_id=movie_id).first()

        return movie 


class Rating(db.Model):
    """Rating on ratings website."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    movie = db.relationship('Movie', backref=db.backref('ratings', order_by=rating_id))
    user = db.relationship('User', backref=db.backref('ratings', order_by=rating_id))

    def __repr__(self):
        """Represents rating object"""
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
