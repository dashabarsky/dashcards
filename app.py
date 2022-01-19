# import dependencies
import random

from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from config import wordpath, mastery_levels, all_ranks
from helpers import error, parse_csv, update_words_per_user, get_available_words, db
from cs50 import SQL

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded. Reused from CS50 Week 9 - Finance
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies). Reused from CS50 Week 9 - Finance
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached. Reused from CS50 Week 9 - Finance"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    """Landing page - just render the homepage.
    If the user is logged in, this offers the user to start a session or logout.
    Otherwise, it offers them to register or login"""

    words_remaining = len(get_available_words(parse_csv(wordpath))) if session.get("user_id") else None

    return render_template("index.html", words_remaining=words_remaining, return_path="/")

@app.route("/cards", methods=["GET", "POST"])
def cards():
    """Display the next word for the user to answer, if any are available
    (otherwise show a message asking them to wait a while)
    Also display the results from the last answer they gave"""

    # if not logged in, redirect them to the homepage
    if session.get("user_id") is None:
        return redirect("/")

    # Parse the CSV to get the dictionary of words (in case it's changed)
    word_dict = parse_csv(wordpath)

    # Initialise the dict which passes information about the previously answered word
    last_word_results = None

    # If the user just answered a word
    if request.method == "POST":

        # Get details about the last answered word
        last_word = request.form.get("word")
        if not last_word:
            return error("Something went wrong - possibility that the HTML of the webpage has been tampered with. Please contact your admin.", request.path)

        last_user_answer = request.form.get("answer")
        if not last_user_answer:
            return error("Please enter an answer!", request.path)

        if last_word in word_dict["words"]:
            last_expected_answer = word_dict["words"][last_word]["answer"]
        else:
            return error("Something went wrong - possibility that the HTML of the webpage has been tampered with. Please contact your admin.", request.path)

        # Handle correct and incorrect answers
        # Pass outcome to the HTML template and update the words database accordingly
        if last_user_answer.lower() == last_expected_answer:
            update_words_per_user(last_word, True, word_dict)
            outcome = "correct"
        else:
            update_words_per_user(last_word, False, word_dict)
            outcome = "incorrect"

        # Build dict to send to the template
        last_word_results = {'word': last_word,
                             'expected_answer': last_expected_answer,
                             'user_answer': last_user_answer,
                             'outcome': outcome}

    # Get a list of available words
    available_words = get_available_words(word_dict)

    # Return the 'run out of words' template if no words available
    if len(available_words) == 0:
        return render_template("runout.html", last_word_results = last_word_results)

    # Otherwise, pick a word at random and pass it through to the template
    word_to_present = random.choice(available_words)
    return render_template("cards.html", word_to_present = word_to_present, last_word_results = last_word_results, words_remaining = len(available_words))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in. Based on CS50 Week 9 - Finance"""

    # Log the user out if they aren't already
    session.pop('user_id', None)

    if request.method == "POST":
        # Validate that user has included username and memorable phrase
        if not request.form.get("username"):
            return error("Username field cannot be empty.", request.path)
        elif not request.form.get("memorable-phrase"):
            return error("Memorable phrase field cannot be empty.", request.path)

        # Find the user
        rows = db.execute("SELECT * FROM user_login WHERE username = ?",
                          request.form.get("username"))

        # Check that the username exists in database and the memorable phrase is right
        if len(rows) == 0 or not check_password_hash(rows[0]["hash"], request.form.get("memorable-phrase")):
            return error("That wasn't quite right. Please check your username and memorable phrase and try again.",
                         request.path)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out. Based on CS50 Week 9 - Finance"""

    # Forget any user_id
    session.pop('user_id', None)

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Check if form has been submitted
    if request.method == "POST":

        # Get field inputs
        user_name = request.form.get("username")
        user_pw = request.form.get("memorable-phrase")
        user_pw_conf = request.form.get("confirmation")

        # Validate that all fields are populated and passwords match
        if not user_name:
            return error("Username field cannot be empty.", request.path)
        elif not user_pw or not user_pw_conf:
            return error("Memorable phrase field cannot be empty.", request.path)
        elif user_pw != user_pw_conf:
            return error("The memorable phrase must match.", request.path)

        # Check whether username exists
        rows = db.execute("SELECT * FROM user_login WHERE username = ?",
                          user_name)

        if len(rows) > 0:
            return error("Username already exists, please choose another.", request.path)

        # Hash the user's password
        hash_pw = generate_password_hash(user_pw)

        # Upload the user to the database
        db.execute("INSERT INTO user_login(username,hash) VALUES(?,?)",
                   user_name, hash_pw)

        # get the user's ID from newly-created row to initialise their user_stats
        user_id = rows = db.execute("SELECT * FROM user_login WHERE username = ?",
                                    request.form.get("username"))[0]["id"]
        db.execute("INSERT INTO user_stats(user_id,current_rank) VALUES(?,?)",
                   user_id,all_ranks[0])

        # use that same ID to log them in straight away
        session["user_id"] = user_id

        # Redirect to home page
        return redirect("/")

    # Display the register form
    return render_template("register.html")

@app.route("/stats")
def stats():
    # if not logged in, redirect them to the homepage
    if session.get("user_id") is None:
        return redirect("/")

    # get the user's rank
    user_stats = db.execute("SELECT * FROM user_stats WHERE user_id = ?",session["user_id"])[0]

    # get all words the user has answered and the stats of each
    all_user_words = db.execute("SELECT * FROM words_per_user WHERE user_id = ?",session["user_id"])

    # initialise
    user_levels_by_rank = {}

    for rank in all_ranks:
        user_levels_by_rank[rank] = {"total": 0, "levels": {}}
        for mastery_level in mastery_levels:
            user_levels_by_rank[rank]["levels"][mastery_level["level"]] = 0

    # calculate how many words at each rank the user has learned to each master level
    for word in all_user_words:
        this_word_rank = word["rank"]
        this_word_level = word["level"]

        user_levels_by_rank[this_word_rank]["levels"][this_word_level] += 1
        user_levels_by_rank[this_word_rank]["total"] += 1

    words_remaining = len(get_available_words(parse_csv(wordpath))) if session.get("user_id") else None

    # pass rank and all words to the page template
    return render_template("stats.html", user_rank = user_stats["current_rank"],
                           user_words = all_user_words,
                           user_levels_by_rank = user_levels_by_rank,
                           mastery_levels = mastery_levels,
                           words_remaining = words_remaining)

@app.route('/getmethod/<jsdata>')
def get_javascript_data(jsdata):
    """Sets colour mode (light mode or dark mode) from AJAX request when user toggles"""
    session["colour_mode"] = jsdata
    return jsdata