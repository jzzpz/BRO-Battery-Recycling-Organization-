from flask import Flask, render_template, session, redirect, url_for, request, escape, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_googlemaps import GoogleMaps, Map
import re, requests
import json
import geocoder
import time

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["GOOGLEMAPS_KEY"] = "AIzaSyClpBTt3Vn_4yvufx-cZgq_XJKVk7MIBfA"
app.secret_key = b'kjkl3jk35jk3xciifo'
db = SQLAlchemy(app)
GoogleMaps(app)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    results = get_db()
    #for result in results:
    #    print(result)
    print(results)
    # creating a map in the view

    cur_loc = get_cur_loc()
    sndmap = Map(
        identifier="sndmap",
        lat=cur_loc[0],
        lng=cur_loc[1],
        style="height:700px;width:100%;margin:0",
        zoom = 13,
        markers = [{'lat': result[-2], 'lng': result[-1], 'infobox': "<h3>{}</h3><p><b>address: </b>{}</p>".format(result[0], result[3])} for result in results] + [{'lat': cur_loc[0],
                        'lng': cur_loc[1],
                        'infobox': '<h3>current location</h3>',
                        'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
                        }],
    )
    print(sndmap.markers)
    coords_list = [{'lat': result[-2], 'lng': result[-1], 'company': result[0], 'address': result[3]} for result in results] + [{'lat': cur_loc[0], 'lng': cur_loc[1]}]
    print(coords_list)
    #time.sleep(5)
    if "logged_in" in session and session['logged_in']:
        return render_template('index.html', sndmap=sndmap, coords=coords_list, username=session['username'], cmd='<a class=\"nav-link\" href=\"./logout\">LOGOUT</a>')
    else:
        return render_template("index.html", sndmap=sndmap, coords=coords_list, username="LOGIN", cmd='<a class=\"nav-link\" href=\"./signup\">SIGNUP</a>')
        #return render_template('index.html', sndmap=sndmap, coords=coords_list)

    #return render_template("index.html", results=results)

@app.route("/path")
def path():
    cur_loc = get_cur_loc()
    cur_loc[0] = str(cur_loc[0])
    cur_loc[1] = str(cur_loc[1])
    results = get_db()
    print(results)
    if "logged_in" in session and session['logged_in']:
        return render_template("temp1.html", cur_loc=cur_loc, results=results, username=session['username'], cmd='<a class=\"nav-link\" href=\"./logout\">LOGOUT</a>')
    else:
        return render_template("temp1.html", cur_loc=cur_loc, results=results, username='LOGIN', cmd='<a class=\"nav-link\" href=\"./signup\">SIGNUP</a>')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':

        sql = """
			SELECT *
			FROM company_info WHERE username='{}' AND password='{}'
			""".format(request.form['username'], request.form['password']) # request.form['username'] is from the name ='username' input tag in html

        results = db.engine.execute(text(sql))
  
        results = [dict(row) for row in results] # a list of dicts, where each dict is each row

        print(results)
        if len(results) >= 1:

            # create the session variables for username and type
            session['username'] = results[0]['username']
            session['logged_in'] = True

            return redirect('/index')

        # failling case
        return render_template('login.html', works=" Username/Password is incorrect")

    # when method = "GET"
    else:
        # when the already loggin redirect them back index homepage
        if ("logged_in" in session) and session["logged_in"]:
            return redirect('/index')

        return render_template("login.html")

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        company_name = request.form['company_name']
        address = request.form['address']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        postal_code = request.form['postal_code']
        
        # check if username already exist
        sql = """ 
			SELECT COUNT(*) AS 'count' FROM company_info WHERE username = '{}'
		""".format(username)

        results = db.engine.execute(sql)
        results = [dict(row) for row in results]

        #sql2 = """
        #SELECT COUNT(*) AS 'count2' FROM users WHERE IDnumber = '{}'
		#""".format(IDnumber)

        #results2 = db.engine.execute(sql2)
        #results2 = [dict(row) for row in results2] # [{count2:0}]
        # if username doesn't already exist and  if the IDnumber don't already exist in the data, then add it into the database
        #if results[0]['count'] == 0 and results2[0]['count2'] == 0:
        if results[0]['count'] == 0:
            
            sql = """
				INSERT INTO company_info (company_name, username, password, address, postal_code, latitude, longitude) VALUES ('{}', '{}', '{}', '{}' , '{}', '{}', '{}')
			""".format(company_name, username, password, address, postal_code, latitude, longitude)

            results = db.engine.execute(text(sql))
        else:
            return "Username already exists! Go back to sign up page and choose a different Username\n , OR this IDnumber already have an accounts"
            
        return redirect(url_for('login'))

    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():

    # pop everything from the user table
    session.pop('username', None)
    session.pop('password', None)
    session['logged_in'] = False

    return redirect(url_for('index'))

@app.route('/about')
def about():
    if "logged_in" in session and session['logged_in']:
        return render_template('about.html', username=session['username'], cmd='<a class=\"nav-link\" href=\"./logout\">LOGOUT</a>') 
    else:
        return render_template("about.html", username="LOGIN", cmd='<a class=\"nav-link\" href=\"./signup\">SIGNUP</a>')

def get_db():
    sql = """
        SELECT *
        FROM company_info
        """
    results = db.engine.execute(text(sql)).fetchall()
    return results


def get_cur_loc():
    myloc = geocoder.ip('me')
    print(myloc.latlng)
    cur_loc = myloc.latlng
    return cur_loc


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)