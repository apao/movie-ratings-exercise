"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

SCORES = [1,2,3,4,5]

@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()

    return render_template("user_list.html", users=users)


@app.route('/users/<int:user_id>')
def user_profile(user_id):
    """Show details about a user."""
    
    user = User.get_user_by_id(user_id)

    return render_template('user_detail.html', user=user)


@app.route('/movies')
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<int:movie_id>')
def movie_details(movie_id):
    """Show details about a movie."""

    movie = Movie.get_movie_by_id(movie_id)
    release_date = movie.released_at.strftime("%B %d, %Y")

    return render_template('movie_detail.html', movie=movie, release_date=release_date, scores=SCORES)


@app.route('/checksession')
def check_session():
    """Check if user is logged in"""

    if session.get('username',None):
        user_status = session['username']
    else:
        user_status = 'Does Not Exist'

    return user_status


@app.route('/signin')
def sign_in():
    """Allows users to login."""

    return render_template("signin.html")


@app.route('/confirm_signin', methods=['POST'])
def confirm_sign_in():
    """Confirms user login."""

    username = request.form.get("user_email")
    password = request.form.get("user_password")

    user = User.query.filter_by(email=username).first()

    if user:
        if (user.password == password):
            session['username'] = username
            user_id = user.user_id
            return redirect(url_for("user_profile", user_id=user_id)) 
            # url_for... is same as "/users/" + str(user_id)
        else:
            flash("Incorrect password. Please try again.")
            return redirect('/signin')

    else:
        flash("Account does not exist. Please sign up!")
        return redirect('/signup_form')


@app.route('/confirm_signin_to_rate', methods=['POST'])
def confirm_sign_in_to_rate_movies():
    """Confirms user login from movie details page."""

    username = request.form.get("user_email")
    password = request.form.get("user_password")

    user = User.query.filter_by(email=username).first()

    if user:
        if (user.password == password):
            session['username'] = username
            return session['username']
            # url_for... is same as "/users/" + str(user_id)
        else:
            return 'Does Not Exist'

    else:
        return 'Does Not Exist'


@app.route('/update_rating', methods=['POST'])
def update_rating():
    """Creates/Updates user rating of a specific movie."""

    username = session["username"]
    movie_id = request.form.get("movie_id")
    score = request.form.get("score")
    movie_title = Movie.get_movie_by_id(movie_id).title


    rating_user_id = User.query.filter_by(email=username).first().user_id
    existing_rating = Rating.query.filter(Rating.user_id == rating_user_id, Rating.movie_id == movie_id).first()
    
    if existing_rating:
        existing_rating.score = score
    else:
        new_rating = Rating(movie_id=int(movie_id), user_id=int(rating_user_id), score=int(score))
        db.session.add(new_rating)
    db.session.commit()

    flash("Your rating of " + score + " for " + movie_title + " has successfully been recorded.")

    return redirect("/movies")


@app.route('/signup_form')
def sign_up():
    """Allow new users to sign up."""

    return render_template("signup_form.html")


@app.route('/confirm_signup', methods=['POST'])
def confirm_sign_up():
    """Shows that user has successfully signed up."""

    username = request.form.get("user_email")
    password = request.form.get("user_password")

    user_exists = User.query.filter_by(email=username).first()

    if user_exists:
        flash("User already exists. Please sign in.")
        return redirect('/signin')
    else:
        user = User(email=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Account was successfully created.")
        session['username'] = username
        return redirect('/')


@app.route('/signout')
def signout():
    """Shows that user has successfully signed out."""

    session['username'] = None
    flash("Successfully signed out.")

    return redirect('/')




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
