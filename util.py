import CRUD
import time
import bcrypt
from datetime import datetime


def create_new_answer(message, question_id):
    answer_list = CRUD.read('answers.csv')
    answer_id = len(answer_list) + 1
    submission_time = int(time.time())
    vote_number = str(0)
    image = None

    return [answer_id, submission_time, vote_number, question_id, message, image]


# Going to borrow this for the answer ID
def create_new_question_id():
    questions = CRUD.read("questions.csv")
    for row in questions:
        if row == 0:
            pass
        else:
            new_id = int(row[0])+1
    return new_id


# Probably don't need this, we should create the same format submission times for both questions/answers
# and manipulate them when we display them -- Emerson
def create_new_question_submission_time():
    return datetime.now()


def hash_password(password):
    # By using bcrypt, the salt is saved into the hash itself
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def validate_user_credentials(username, password):
    user_details = CRUD.get_user_details(username)
    if user_details:
        hashed_password = user_details["password"]
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    return False
