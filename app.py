from flask import Flask, request, render_template, session, redirect, url_for
from db import test_connection, get_connection
import psycopg2



app = Flask(__name__)
app.secret_key = "e3b6f7c2fd1e497bb3c1f0c39d3be24f1fa91d3f260a9fc715f68699fbd55e80"

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    user = request.form['user']
    password = request.form['password']

    try:
        # test database connection
        conn = test_connection(user, password)
        conn.close()

        # save credentials in session
        session['db_user'] = user
        session['db_pass'] = password

        # redirect to search page
        return redirect(url_for('search'))

    except Exception as e:
        return f"Connection failed: {e}"


@app.route('/search', methods=['GET', 'POST'])
def search():
    # make sure user is logged in
    if 'db_user' not in session or 'db_pass' not in session:
        return redirect(url_for('home'))

    if request.method == 'GET':
        # render search form
        return render_template("query.html")

    # POST: process search query
    major = request.form.get('major')
    state = request.form.get('state')

    try:
        conn = get_connection(session['db_user'], session['db_pass'])
        cur = conn.cursor()
        query = """
            SELECT *
            FROM institutions i
            WHERE i.major = %s
            AND i.state = %s;
        """
        values = (major, state)
        cur.execute(query, values)
        results = cur.fetchall()
        cur.close()
        conn.close()

        # render results page
        return render_template("results.html", results=results)

    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)