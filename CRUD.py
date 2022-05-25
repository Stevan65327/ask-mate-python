import database_common
import json
import os



@database_common.connection_handler
def get_entries(cursor, table):
    query = f"""
        SELECT * 
        FROM {table}
        ORDER BY id
    """
    cursor.execute(query)
    return cursor.fetchall()


# this is saving code but I'm not sure it's worth it as it detracts from the readability and two diff functions
@database_common.connection_handler
def increment_votes_views(cursor, table, question_id, column, action):
    if action == "increment":
        query = f"""
            UPDATE {table} 
            SET {column} = {column} + 1
            WHERE id = {question_id}
        """
    elif action == "decrease":
        query = f"""
            UPDATE {table} 
            SET {column} = {column} - 1
            WHERE id = {question_id}
                """
    else:
        return
    cursor.execute(query)


@database_common.connection_handler
def update_question(cursor, table, question_id, title, message):
    query = f"""
            UPDATE {table} 
            SET title = '{title}', message = '{message}'
            WHERE id = {question_id}
                """
    cursor.execute(query)


@database_common.connection_handler
def add_new_question(cursor, title, message, image):
    query = f"""
        INSERT INTO question(submission_time, view_number, vote_number, title, message, image)
        VALUES(current_timestamp, 0, 0,'{title}' ,'{message}', '{image}')        
    """
    cursor.execute(query)


@database_common.connection_handler
def add_new_answer(cursor, message, question_id, image):
    query = f"""
        INSERT INTO answer(submission_time, vote_number, question_id, message, image)
        VALUES(current_timestamp, 0, {question_id}, '{message}', '{image}')        
    """
    cursor.execute(query)


@database_common.connection_handler
def delete_question(cursor, question_id):
    query = f"""
        DELETE FROM question 
        WHERE id = {question_id}
    """
    cursor.execute(query)


@database_common.connection_handler
def add_new_comment(cursor, question_id, message, answer_id='NULL'):
    query = f"""
        INSERT INTO comment(question_id, answer_id, message, submission_time, edited_count)
        VALUES({question_id},{answer_id},'{message}', current_timestamp, 0)
    """
    cursor.execute(query)


@database_common.connection_handler
def update_comment(cursor, comment_id, message):
    query = f"""
            UPDATE comment 
            SET message = '{message}', 
            submission_time = current_timestamp, 
            edited_count = edited_count + 1 
            WHERE id = {comment_id}
                """
    cursor.execute(query)


@database_common.connection_handler
def delete_comment(cursor, comment_id):
    query = f"""
        DELETE FROM comment 
        WHERE id = {comment_id}
    """
    cursor.execute(query)


@database_common.connection_handler
def sort_questions(cursor, table, column, direction):
    query = f"""
        SELECT * 
        FROM {table}
        ORDER BY {column} {direction}
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_latest_questions(cursor):
    query = f"""
        SELECT * 
        FROM question
        ORDER BY submission_time DESC
        LIMIT 5
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def upload_image(cursor, question_id, saved_file):
    query = f"""
        UPDATE question
        SET image = '{saved_file}'
        WHERE id = {question_id} 
    """
    cursor.execute(query)


@database_common.connection_handler
def question_string_search(cursor, search_phrase):
    query = f"""
    SELECT *
    FROM question 
    WHERE title ilike '%{search_phrase}%'
    OR message ilike '%{search_phrase}%'
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_question(cursor, question_id):
    query = f"""
    SELECT * 
    FROM question
    WHERE id = {question_id}
    """
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_comments(cursor, question_id):
    query = f"""
    SELECT *
    FROM comment
    WHERE question_id = {question_id}
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answer(cursor, answer_id):
    query = f"""
    SELECT * 
    FROM answer 
    WHERE id = {answer_id}
    """
    cursor.execute(query)
    return cursor.fetchone()

@database_common.connection_handler
def get_answers(cursor, question_id):
    query = f"""
    SELECT * 
    FROM answer
    WHERE question_id = {question_id}
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_user_data(cursor, username, password):
    query = f"""
        INSERT INTO users (username, password, registration_date)
        VALUES ('{username}','{password}',current_date)
    """
    cursor.execute(query)


@database_common.connection_handler
def get_user_details(cursor, username):
    query = f"""
    SELECT username, password
    FROM users where username = '{username}'
    """
    cursor.execute(query)
    return cursor.fetchone()

