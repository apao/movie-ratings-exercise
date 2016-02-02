"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

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
            flash("Successfully logged in.")
            return redirect('/')
        else:
            flash("Incorrect password. Please try again.")
            return redirect('/signin')

    else:
        flash("Account does not exist. Please sign up!")
        return redirect('/signup_form')


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
        flash("User already exists. Please login.")
    else:
        user = User(email=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Account was successfully created.")

    return redirect('/signin')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
