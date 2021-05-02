from flask import request,Flask,render_template,flash, redirect, url_for, session, logging
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from passlib.hash import sha256_crypt
from functools import wraps
import os
from dataProcessing import *
from Threads import *
from flask import send_file
import time
import shutil

app = Flask(__name__)
app.secret_key='secret123'

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Abcd@123'
app.config['MYSQL_DB'] = 'cc_proj'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Register Form Class
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        print(email)
        print(username)
        print(password)

        # Create cursor
        cur = mysql.connection.cursor()

        checkUsername = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if checkUsername > 0:
            cur.close()
            flash('Username Already in Use', 'danger')
            return redirect(url_for('register'))
        # Execute query
        cur.close()
        
        cur = mysql.connection.cursor()
        check_email = cur.execute("SELECT * FROM users WHERE email = %s", [email])
        if check_email > 0:
            cur.close()
            flash('Email Already in Use', 'danger')
            return redirect(url_for('register'))
        # Execute query
        cur.close()
        
        #user_folder generation
        directory = username
  
        # Path
        path = os.path.join(os.getcwd(), 'Storage/')
        path = os.path.join(path, username)
        
        # Create the directory
        os.mkdir(path)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(email, username, password) VALUES(%s, %s, %s)", (email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['email'] = data['email']

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    try:
        # os.remove("Original.txt")
        os.remove("Output.txt")
    except:
        pass
    cur = mysql.connection.cursor()

    # Get articles
    # result = cur.execute("SELECT * FROM articles")
    # Show articles only from the user logged in 
    result = cur.execute("SELECT * FROM files WHERE username = %s", [session['username']])

    files = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', files=files)
    else:
        msg = 'No Files Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()

# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])
    # txt_file = FileField(validators=[FileRequired()])

# File Form Class
class FileForm(FlaskForm):
    txt_file = FileField(validators=[FileRequired()])

from flask import request
from werkzeug.datastructures import CombinedMultiDict


# upload file
@app.route('/upload', methods=['GET', 'POST'])
@is_logged_in
def upload():
    form = FileForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST' and request.files:
        f = form.txt_file.data
        filename = secure_filename(f.filename)

        cur = mysql.connection.cursor()
        check_filename = cur.execute("SELECT * FROM files WHERE filename = %s and username = %s", (filename.split('.')[0],session['username']))
        if check_filename > 0:
            cur.close()
            flash('File Already Present', 'danger')
            return redirect(url_for('dashboard'))
        # Execute query
        cur.close()

        print(filename)
        path = os.path.join(os.getcwd(), 'Storage')
        path = os.path.join(path, session['username'])
        path = os.path.join(path, filename.split('.')[0] )
        print(path)
        # Create the directory
        os.mkdir(path)
        
        f.save(os.path.join(path, filename))
        start(path,filename)
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO files(username, filename) VALUES(%s, %s)",(session['username'],filename.split('.')[0]))

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()
        os.remove(os.path.join(path, filename))

        return redirect(url_for('dashboard'))

    return render_template('upload.html', form=form)

@app.route('/delete_file/<string:id>',methods=['POST'])
@is_logged_in
def delete_file(id):
    cur = mysql.connection.cursor()
    id = [id]
    # Execute
    cur.execute("Select * FROM files WHERE id = %s", id)
    data = cur.fetchone()
    filename =data['filename']
    cur.close()

    shutil.rmtree(os.path.join(os.getcwd(),'Storage',session['username'],filename))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM files WHERE id = %s", id)
    mysql.connection.commit()
    cur.close()

    flash('File->'+filename +' deleted', 'success')

    return redirect(url_for('dashboard'))
#key Form
class KeyForm(Form):
    key = StringField('Enter File decryption key', [validators.Length(min=1, max=200)])

@app.route('/decrypt_file/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def decrypt_file(id):
    form = KeyForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            key = form.key.data
            cur = mysql.connection.cursor()
            id = [id]
            # Execute
            cur.execute("Select * FROM files WHERE id = %s", id)
            data = cur.fetchone()
            filename =data['filename']
            cur.close()
            path = os.path.join(os.getcwd(),'Storage',session['username'],filename)
            os.mkdir(path+'/temp')
            os.mkdir(path+'/temp/Segments')
            os.mkdir(path+'/temp/Infos')
            DecryptMessage(key,path,filename)
            
            return_files_data(filename)
            shutil.rmtree(path+'/temp')
            flash('File Decrypted', 'success')
            return send_file('./Output.txt',attachment_filename=filename+'.txt',as_attachment=True)
        except Exception as e:
            if str(os.path.exists(path+'/temp')):
                shutil.rmtree(path+'/temp')
            flash('Error->wrong Key'+ str(e), 'danger')
            return redirect(url_for('dashboard'))

    return render_template('decrypt_file.html', form=form)

# Decrypt Function Calls

def DecryptMessage(key,path,filename):
    st=time.time()
    HybridDeCrypt(key,path,filename)
    et=time.time()
    print(et-st)
    trim(path)
    st=time.time()
    Merge(path)
    et=time.time()
    print(et-st)

@app.route('/return-files-data/<string:filename>')
def return_files_data(filename):
    try:
        return send_file('./Output.txt',attachment_filename=filename,as_attachment=True)
    except Exception as e:
        return str(e)

# Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM articles WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))


# ENcryption Decryption call functions
import smtplib

def start(path,filename):
    content = open(os.path.join(path, filename),'r')
    content.seek(0)
    first_char = content.read(1) 
    if not first_char:
        flash('Empty File', 'danger')
        return render_template('upload')
    else:
        EncryptInput(path,filename)


def EncryptInput(path,filename):
    Segment(path,filename)
    gatherInfo(path)
    key = HybridCrypt(path)

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM users WHERE username = %s", [session['username']])

    data = cur.fetchone()
    print(data)

    sender = 'secure.storage.cloud.project@gmail.com'
    receiver = data['email']
    SUBJECT = "Key for file - " + filename
    TEXT = "Do not share this key \n key -" + str(key)
    message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
    username = sender
    password = 'secure677071'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(sender, receiver, message)
    server.quit()










if __name__ == '__main__':
    #app.secret_key='secret123'
    app.config['SESSION_TYPE'] = 'filesystem'	
    app.run(debug=True)