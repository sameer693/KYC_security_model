from collections import defaultdict
from flask import Flask, Response, jsonify, render_template, request, redirect, session, flash
from facefunc import gen_frames, gen_register
from face_rec import detect_and_display, init
from helper import login_required, apology
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import cv2
import pickle
app = Flask(__name__)

app.secret_key="secret key"

def get_db_connection():
    #conn = sqlite3.connect("database.db")
    conn = sqlite3.connect("DB.db")
    conn.row_factory = sqlite3.Row
    return conn

def gen_frames_live():
    #get name and face encoding from database
    conn = get_db_connection()
    cursor = conn.cursor()
    users = []
    try:
        cursor.execute("SELECT adhar,user_face_encoding FROM users")
        users = cursor.fetchall()
    except:
        pass
    known_face_encodings = []
    known_face_names = []
    for user in users:
        known_face_encodings.append(pickle.loads(user["user_face_encoding"]))
        known_face_names.append(user["adhar"])
    
    data={"encodings":known_face_encodings,"names":known_face_names}
    eyes_detected = defaultdict(str)
    (model, face_detector, open_eyes_detector,left_eye_detector,right_eye_detector, video_capture, images) = init()
    while True:
        #take user if true or false
        frame = detect_and_display(model, video_capture, face_detector, open_eyes_detector,left_eye_detector,right_eye_detector, data, eyes_detected)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
  

#npx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css --watch
@app.route('/', methods=['GET'])
def hello():
    return render_template('hello.html', name='World')

#login and register

@app.route('/video', methods=['GET'])
def video():
    return Response(gen_frames_live(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed',methods=['GET'])
def video_feed():

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve user from the database
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user["password"], password):
            session["username"] = username
            session["id"] = user["id"]
            flash("You are logged in", "success")
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        dob = request.form['dob']
        address = request.form['address']
        adhar = request.form['adhar']
        password = request.form['password']
        userimage = request.files['image']


        if not first_name:
            flash("First name is required", "danger")
            return redirect('/register')
        if not password:
            flash("Password is required", "danger")
            return redirect('/register')
        if not last_name:
            flash("Last name is required", "danger")
            return redirect('/register')
        if not dob:
            flash("Date of Birth is required", "danger")
            return redirect('/register')
        if not address:
            flash("Address is required", "danger")
            return redirect('/register')
        if not adhar:
            flash("Adhar is required", "danger")
            return redirect('/register')
        if not userimage:
            flash("Image is required", "danger")
            return redirect('/register')

        if len(adhar) != 12 or not adhar.isdigit():
            flash("Adhar should be of 12 digits", "danger")
            return redirect('/register')
        user_face_encoding = gen_register(userimage)
        user_face_encoding = pickle.dumps(user_face_encoding)
        password = generate_password_hash(password,salt_length=16,method='pbkdf2:sha256')
        print(user_face_encoding)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (first_name, last_name, dob, address, adhar, password, user_face_encoding) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (first_name, last_name, dob, address, adhar, password, user_face_encoding))
        conn.commit()
        conn.close()
        flash(f"You are registered as {first_name}{last_name}", "success")
        return redirect('/login')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return "You are logged out"

#after register take facial input

if __name__ == '__main__':

    app.run(debug=True,
            
            ) 