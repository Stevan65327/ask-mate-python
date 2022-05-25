import datetime
from psycopg2 import errors
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from bonus_questions import SAMPLE_QUESTIONS
from functools import wraps
import CRUD
import util
import os


# initializing application
app = Flask(__name__)
app.secret_key = 'donttellanyone'


# Global variables and constants
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.join(os.path.curdir, 'static'), "images"))
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get('username'):
            backurl = request.path
            return redirect(url_for('login', backurl=backurl))
        return function(*args, **kwargs)
    return wrapper


@app.route("/")
def index():
    if not request.args:
        questions = CRUD.get_latest_questions()
    else:
        search_phrase = request.args.get("search_phrase")
        questions = CRUD.question_string_search(search_phrase)
    return render_template("index.html", data=questions)


@app.route("/list")
def display_question_list():
    """Displays the list of questions and their attributes on the home page."""
    questions = CRUD.get_entries("question")
    query_string = request.args
    if query_string:
        questions = CRUD.sort_questions("question", query_string["sort_by"], query_string["direction"])
    return render_template('list.html', data=questions)


@app.route("/question/<question_id>")
def display_question(question_id):
    """Displays a single question on it's own page, along with attributes and edit options."""
    CRUD.increment_votes_views("question", question_id, "view_number", "increment")
    question = CRUD.get_question(question_id)
    answers = CRUD.get_answers(question_id)
    comments = CRUD.get_comments(question_id)
    return render_template('question.html', question=question,
                           answers=answers,
                           question_id=int(question_id),
                           comments=comments)


@app.route("/question/<question_id>/new-answer")
def display_add_answer(question_id):
    """Displays the page that allows the user to input a new answer and submit it to server."""
    question = CRUD.get_question(question_id)
    return render_template("new-answer.html", question=question)


@app.route("/question/<question_id>/new-answer", methods=["POST"])
def redirect_new_answer(question_id):
    """Redirects the user back to the question page after answer submission and displays the new answer."""
    # declaring the values to be added to answer
    # to-do, fix apostrophe through parameterized SQL
    message = request.form.get("answer")
    image = 'NULL'
    # adding question to db
    CRUD.add_new_answer(message, question_id, image)
    return redirect(url_for('display_question', question_id=int(question_id)))


# should delete through DELETE method
@app.route("/question/<question_id>/delete", methods=["POST", "GET"])
def delete_question(question_id):
    """Deletes a question from the questions list and redirects the user to the list of questions."""
    if request.method == 'POST':
        CRUD.delete_question(question_id)
        return redirect(url_for('display_question_list'))
    return render_template("confirm_deletion.html", question_id=question_id)


@app.route("/add-question")
@login_required
def display_add_question():
    """Displays the page allowing the user to submit a new question."""
    return render_template("add-question.html")


@app.route("/add-question", methods=['POST'])
def redirect_add_question():
    """After a user has added a question, redirect them back to the main page, where the new question can be seen."""
    if request.method == "POST":
        # readying values for new question
        title = request.form['title']
        message = request.form['message']

        # if image uploaded, get file path
        uploaded_image = request.files['image_file']
        if uploaded_image.filename != '':
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_image.filename)
            uploaded_image.save(image_path)
            # CRUD.upload_image(question_id, os.path.join("images", uploaded_image.filename), )
        else:
            image_path = 'Null'

        # add new entry to question table
        CRUD.add_new_question(title, message, image_path)

    return redirect(url_for('display_question_list'))


# what's this doing here?
@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route("/question/<question_id>/edit", methods=['GET', 'POST'])
def edit_question(question_id):
    """Brings the user to a form where they can edit the question.  Upon submission, redirects to questions list."""
    if request.method == "POST":
        title = request.form['title']
        message = request.form['message']
        CRUD.update_question("question", question_id, title, message)
        return redirect(url_for('display_question_list'))
    question = CRUD.get_question(question_id)
    return render_template("edit_question.html", question=question)


# open question here about how to cache on FE rather than reloading each time?
@app.route("/answer/<answer_id>/vote-up")
def answer_vote_up(answer_id):
    CRUD.increment_votes_views("answer", answer_id, "vote_number", "increment")
    return redirect(request.referrer)


@app.route("/answer/<answer_id>/vote-down")
def answer_vote_down(answer_id):
    CRUD.increment_votes_views("answer", answer_id, "vote_number", "decrease")
    return redirect(request.referrer)


@app.route("/question/<question_id>/vote-up")
def question_vote_up(question_id):
    CRUD.increment_votes_views("question", question_id, "vote_number", "increment")
    return redirect(url_for('display_question_list'))


@app.route("/question/<question_id>/vote-down")
def question_vote_down(question_id):
    CRUD.increment_votes_views("question", question_id, "vote_number", "decrease")
    return redirect(url_for('display_question_list'))


@app.route("/question/<question_id>/new-comment")
def show_new_comment_form(question_id):
    question = CRUD.get_question(question_id)
    return render_template('question_new_comment.html', question_id=int(question_id), question=question)


@app.route("/question/<question_id>/new-comment", methods=['POST'])
def new_question_comment(question_id):
    new_comment = request.form['comment']
    CRUD.add_new_comment(question_id, new_comment)
    return redirect(url_for('display_question', question_id=question_id))


# We should separate out routes/functions based on their request type here
@app.route("/answer/<answer_id>/new-comment", methods=['GET', 'POST'])
def new_answer_comment(answer_id):

    if request.method == 'POST':
        question_id = request.form.get('question_id')
        new_comment = request.form['comment']
        CRUD.add_new_comment(question_id, new_comment, answer_id)
        return redirect(url_for('display_question', question_id=question_id))

    answer = CRUD.get_answer(answer_id)
    return render_template('answer_new_comment.html', answer_id=int(answer_id), answer=answer)


@app.route("/comment/<question_id>/<comment_id>/edit", methods=['GET', 'POST'])
def edit_comment(comment_id, question_id):
    if request.method == 'POST':
        new_comment = request.form['message']
        CRUD.update_comment(comment_id, new_comment)
        return redirect(url_for('display_question', question_id=int(question_id)))
    comments = CRUD.get_comments(question_id)
    return render_template('edit_comment.html', comment_id=int(comment_id), comments=comments,
                           question_id=int(question_id))


@app.route("/comment/<question_id>/<comment_id>/delete")
def delete_comment(comment_id, question_id):
    CRUD.delete_comment(comment_id)
    return redirect(url_for('display_question', question_id=int(question_id)))


@app.route("/registration", methods=['GET'])
def display_registration_page():
    return render_template("registration.html")


@app.route("/registration", methods=['POST'])
def register_new_user():
    username_taken_error = errors.lookup('23505')
    try:
        username = request.form.get("username")
        password = util.hash_password(request.form.get("password"))
        CRUD.add_user_data(username, password)
        return redirect(url_for('index'))
    except username_taken_error:
        error_message = "This username has already been taken, please try again"
        return render_template("registration.html", error_message=error_message)


@app.route("/login")
def display_login_page():
    return render_template("login.html")


@app.route("/login", methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if util.validate_user_credentials(username, password):
        session['username'] = username
        return redirect('/')
    error_message = "Incorrect Credentials, please try again"
    return render_template("login.html", error_message=error_message)


@app.route("/users")
@login_required
def display_users_list():
    """Displays the list of users and their registration date in a table."""
    users = CRUD.get_entries("users")
    return render_template('users.html', data=users)


@app.route("/logout", methods=['POST', 'GET'])
@login_required
def logout():
    if request.method == 'POST':
        session.pop('username')
        return redirect('/')
    return render_template('logout.html')


if __name__ == "__main__":
    app.run()
