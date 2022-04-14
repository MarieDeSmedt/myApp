from flask import Flask, render_template, json, request, redirect, session, flash
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import os

mysql = MySQL()
app = Flask(__name__)
app.debug = True
app.secret_key = 'why would I tell you my secret key?'
# app.config.from_object('config')

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'marie'
app.config['MYSQL_DATABASE_PASSWORD'] = 'marikiki9283'
app.config['MYSQL_DATABASE_DB'] = 'MapApp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/api/signup', methods=['POST'])
def signUp():
    
        try:
            _name = request.form['inputName']
            _email = request.form['inputEmail']
            _password = request.form['inputPassword']

            # validate the received values
            if _name and _email and _password:

            # All Good, let's call MySQL

                conn = mysql.connect()
                cursor = conn.cursor()
                _hashed_password = generate_password_hash(_password)
                cursor.callproc('sp_createUser', (_name, _email, _hashed_password))
                data = cursor.fetchall()

                if len(data) == 0:
                    conn.commit()
                    flash('success')
                    return json.dumps({'message': 'User created successfully !'})
                else:
                    return json.dumps({'error': str(data[0])})
            else:
                return json.dumps({'html': '<span>Enter the required fields</span>'})
   
        except Exception as e:
            return json.dumps({'error': str(e)})
        finally:
            cursor.close()
            conn.close()

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')


@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userhome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/validateLogin',methods=['POST'])
def validateLogin():

    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
 
        # connect to mysql
 
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()
 
        if len(data) > 0:
           
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                # return redirect('/userHome')
                return redirect('/getSite')
            else:
               
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            
            return render_template('error.html',error = 'Wrong Email address or Password.')
 
 
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


@app.route('/showAddSite')
def showAddSite():
    return render_template('addSite.html')

@app.route('/addSite',methods=['POST'])
def addSite():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _longitude = request.form['inputLon']
            _latitude = request.form['inputLat']
            _siteSid = request.form['inputSiteSid']
            _user = session.get('user')
 
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addSite',(_title,_longitude,_latitude,_siteSid,_user))
            data = cursor.fetchall()
 
            if len(data) is 0:
                conn.commit()
                return redirect('/userhome')
            else:
                return render_template('error.html',error = 'An error occurred!')
 
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/getSite')
def getSite():
    try:
        if session.get('user'):
            _user = session.get('user')
 
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetSiteByUser',(_user,))
            sites = cursor.fetchall()
 
            site_dict = []

            # for site,i in sites:
            #     new = {
            #             'Id': site[0],
            #             'Title': site[1],
            #             'Longitude': site[2],
            #             'Latitude': site[3],
            #             'SiteSid': site[4],
            #             'Date': site[6]}
            #     site_dict[i]=new
 
            
            return render_template('error.html', error = json.dumps(sites))
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))




if __name__ == "__main__":
    
    app.run(debug=True)