import json
import string
import os
import random
import tempfile
import shutil

from scripts.send_email import email
from scripts.mongo import db

from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory

from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
#from flask.ext.cache import Cache

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename

from bson.objectid import ObjectId

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/images')

app.config["SECRET_KEY"] = ''
#app.config["CACHE_TYPE"] = "none"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
#Cache().init_app(app)
bootstrap = Bootstrap(app)

##############################################
##############################################
#######USER CLASS FOR LOGGING IN AND OUT
##############################################
##############################################
class User(UserMixin):
  def __init__(self, email, password, id, active=True):
    self.email = email
    self.password = password
    self.id = id
    self.active = active

  def is_active(self):
    account = db.accounts.find_one({ "email": self.email})
    if account is not None:
      if self.email != account['email'] or check_password(account['account']['password'], self.password) == False:
        self.active = False
    else:
      self.active = False
    return self.active

  def is_anonymous(self):
    return False

  def is_authenticated(self):
    return True

  def get_id(self):
    return str(db.accounts.find_one({'email': self.email})['_id'])

##############################################
##############################################
#######METHODS DEALING WITH LOGGING IN AND OUT
##############################################
##############################################
@login_manager.user_loader
def load_user(userid):
  user_rec = db.accounts.find_one({'_id': ObjectId(userid)})
  user = User(user_rec['email'] ,user_rec['account']['password'], user_rec['_id'])
  return user

@app.route('/logout', methods=["GET"])
@login_required
def logout():
  current_user.active = False
  logout_user()
  return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
  account = ''
  db_email = ''
  db_password = ''
  email_validated = ''
  if request.method == 'POST':
    post_email = request.form.get('email', '')
    post_password = request.form.get('password', '')
    try:
      account = db.accounts.find_one({"email": post_email})
      db_password = account['account']['password']
      db_email = account['email']
      email_validated = account['email_validated']
    except:
      pass
    if db_email != post_email or check_password(db_password, post_password) == False or email_validated == False:
      if email_validated == False:
        flash('Please check you email and validate your account')
        return render_template('login.html', email_validated=email_validated, email=db_email)
      else:
        flash('Invalid Credentials, Please Try Again')
        return render_template('login.html', email_validated=email_validated, email=db_email)
    else:
      user = User(post_email, post_password, account['_id'])
      login_user(user)
      return redirect(url_for('home'))
  return render_template('login.html', email_validated=email_validated, email=db_email)
  

@app.route('/check_email', methods=['POST'])
def check_email():
  db_email = db.accounts.find_one({'email': request.form['email']})
  if db_email is None:
    return json.dumps(True)
  else:
    return json.dumps(False)

def set_password(password):
  pw_hash = generate_password_hash(password)
  return pw_hash

def check_password(dbpassword, password):
  return check_password_hash(dbpassword, password)

##############################################
##############################################
#######CREATE ACCOUNT METHODS
##############################################
##############################################
@app.route('/create_account', methods=['POST', 'GET'])
def create_account():
  if request.method == 'POST':
    new_account = {}
    post_email = request.form['email'].strip()
    post_username = request.form['username'].strip()
    post_cellphone = request.form['phonenumber'].strip()
    post_password = request.form['password'].strip()
    post_provider = request.form['provider'].strip()

    db_email = db.accounts.find_one({'email': post_email})
    if db_email is not None:
      flash('The Email Already Exist')
      return redirect(url_for('login'))

    db_phonegroup = db.providers.find_one({})

    if str(post_provider) in db_phonegroup['providers'].keys():
      try:
        cellphone_email =  str(post_cellphone) + str(db_phonegroup['providers'][post_provider])
      except:
        cellphone_email = None
        pass

    new_account = {
      #'email': post_email,
      'username': post_username,
      'password': set_password(post_password),
      'cellphone': post_cellphone,
      'cellphone_email': cellphone_email,
    }
    token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))
    db.accounts.update({'email': post_email}, {'email': post_email, 'account': new_account, 'new_user': True, 'email_validated': False, 'token': token}, upsert=True)
    email.send_raw('reticentroot@gmail.com', 'reticentroot@gmail.com', 'Fast MMS Account Created', "username: {0} \n user email: {1}".format(post_username, post_email))
    email.send_raw(post_email, post_email, 'Validate Fast MMS Account', 'Your Validation Token Is: {0}'.format(token))
    flash('Account Created Please Check Your Email To Validate Your Account')
  return redirect(url_for('login'))

@app.route('/confirm', methods=['POST'])
def confirm():
  token = request.form.get('token', '').strip()
  post_email = request.form.get('validation_email', '')
  if post_email != '' or token != '':
    account = db.accounts.find_one({'email': post_email})
    if account:
      if account['token'] == token:
        db.accounts.update({'email': post_email}, {'$set': {'email_validated': True}})
        flash('Account Validated, Please Log In')
        return redirect(url_for('login'))
  return redirect(url_for('login'))

##############################################
##############################################
#######MAIN ROUTE
##############################################
##############################################
@app.route('/', methods=['GET'])
@login_required
def home():
  user_obj = None
  try:
    user_obj = db.accounts.find_one({'email':current_user.email})
    del user_obj['_id']
    del user_obj['account']['password']
  except:
    pass
  return render_template('index.html', account=user_obj)

##############################################
##############################################
#######FAQ
##############################################
##############################################
@app.route('/faq', methods=['GET'])
@login_required
def faq():
  return render_template('faq.html')

##############################################
##############################################
#######FEEDBACK
##############################################
##############################################
@app.route('/feedback', methods=['GET'])
@login_required
def feedback():
  return render_template('feedback.html')

@app.route('/send_feedback', methods=['POST'])
@login_required
def send_feedback():
  sender = request.form.get('email', '')
  feedback = request.form.get('feedback_msg', '')
  email.send_raw(sender, 'reticentroot@gmail.com', 'Fast MMS Feedback', feedback)
  return redirect(url_for('home'))

##############################################
##############################################
#######ACCOUNT INFORMATION
##############################################
##############################################
@app.route('/account_information',  methods=['GET'])
@login_required
def setting_information():
  user_obj = None
  try:
    user_obj = db.accounts.find_one({'email':current_user.email})
    del user_obj['_id']
    del user_obj['account']['password']
  except Exception:
    pass
  return render_template('account_information.html', account=user_obj)

@app.route('/update_information',  methods=['POST'])
@login_required
def update_setting_information():
  try:
    db_phonegroup = db.providers.find_one({})
    username = request.form['username']
    cellphone = request.form['cellphone']
    provider = request.form['provider']
    cellphone_email =  str(cellphone) + str(db_phonegroup['providers'][provider])
    db.accounts.update({'email':current_user.email}, {'$set' : {'account.username': username, 'account.cellphone': cellphone, 'account.cellphone_email': cellphone_email}})
  except Exception:
    pass
  return redirect(url_for('home'))

##############################################
##############################################
#######NEW USER POST
##############################################
##############################################
@app.route('/new_user', methods=['POST'])
@login_required
def new_user():
   db.accounts.update({'email':current_user.email}, {'$set': {'new_user' : False}})
   return redirect(url_for('home')) 

##############################################
##############################################
#######VALID PHONE NUMBER
##############################################
##############################################
@app.route('/validate_numbers', methods=['POST'])
@login_required
def valid_numbers():
  phonenumbers = json.loads(request.form['phonenumbers'])  # phonenumber is the key, provider the value
  print phonenumbers, 'here'
  group_name = request.form['group_name']
  print group_name, 'here2'
  names = json.loads(request.form['names'])
  print names, 'here3'
  db_phonegroup = db.providers.find_one({})
  
  
  
  emailmap = {}
  for phonenumber, provider in phonenumbers.iteritems():
    if str(provider) in db_phonegroup['providers'].keys():
      try:
        emailmap[phonenumber] =  {
          'email': str(phonenumber) + str(db_phonegroup['providers'][provider]),
          'name' : names[phonenumber]
          }
      except:
        pass

  db.accounts.update({'email':current_user.email}, {'$set' : {'groups.{0}'.format(group_name): emailmap}} , upsert=True)

  return redirect(url_for('home'))

##############################################
##############################################
#######EDIT GROUP
##############################################
##############################################
@app.route('/edit_group', methods=['POST'])
@login_required
def edit_group():
  phonenumbers = json.loads(request.form['phonenumbers'])  # phonenumber is the key, provider the value
  old_group_name = request.form['old_group_name']
  current_group_name = request.form['group_name']
  names = json.loads(request.form['names'])
  db_phonegroup = db.providers.find_one({})

  emailmap = {}
  for phonenumber, provider in phonenumbers.iteritems():
    if str(provider) in db_phonegroup['providers'].keys():
      try:
        emailmap[phonenumber] =  {
          'email': str(phonenumber) + str(db_phonegroup['providers'][provider]),
          'name' : names[phonenumber]
          }
      except:
        pass

  db_account = db.accounts.find_one({'email':current_user.email})
  if old_group_name != current_group_name:
    db_account['groups'][current_group_name] = db_account['groups'].pop(old_group_name)
    
  db_account['groups'][current_group_name] = emailmap

  db.accounts.update({'email':current_user.email}, db_account)
  return redirect(url_for('home'))

##############################################
##############################################
#######SAVE GROUP CHANGES
##############################################
##############################################
@app.route('/remove_group', methods=['POST'])
@login_required
def remove_group():
  db_account = db.accounts.find_one({'email':current_user.email})
  group_name = request.form['group_name']
  # removed values
  right_vals = json.loads(request.form['right_vals'])
  if right_vals != []:
    for right in right_vals:
      db_account['groups'][group_name].pop(right)
    db_account = db.accounts.update({'email':current_user.email}, {'$set' : {'groups.{0}'.format(group_name) : db_account['groups'][group_name]}})

  return redirect(url_for('home'))

##############################################
##############################################
#######FORGOT PASSWORD
##############################################
##############################################
@app.route('/forget_password', methods=['POST'])
def forgot_password():
  post_email = request.form['email']
  db_account = db.accounts.find_one({'email':post_email})
  if db_account:
    temp_pass = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
    email.send_raw(str(db_account['email']), str(db_account['email']), 'Mass Message Password Request', "Temporary Password: " + temp_pass)
    db.accounts.update({'email':post_email}, {'$set' : {'account.password': set_password(temp_pass)}})
    flash('Email with your temporary password has been sent')
  else:
    flash('The Email Address You\'ve Entered Does Not Exist')
  return redirect(url_for('login'))
  
##############################################
##############################################
#######FILE UPLOAD
##############################################
#############################################
# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
  return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
  file = request.files.get('file', None)
  message = request.form.get('sms_data', '')
  group_name = request.form.get('group_name', '')

  db_account = db.accounts.find_one({'email':current_user.email})
  numbers = db_account['groups'][group_name]
  for number, value in numbers.iteritems():
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      directory_name = tempfile.mkdtemp()
      file.save(os.path.join(directory_name, filename))
      #email.send_attach(db_account['account']['cellphone_email'], value['email'], '', message, os.path.join(directory_name, filename))
      email.send_attach(current_user.email, value['email'], '', message, os.path.join(directory_name, filename))
      shutil.rmtree(directory_name)
      # return redirect(url_for('home', filename=filename))
    else:
      if not file and message != '':
        email.send_raw(current_user.email, value['email'], '', message)
        #email.send_raw('tyrthor115@gmail.com', value['email'], '', message)
  return redirect(url_for('home'))

##############################################
##############################################
#######ERROR HANDLING METHODS
##############################################
##############################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_not_found(e):
    return render_template('500.html'), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('413.html'), 413

if __name__ == '__main__':
  app.run(debug=True, threaded=True)
