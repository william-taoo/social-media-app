import flask
import sqlite3
import hashlib
from datetime import datetime

def create_app():
    app = flask.Flask(__name__)

    conn = sqlite3.connect('data/database.db')
    # sql - username and password (becomes hashed)
    sql = "CREATE TABLE IF NOT EXISTS user_pass (username TEXT NOT NULL, hashed_code TEXT)" 
    # sql2 - id (the hashed password), name, and email
    sql2 = "CREATE TABLE IF NOT EXISTS personal_info (id TEXT PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL, email EMAIL NOT NULL)" 
    # sql3 - post data
    sql3 = "CREATE TABLE IF NOT EXISTS posts (title TEXT NOT NULL, content TEXT NOT NULL, date TEXT NOT NULL, user TEXT NOT NULL, hashcode TEXT NOT NULL)"
    conn.execute(sql)
    conn.execute(sql2)
    conn.execute(sql3)
    conn.commit()
    conn.close()

    @app.route('/', methods=['GET'])
    def default():
        return flask.redirect(flask.url_for('register')) # automatically directs to the register page

    @app.route('/register')
    def register_form():
        return flask.render_template('register.html') # The register page

    @app.route('/register', methods=['POST'])
    def register():
        # Get the username and password from the user's input
        username = flask.request.form['username']
        password = flask.request.form.get('password')

        # Using sha256 to hash the username and password (if provided)
        if password:
            hashed_code = hashlib.sha256((username + password).encode('utf-8')).hexdigest()
        else:
            hashed_code = hashlib.sha256(username.encode('utf-8')).hexdigest()

        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_pass WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        # Looks to see if you are already registered, if you are, then pressing register/login will automatically send you to the profile page
        if existing_user:
            cursor.execute("SELECT * FROM personal_info WHERE id = ?", (hashed_code,))
            existing_hash = cursor.fetchone()
            if existing_hash:
                return flask.redirect(flask.url_for('profile', hashcode=hashed_code))
            else:
                return flask.redirect(flask.url_for('signup', id=hashed_code))
        else:
            # Insert the information to the database with sql injection protection in mind
            cursor.execute(f"INSERT INTO user_pass (username, hashed_code) VALUES(?, ?)", (username, hashed_code))

        conn.commit()
        cursor.close()
        conn.close()

        # Redirects you to the info function where the id will be a part of the app.route
        return flask.redirect(flask.url_for('info', id=hashed_code))

    @app.route('/personal_info/<id>', methods=['GET', 'POST'])
    def info(id):
        id = id
        if flask.request.method == 'GET':
            return flask.render_template('personal_info.html', id=id)
        else:
            first_name = flask.request.form['first_name']
            last_name = flask.request.form['last_name']
            email = flask.request.form['email']
            
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO personal_info (id, first_name, last_name, email) VALUES(?, ?, ?, ?)", (id, first_name, last_name, email))
            conn.commit()
            conn.close()

        return flask.redirect(flask.url_for('profile', hashcode=id))

    @app.route('/profile/<hashcode>', methods=['GET', 'POST'])
    def profile(hashcode):
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personal_info WHERE id = ?", (hashcode,))
        info = cursor.fetchall()
        cursor.execute("SELECT u.username FROM user_pass u WHERE u.hashed_code = ?", (hashcode,))
        username = cursor.fetchone()

        # Getting post info
        cursor.execute("SELECT * FROM posts WHERE hashcode = ?", (hashcode, ))
        post_info = cursor.fetchall()
        conn.close()

        if flask.request.method == 'GET':
            return flask.render_template('profile.html', info=info, username=username, post_info=post_info) 
        
        return flask.redirect(flask.url_for('create', hashcode=hashcode))

    @app.route('/create/<hashcode>', methods=['GET', 'POST'])
    def create(hashcode):
        if flask.request.method == 'POST':
            title = flask.request.form['title']
            content = flask.request.form['content']
            date = flask.request.form['date']
            date = datetime.fromtimestamp(int(date) / 1000.0)
            formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')

            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT u.username FROM user_pass u WHERE u.hashed_code = ?", (hashcode,))
            user = cursor.fetchone()
            cursor.execute("INSERT INTO posts (title, content, date, user, hashcode) VALUES (?, ?, ?, ?, ?)", (title, content, formatted_date, user[0], hashcode))
            conn.commit()
            conn.close()

            return flask.redirect(flask.url_for('profile', hashcode=hashcode))
        
        return flask.render_template('create.html', hashcode=hashcode)
    
    @app.route('/home', methods=['GET'])
    def home():
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts")
        postdata = cursor.fetchall() # Gets all the post data to be displayed on home page
        conn.commit()
        conn.close()

        return flask.render_template('homepage.html', postdata=postdata)


    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=5500, host='127.0.0.1', debug=True, use_evalex=False, use_reloader=False)