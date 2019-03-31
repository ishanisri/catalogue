from flask import render_template,redirect, request, flash,g,session,url_for,Flask
import os
import sqlite3 as sql
from werkzeug import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import send_from_directory
import requests
import simplejson as json
from flask_socketio import SocketIO, emit

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.secret_key="why would i tell my secret key?"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)






@app.route("/")
def main():
    return render_template('index.html')
@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html') 
@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html') 
@app.route('/addContents')
def showAdd():
    return render_template('addContents.html') 




@app.route('/signUp',methods=['GET','POST'])
def signedUp():
    if(request.method=='POST'):

        username= request.form.get('inputName')
        rollno = request.form.get('inputRoll')
        password=request.form.get('inputPassword')
        
        print(username+" "+rollno+" "+password)
        hashed_password = generate_password_hash(password)
        print(hashed_password)
        

        print("hi")	
        
        with sql.connect("luggage.db") as con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS account_holder(rollno TEXT  NOT NULL PRIMARY KEY,username TEXT DEFAULT NULL,password TEXT DEFAULT NULL)")
            cur.execute("SELECT * FROM account_holder where rollno=?",(rollno,))
            data=cur.fetchall()
            if(data):
            	return render_template('error.html',error="User exists already")

            else: 	
	            cur.execute("INSERT INTO account_holder (rollno,username,password) VALUES (?,?,?)", (rollno,username,hashed_password))
	            cur.execute("CREATE TABLE IF NOT EXISTS luggage_list(roll INTEGER DEFAULT NULL,luggage_name TEXT DEFAULT NULL,contents TEXT DEFAULT NULL,image BLOB,striked TEXT DEFAULT OFF)")
	            cur.execute("SELECT * FROM account_holder where rollno=?",(rollno,))
	            data=cur.fetchall()
	            print(data)
	            con.commit()

                                                                                         
        session['user']=rollno
        print(session.get('user'))
        cur.close()
        con.close()   
    return redirect('/userHome') 


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


@app.route('/validateLogin',methods=['GET','POST'])
def validateLogin():
    if(request.method=='POST'):
        con = sql.connect("luggage.db")
        cur=con.cursor()
        
        try:
            
            rollno = request.form['inputRoll']
            password = request.form['inputPassword']
            cur.execute("SELECT * FROM account_holder where rollno=?",(rollno,))
            print("hi")
            data = cur.fetchall()
            print(data)
            if len(data) > 0:

                if check_password_hash(str(data[0][2]),password):
                    print("inside check")
                    session['user'] = data[0][0]
                    
                else:
                    return render_template('error.html',error = 'Wrong Roll No or Password.')
            else:
                return render_template('error.html',error = 'Wrong Roll No or Password!!!!')                  

     
        except Exception as e:
            return render_template('error.html',error = str(e))
        finally:
            cur.close()
            con.close()
    return redirect('/userHome')





@app.route('/addLuggage',methods=['GET','POST'])
def addLuggage():
    if(request.method=='POST'):
        con = sql.connect("luggage.db")
        cur=con.cursor()
       # print(session.get('user'))
        try:
            if(session.get('user')):
                _luggage_name=request.form['inputName']
                
                _description=request.form['inputDescription']
                
                print("works before image")
                # check if the post request has the file part
                if 'file' not in request.files:
                  flash('No file part')
                  return redirect(request.url)
                file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
                if file.filename == '':
                  flash('No selected file')
                  return redirect(request.url)
                if file and allowed_file(file.filename):
                  filename = secure_filename(file.filename)
                  print(filename)
                  file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                  _image=os.path.join(app.config['UPLOAD_FOLDER'], filename)
                  print(_image)
                  print(uploaded_file(filename))
                print("hello")
                print(session.get('user'))
                cur.execute("INSERT INTO luggage_list VALUES(?,?,?,?,?)",(session.get('user'),_luggage_name,_description,_image,'OFF'))
                cur.execute("SELECT * FROM luggage_list where roll=?",(session.get('user'),))
                data=cur.fetchall()
                print(data)
                con.commit()
        except Exception as e:
            return render_template('error.html',error = str(e))
        finally:
            cur.close()
            con.close()
    return redirect('/userHome')   



@app.route('/strike')
def strike():
    data_dict=[]
    
        
    con = sql.connect("luggage.db")
    cur=con.cursor()
        
    try:
            if(session.get('user')):
                roll=session.get('user')
                print(roll)
                cur.execute("SELECT * FROM luggage_list WHERE roll=?",(roll,))
                data=cur.fetchall()
                print(data)
                j=0
                i=0
                for row in data:
                        i=i+1
                        j=i
                        row_dict={
                         'Name':row[1],
                         'Contents':row[2],
                         'Image':row[3],
                         'i':i,
                         'Strike':row[4]

                        }
                        
                        data_dict.append(row_dict)
                
                print(data_dict)
            else:
                 return render_template('error.html',error = "User not found") 
    except Exception as e:
            return render_template('error.html',error = str(e))
    finally:
            cur.close()
            con.close()
            
    return render_template('strike.html',data_dict=data_dict,j=j)    


@app.route('/dostrike',methods=['POST','GET'])
def striketime():
  if(request.method=='POST'):
    con = sql.connect("luggage.db")
    cur=con.cursor()
    _roll=session.get('user')
    r=request.json
    retrieved=json.dumps(r)
    print(r)
    cur.execute("UPDATE luggage_list SET STRIKED='OFF' WHERE roll=?",(_roll,))
    if(r is not None):
        for i in range(len(r)):
          cur.execute("SELECT * FROM luggage_list WHERE roll=? and luggage_name=?",(_roll,r[i]))
          data=cur.fetchall()    
          print(data)

          cur.execute("UPDATE luggage_list SET STRIKED='ON' WHERE roll=? and luggage_name=?",(_roll,r[i]))

    con.commit()
    cur.close()
          
  return redirect('/userHome')    



@app.route('/userHome',methods=['GET','POST'])
def userHome():
    data_dict=[]
    data1=[]
        
    con = sql.connect("luggage.db")
    cur=con.cursor()
    

    try:
            if(session.get('user')):
                roll=session.get('user')
                print(roll)
                cur.execute("SELECT rollno from account_holder where rollno!=?",(roll,))
                datauser=cur.fetchall()
                print(datauser)
                for row in datauser:
                        
                        row_dict={
                         'User':row[0]

                        }
                        
                        data1.append(row_dict)
                
                cur.execute("SELECT * FROM luggage_list WHERE roll=?",(roll,))
                data=cur.fetchall()
                print(data)
                j=0
                i=0
                for row in data:
                        i=i+1
                        j=i
                        row_dict={
                         'Name':row[1],
                         'Contents':row[2],
                         'Image':row[3],
                         'i':i,
                         'Strike':row[4]

                        }
                        
                        data_dict.append(row_dict)
                
                print(data_dict)
            else:
                 return render_template('error.html',error = "User not found") 
    except Exception as e:
            return render_template('error.html',error = str(e))
    finally:
            cur.close()
            con.close()
    return render_template('userHome.html',data_dict=data_dict,j=j,user=session.get('user'),data1=data1)    




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@socketio.on('my event')
def test_message(message):
    print(message['data'])
    roll=message['data']
    user=session.get('user')
    con = sql.connect("luggage.db")
    cur=con.cursor()
    cur.execute("SELECT * FROM luggage_list WHERE roll=?",(user,))
    data=cur.fetchall()
    print(data)
    j=0
    i=0
    for row in data:
                        i=i+1
                        
    
    
    emit('my response', {'data':i,'sendto':str(roll),'whosent':str(user)},broadcast=True)
    


@app.route('/preview/<filename>')
def uploaded_file(filename):

    return '''<html><body><img src=filename></body></html>'''


if __name__ == "__main__":
     #app.run(debug=True)
     print("start")
     socketio.run(app)  
