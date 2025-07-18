from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
#import os

from helpers import apology, login_required, lookup

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")
#conn = sqlite3.connect("project.db")
#db = conn.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]
    if user_id:
        if request.method == "POST":
            name = request.form.get("name")
            if not name:
                return apology("you forgot to add a child")
            age = request.form.get("age")
            if not age:
                return apology("lack of information")
            disease = request.form.get("disease")
            if not disease:
                return apology("lack of information")
            specialty = request.form.get("symbol")

            try:
                db.execute("INSERT INTO children (name, age, disease, specialty_in_need, family_id) VALUES (?, ?, ?, ?, ?)", name, age, disease, specialty, user_id)
                flash("New baby successfully added!")
            except ValueError:
                return apology("this child already exists")

            doctors = db.execute("SELECT * FROM Doctors WHERE Specialty = ?", specialty)
            return render_template("doctors.html", doctors=doctors)




        else:
            children = db.execute("SELECT * FROM children WHERE family_id =?  ORDER BY age ", user_id)
            specialties = db.execute("SELECT DISTINCT(specialty) FROM Doctors ORDER BY Specialty")

            return render_template("index.html", children=children, specialties=specialties)
    else:
        return redirect("/login")


@app.route("/doctors", methods=["GET", "POST"])
@login_required
def doctors():
    if request.method == "POST":
        child_id = request.form['form_id']
        specialty = db.execute("SELECT specialty_in_need FROM children WHERE id = ?", child_id)
        doctors = db.execute("SELECT * FROM Doctors WHERE Specialty = ?", specialty[0]["specialty_in_need"])

        return render_template("doctors.html", doctors=doctors)

    return render_template("doctors.html")






# this inspired by finance PSET9
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("family_name"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE family_name = ?", request.form.get("family_name")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid family_name and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Logging in succeeded")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



# this inspired by finance PSET9
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# my function register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    if request.method == "POST":
        username = request.form.get("family_name")
        if not username:
            return apology("must provide a name")
        contact = request.form.get("contact")
        if not contact:
            return apology("lack of information")
        password = request.form.get("password")
        if not password:
            return apology("must provide password")
        confirmation = request.form.get("confirmation")
        if not confirmation or not confirmation == password:
            return apology("passwords don't match")
        hash = generate_password_hash(password)
        try:
            new_user = db.execute(
                "INSERT INTO users (family_name, hash, contact) VALUES (?, ?, ?)", username, hash, contact)
        except ValueError:
            return apology("username already exists")
        session["user_id"] = new_user
        flash("Registered!")
        return redirect("/")
    else:
        return render_template("register.html")





@app.route("/search")
@login_required
def search():
    return render_template("search.html")

@app.route("/profile")
@login_required
def profile():
    user_id =session["user_id"]
    family_name = db.execute("SELECT family_name FROM users WHERE id = ?", user_id)
    contact = db.execute("SELECT contact FROM users WHERE id = ?", user_id)
    children = db.execute("SELECT COUNT(name) FROM children WHERE family_id = ?", user_id)

    return render_template("profile.html", family_name=family_name[0]["family_name"], contact=contact[0]["contact"], count=children[0]["COUNT(name)"])


@app.route("/ch_pswrd", methods=["GET", "POST"])
@login_required
def ch_pswrd():
    user_id = session["user_id"]
    if request.method == "POST":
        current = request.form.get("current")
        if not current:
            return apology("Write the current password")

        rows = db.execute(
            "SELECT * FROM users WHERE id = ?", user_id
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], current
        ):
            return apology("invalid password", 403)


        new = request.form.get("updated")
        if not new:
            return apology("empty place")
        confirm = request.form.get("confirm")
        if not confirm:
            return apology("empty place")

        if not new == confirm:
            return apology("Don't match")
        new = generate_password_hash(new)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new, user_id)
        flash("PASSWORD HAS BEEN SUCCESSFULLY CHANGED!")
        return redirect("/")

    return render_template("ch_pswrd.html")

if __name__ == '__main__':
    app.run(debug=True)
