from flask import session

from shared_code import aad_helper


def set_session_variables():
    name, email = aad_helper.get_name_and_email_address()
    session['user_name'] = name
    session['user_email'] = email