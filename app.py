from flask import Flask, render_template, redirect, session, url_for, flash, request
from data.db_session import db_auth
#from services.accounts_service import create_user, login_user, get_profile, update_profile
from services.accounts_service import *
import os

app = Flask(__name__) #create application
app.secret_key = os.urandom(24) 

graph = db_auth() #connect to neo4j


@app.route('/')
def index():
    return render_template("home/index.html")


@app.route('/accounts/register', methods=['GET'])
def register_get():
    return render_template("accounts/register.html")


@app.route('/accounts/register', methods=['POST'])
def register_post():
    # Get the form data from register.html
    name = request.form.get('name')
    email = request.form.get('email').lower().strip()
    company = request.form.get('company').strip()
    password = request.form.get('password').strip()
    confirm = request.form.get('confirm').strip()

    # Check for blank fields in the registration form
    if not name or not email or not company or not password or not confirm:
        flash("Please populate all the registration fields", "error")
        return render_template("accounts/register.html", name=name, email=email, company=company, password=password, confirm=confirm)

    # Check if password and confirm match
    if password != confirm:
        flash("Passwords do not match")
        return render_template("accounts/register.html", name=name, email=email, company=company)

    # Create the user
    user = create_user(name, email, company, password)
    # Verify another user with the same email does not exist
    if not user:
        flash("A user with that email already exists.")
        return render_template("accounts/register.html", name=name, email=email, company=company)

    return redirect(url_for("profile_get"))


@app.route('/accounts/login', methods=['GET'])
def login_get():
    # Check if the user is already logged in.  if yes, redirect to profile page.
    if "usr" in session:
        return redirect(url_for("profile_get"))
    else:
        return render_template("accounts/login.html")


@app.route('/accounts/login', methods=['POST'])
def login_post():
    # Get the form data from login.html
    email = request.form['email']
    password = request.form['password']
    if not email or not password:
        return render_template("accounts/login.html", email=email, password=password)

    # Validate the user
    user = login_user(email, password)
    if not user:
        flash("No account for that email address or the password is incorrect", "error")
        return render_template("accounts/login.html", email=email)

    # Log in user and create a user session, redirect to user profile page.
    usr = request.form["email"]
    session["usr"] = usr
    return redirect(url_for("profile_get"))


@app.route('/accounts/profile', methods=['GET'])
def profile_get():
    # Make sure the user has an active session.  If not, redirect to the login page.
    if "usr" in session:
        usr = session["usr"]
        session["usr"] = usr
        user_profile = get_profile(usr)
        return render_template("accounts/index.html", user_profile=user_profile)
    else:
        return redirect(url_for("login_get"))


@app.route('/accounts/profile', methods=['POST'])
def profile_post():
    # Get the data from index.html
    name = request.form.get('name')
    company = request.form.get('company').strip()
    # Make sure the user has an active session.  If not, redirect to the login page.
    if "usr" in session:
        usr = session["usr"]
        session["usr"] = usr
        user_profile = update_profile(usr, name, company)
        user_profile = get_profile(usr)
        return render_template("accounts/index.html", user_profile=user_profile)
    else:
        return redirect(url_for("login_get"))

@app.route('/accounts/equipments', methods=['GET'])
def equipments_get():
    if "usr" in session:
        usr = session["usr"]
        session["usr"] = usr
        user_equipments = get_equipments(usr)
        if not user_equipments:
            flash("Don't have any equipment yet! Please add a equipment first", "error")
            #user_equipments = create_equipments()
        return render_template("accounts/equipments.html", user_equipments = user_equipments)
    else:
        return redirect(url_for("login_get"))

@app.route('/accounts/equipments', methods=['POST'])

def equipments_post():
    Site = request.form.get('site').strip()
    Longitude = request.form.get('longitude').strip()
    Latitude = request.form.get('latitude').strip()
    Altitude = request.form.get('altitude').strip()
    tz = request.form.get('time_zone').strip()
    daylight = request.form.get('daylight_saving').strip()
    wv = request.form.get('water_vapor').strip()
    light_pollusion = request.form.get('light_pollusion').strip()
    eid = request.form.get('equipment_id').strip()
    if "usr" in session:
        usr = session["usr"]
        session["usr"] = usr
        #user_equipments = update_equipments()
        print(usr)
        print(eid)
        user_equipments = create_equipments(usr,eid,Site,Longitude,Latitude,Altitude,tz,daylight,wv,light_pollusion)
        user_equipments = get_equipments(usr)
        return render_template("accounts/equipments.html", user_equipments = user_equipments)
    else:
        return redirect(url_for("login_get"))

@app.route('/accounts/logout')
def logout():
    session.pop("usr", None)
    flash("You have successfully been logged out.", "info")
    return redirect(url_for("login_get"))


if __name__ == '__main__':
    app.run(debug=True)