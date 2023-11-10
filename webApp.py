
from PIL import Image

import os

from flask_mysqldb import MySQL

from ultralytics import YOLO

from flask import Flask,render_template,request,redirect,send_from_directory,url_for,session

from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'e2974501361b28'
app.config['MAIL_PASSWORD'] = '8bd47ab35020dd'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "flaskdb"
mysql = MySQL(app)

@app.route("/home", methods=['GET', 'POST'])
def hello():
    if 'username' in session:
        return render_template("index.html", username = session['username'])
    
    if request.method == "POST":
        username = request.form('name')
        email = request.form('email')
        phone = request.form('phone')
        msg = request.form('message')

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO feedback (username,email,phone,msg) VALUES (%s,%s,%s,%s)",(username,email,phone,msg))

        mysql.connection.commit()

        cur.close()

@app.route("/about")
def aboutUS():
    return render_template("aboutUs.html")

@app.route("/")
def log():
    return render_template("login.html")

@app.route("/login", methods = ['POST'])
def log_submit():
    username = request.form['username']
    session['username'] = username
    return redirect(url_for('hello'))

@app.route('/updated')
def didit():
    return render_template('municipal_inform.html')

@app.route('/get_location', methods=['POST'])
def get_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    session['latitude'] = latitude
    session['longitude'] = longitude

    # Do something with the received latitude and longitude values
    print(f"Received Latitude: {latitude}, Longitude: {longitude}")

    return redirect(url_for('update_location'))

@app.route('/update_location', methods = ['POST'])
def update_location():
    print(request.form)
    if request.method == "POST":     
        namer = request.form['usern']
        caller = request.form['phonen']
        mailer = request.form['maili']
        if 'latitude' in session and 'longitude' in session:
            latitude = session['latitude']
            longitude = session['longitude']

        msg = Message('Urgent', sender = mailer, recipients = ['highauthoritycorporation@gmail.com'])

        msg.body = f'Pothole Co-ordinates : Latitude - {latitude}, Longitude - {longitude}.\n Name : {namer}, phone : {caller}'

        mail.send(msg)

        return "Mail sent successfully <a href='/home'>Home</a>"

@app.route("/detect", methods = ['GET', 'POST'])
def predict_img():
    if request.method == "POST":
        f = request.files['file']
        if f:  
            basepath = os.path.dirname(__file__)
            filepath = os.path.join(basepath,'uploads',f.filename)
            print("upload folder is: ", filepath)
            f.save(filepath)

            

            image = Image.open(filepath)

            #Detection Starts here
            yolo = YOLO("last.pt")
            results = yolo.predict(image,save=True,show = True)

            for r in results:
                print(len(r.boxes.conf))
                num = len((r.boxes.conf))

            print(f"The number of potholes are: {num}")


            if num == 0:
                 return "No Pothole Detected. Click <a href='/home'>here</a> to go back to home page"
            else:
                return display(f.filename)
           

    folder_path = "runs\detect"

    #To get the list of files present in detect folder
    file_list = [ file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
    print(file_list)

    #To arrange the list of files in detect folder based on the time of creation
    file_list.sort(key = lambda x: os.path.getctime(os.path.join(folder_path, x)), reverse = True)
    print(file_list)

    #Obviously the first file in the list will be the latest file created
    latest_file = file_list[0]
    print(latest_file)

    #To get the path of the latest file created
    latest_file_path = os.path.join(folder_path,latest_file)
    print(latest_file_path)

    #To get the jpg files present in the latest file fetched from detect folder
    jpg_files = [os.path.join(latest_file_path, entry) for entry in os.listdir(latest_file_path) if entry.lower().endswith(".jpg")]
    jpg_file_path = jpg_files[0]
    print(jpg_file_path)
            
    return render_template('detect.html')

@app.route('/<path:filename>')
def display(filename):
    folder_path = "runs\detect"

    #To get the list of files present in detect folder
    file_list = [ file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
    print(file_list)

    #To arrange the list of files in detect folder based on the time of creation
    file_list.sort(key = lambda x: os.path.getctime(os.path.join(folder_path, x)), reverse = True)
    print(file_list)

    #Obviously the first file in the list will be the latest file created
    latest_file = file_list[0]
    print(latest_file)

    #To get the path of the latest file created
    latest_file_path = os.path.join(folder_path,latest_file)
    print(latest_file_path)

    #To get the jpg files present in the latest file fetched from detect folder
    jpg_files = [os.path.join(latest_file_path, entry) for entry in os.listdir(latest_file_path) if entry.lower().endswith(".jpg")]
    filer = os.listdir(latest_file_path)
    the_file = filer[0]
    filename = jpg_files[0]
    print(filename)

    file_ext = filename.split(".")


    if file_ext[-1] == "jpg":
        return send_from_directory(latest_file_path,the_file)


app.run(debug=True)