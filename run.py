import json
import os

import flask_bcrypt
import database

from wrdb import JSON_data
import flask
from flask import url_for
from flask.ext.login import login_required, login_user, logout_user, LoginManager, current_user

########################################

app = flask.Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(userid):
    return session.query(database.User).get(userid)


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return e
    return True


def to_json(data):
    return json.dumps(data) + "\n"


def resp(code, data):
    return flask.Response(
        status=code,
        mimetype="application/json",
        response=to_json(data)
    )


@app.errorhandler(400)
def page_not_found(e):
    return resp(400, {})


# @app.errorhandler(500)
# def page_not_found(e):
#     return flask.render_template("404.html"), 500


@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template("404.html"), 404


@app.errorhandler(405)
def page_not_found(e):
    return resp(405, {})


@app.route("/term")
@login_required
def term():
    flask.redirect("127.0.0.1:5001/terminal", 302)


@app.route('/index')
@app.route('/')
@login_required
def index():
    if current_user.is_anonymous:
        rolename = "anonym"
        return flask.render_template("index.html", username=rolename, role=rolename), 200
    else:
        role = session.query(database.Role).get(current_user.roleid)
        return flask.render_template("index.html", username=current_user.username, role=role.rolename, lines=[]), 200


@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html')
    username = flask.request.form['username']
    password = flask.request.form['password']

    registered_user = session.query(database.User).filter_by(username=username).one_or_none()
    if registered_user is None or not flask_bcrypt.check_password_hash(registered_user.password, password.encode()):
        flask.flash('Username or Password is invalid', 'error')
        return flask.redirect(url_for('login'))
    elif session.query(database.Role).get(registered_user.roleid).rolename != 'admin':
        flask.flash("Only admin users has access to this page", "error")
    else:
        login_user(registered_user)
        flask.flash('Logged in successfully')
    return flask.redirect(url_for('index'))


@app.route("/load_ajax", methods=["GET"])
@login_required
def load_ajax():
    result = []
    with open(database.filename, 'r') as log_file:
        result = ['<div class="content-message">{}</div>'.format(line.strip()) for line in tail(log_file, 30)]
    logger.debug(result)
    return json.dumps(result)


def tail(f, lines=1, _buffer=4098):
    """Tail a file and get N lines from the end"""
    lines_found = []
    block_counter = -1
    while len(lines_found) < lines:
        try:
            f.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:
            f.seek(0)
            lines_found = f.readlines()
            break
        lines_found = f.readlines()
        if len(lines_found) > lines:
            break
        block_counter -= 1
    return lines_found[-lines:]


@app.route('/logout')
def logout():
    logout_user()
    return flask.redirect(url_for('index'))


@app.route('/api/db', methods=['GET', 'POST'])
def get():
    if flask.request.method == "GET":
        logger.info("send validation key")
        return validator
    elif flask.request.method == "POST":
        _json = flask.request.json
        if _json["secret"] == secret:
            logger.info("geted secret key valid...")
            data = JSON_data(_json['data'], session)
            data.write_to_db()
            return '', 200
        else:
            logger.warning("Secret key from JSON data is incorrect")


if __name__ == '__main__':
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("Server started")
    app.debug = False  # enables auto reload during development
    app.secret_key = "Denizantip"
    database.Base.metadata.create_all(database.engine)
    session = database.Session()
    port = 5000
    validator = "72bd44379a82188ccea6dc440ae528754aeada56"
    secret = "12!Secret@erc"
    try:
        app.run(host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        logger.info("server stoped")
