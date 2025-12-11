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
        conn = test_connection(user, password)
        conn.close()

        session['db_user'] = user
        session['db_pass'] = password

        return redirect(url_for('search'))

    except Exception as e:
        return f"Connection failed: {e}"


@app.route('/search', methods=['GET', 'POST'])
def search():
    # make sure user is logged in
    if 'db_user' not in session or 'db_pass' not in session:
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template("query.html")

    major = request.form.get('major')
    state = request.form.get('state').upper().strip()

    try:
        conn = get_connection(session['db_user'], session['db_pass'])
        cur = conn.cursor()

        cur.execute("SET search_path TO jett_morrandez;")

        # Main query for results table
        query = """
            SELECT DISTINCT s.Major, 
            (s.startingmediansalary * 10 - COALESCE(i.costt4_a, 0)*4) AS roi, i.costt4_a,
            i.INSTNM
            FROM programs p
            JOIN degree_to_salary s ON p.majorid = s.majorid
            JOIN institutions i ON p.UNITID = i.UNITID
            WHERE i.STABBR = %s
                AND s.Major = %s
                AND p.CREDDESC = 'Bachelor''s Degree'
            ORDER BY roi DESC;
        """
        cur.execute(query, (state, major))
        results = cur.fetchall()

        # Data for sunburst chart - salary ranges by major
        sunburst_query = """
            SELECT s.Major,
                   CASE 
                       WHEN s.startingmediansalary < 45000 THEN 'Low'
                       WHEN s.startingmediansalary < 65000 THEN 'Medium' 
                       ELSE 'High'
                   END as salary_range,
                   COUNT(*) as count
            FROM programs p
            JOIN degree_to_salary s ON p.majorid = s.majorid
            JOIN institutions i ON p.UNITID = i.UNITID
            WHERE i.STABBR = %s AND p.CREDDESC = 'Bachelor''s Degree'
            GROUP BY s.Major, salary_range
            ORDER BY s.Major;
        """
        cur.execute(sunburst_query, (state,))
        sunburst_data = cur.fetchall()

        chart_labels = [row[2] for row in results]  # Institution names
        chart_values = [float(row[1]) if row[1] else 0 for row in results]

        cur.close()
        conn.close()

        return render_template(
            "results.html",
            results=results,
            chart_labels=chart_labels,
            chart_values=chart_values,
            sunburst_data=sunburst_data,
            state=state
        )
    except Exception as e:
        return f"Error: {e}"

@app.route('/logout')
def logout():
    # Clear all session data
    session.clear()
    # Redirect to the home/login page
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
