from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField,DateField,DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from functools import wraps
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import pymysql
#import secrets
import os

dbuser=os.environ.get('DBUSER')
dbpass=os.environ.get('DBPASS')
dbhost=os.environ.get('DBHOST')
dbname=os.environ.get('DBNAME')
#conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser,dbpass,dbhost,dbname)
# Open database connection
#dbhost = secrets.dbhost
#dbuser = secrets.dbuser
#dbpass = secrets.dbpass
#dbname = secrets.dbname

#db = pymysql.connect(dbhost, dbuser, dbpass, dbname)

app = Flask(__name__)

login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'danger' # sets flash category for the default message 'Please log in to access this page.'


app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
db=_BaseSQLAlchemy(app)
#import os
# = os.environ.get('SECRET_KEY')


# Prevent --> pymysql.err.OperationalError) (2006, "MySQL server has gone away (BrokenPipeError(32, 'Broken pipe')
class SQLAlchemy(_BaseSQLAlchemy):
     def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(app, options)
        options["pool_pre_ping"] = True
# <-- MWC




# report database function
class jzhu72_project(db.Model):
    InstanceID = db.Column(db.Integer,primary_key=True)
    HawkID=db.Column(db.Integer)
    First_name=db.Column(db.String(255))
    Last_name=db.Column(db.String(255))
    TemperatureC=db.Column(db.DECIMAL(5,2))
    FeelingGood=db.Column(db.String(255))
    NeedHelp=db.Column(db.String(255))
    TodayClass=db.Column(db.String(255))
    ContactSickPeople=db.Column(db.String(255))
    ReportDate=db.Column(db.Date)

    def __repr__(self):
        return "InstanceID: {0} | HawkID: {1} | First_name: {2} | Last_name: {3} |TemperatureC : {4} | FeelingGood: {5} | NeedHelp: {6} | ContactSickPeople: {7} | ReportDate: {8}".format( self.InstanceID, self.HawkID, self.First_name, self.Last_name,self.TemperatureC ,self.FeelingGood,self.NeedHelp,self.TodayClass,self.ContactSickPeople,self.ReportDate)



class reportdb(FlaskForm):
    InstanceID=IntegerField('InstanceID :')
    HawkID=IntegerField('HawkID:',validators=[DataRequired()])
    First_name=StringField('First_name:',validators=[DataRequired()])
    Last_name=StringField('Last_name:',validators=[DataRequired()])
    TemperatureC=DecimalField('TemperatureC:',validators=[DataRequired()])
    FeelingGood=StringField('FeelingGood:',validators=[DataRequired()])
    NeedHelp=StringField('NeedHelp:',validators=[DataRequired()])
    TodayClass=StringField('TodayClass:',validators=[DataRequired()])
    ContactSickPeople=StringField('ContactSickPeople:',validators=[DataRequired()])
    ReportDate=DateField('ReportDate:',validators=[DataRequired()])


@app.route('/databaseoverview')
def databaseoverview():
    all_reports=jzhu72_project.query.all()
    return render_template('databaseoverview.html',reporttable=all_reports,pageTitle='University of Iowa Daily Report')


@app.route('/database')
def database():
    all_reports=jzhu72_project.query.all()
    return render_template('database.html',reporttable=all_reports,pageTitle='University of Iowa Daily Report')

@app.route('/reports/<int:InstanceID>',methods=['GET','POST'])
def get_report(InstanceID):
    reports=jzhu72_project.query.get_or_404(InstanceID)
    return render_template('databasedetail.html',form=reports,pageTitle="reports details", legend='report Details')

@app.route('/reports_user/<int:InstanceID>',methods=['GET','POST'])
def get_report_user(InstanceID):
    reports_user=jzhu72_project.query.get_or_404(InstanceID)
    return render_template('userdetail.html',form=reports_user,pageTitle="reports details", legend='report Details')





@app.route('/reports/<int:InstanceID>/update', methods=['POST'])
def update_report(InstanceID):
    reports = jzhu72_project.query.get_or_404(InstanceID)
    form = reportdb()

    if form.validate_on_submit():
        reports.HawkID=form.HawkID.data
        reports.First_name=form.First_name.data
        reports.Last_name=form.Last_name.data
        reports.TemperatureC=form.TemperatureC.data
        reports.FeelingGood=form.FeelingGood.data
        reports.NeedHelp=form.NeedHelp.data
        reports.TodayClass=form.TodayClass.data
        reports.ContactSickPeople=form.ContactSickPeople.data
        reports.ReportDate=form.ReportDate.data
        db.session.commit()
        return redirect(url_for('get_report',InstanceID=reports.InstanceID))

    form.InstanceID.data=reports.InstanceID
    form.HawkID.data=reports.HawkID
    form.First_name.data=reports.First_name
    form.Last_name.data=reports.Last_name
    form.TemperatureC.data=reports.TemperatureC
    form.FeelingGood.data=reports.FeelingGood
    form.NeedHelp.data=reports.NeedHelp
    form.TodayClass.data=reports.TodayClass
    form.ContactSickPeople.data=reports.ContactSickPeople
    form.ReportDate.data=reports.ReportDate


    return render_template('databaseupdate.html',form=form,pageTitle='Update report',legend='Updata a report')

@app.route('/search',methods=['GET','POST'])
def search():
        if request.method=="POST":
            form=request.form
            search_value=form['search_string']
            search="%{}%".format(search_value)
            results=jzhu72_project.query.filter(or_(jzhu72_project.First_name.like(search),
                                                          jzhu72_project.HawkID.like(search),
                                                          jzhu72_project.Last_name.like(search),
                                                          jzhu72_project.TemperatureC.like(search),
                                                          jzhu72_project.FeelingGood.like(search),
                                                          jzhu72_project.NeedHelp.like(search),
                                                          jzhu72_project.TodayClass.like(search),
                                                          jzhu72_project.ContactSickPeople.like(search),
                                                          jzhu72_project.ReportDate.like(search))).all()
            return render_template('database.html',reporttable=results,pageTitle="The University of Iowa Daily Report",legend="Search results")
        else:
            return redirect('/')



@app.route('/search_overview',methods=['GET','POST'])
def search_overview():
        if request.method=="POST":
            form=request.form
            search_value=form['search_string']
            search="%{}%".format(search_value)
            results=jzhu72_project.query.filter(or_(jzhu72_project.First_name.like(search),
                                                          jzhu72_project.HawkID.like(search),
                                                          jzhu72_project.Last_name.like(search),
                                                          jzhu72_project.TemperatureC.like(search),
                                                          jzhu72_project.FeelingGood.like(search),
                                                          jzhu72_project.NeedHelp.like(search),
                                                          jzhu72_project.TodayClass.like(search),
                                                          jzhu72_project.ContactSickPeople.like(search),
                                                          jzhu72_project.ReportDate.like(search))).all()
            return render_template('databaseoverview.html',reporttable=results,pageTitle="The University of Iowa Daily Report",legend="Search results")
        else:
            return redirect('/')


@app.route('/addreport',methods=['GET','POST'])
def addreport():
    form=reportdb()
    if form.validate_on_submit():
        report=jzhu72_project(HawkID=form.HawkID.data,First_name=form.First_name.data,Last_name=form.Last_name.data,TemperatureC=form.TemperatureC.data,
        FeelingGood=form.FeelingGood.data,NeedHelp=form.NeedHelp.data,TodayClass=form.TodayClass.data,ContactSickPeople=form.ContactSickPeople.data,ReportDate=form.ReportDate.data)
        db.session.add(report)
        db.session.commit()
        return redirect('/database')
    return render_template('addreport.html',form=form,pageTitle='add report')



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class NewUserForm(FlaskForm):
    name = StringField('Name: ', validators=[DataRequired()])
    username = StringField('Username: ', validators=[DataRequired()])
    email = StringField('Email: ', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    access = IntegerField('Access: ')
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class UserDetailForm(FlaskForm):
    id = IntegerField('Id: ')
    name = StringField('Name: ', validators=[DataRequired()])
    username = StringField('Username: ', validators=[DataRequired()])
    email = StringField('Email: ', validators=[DataRequired(), Email()])
    access = IntegerField('Access: ')

class AccountDetailForm(FlaskForm):
    id = IntegerField('Id: ')
    name = StringField('Name: ', validators=[DataRequired()])
    email = StringField('Email: ', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])


ACCESS = {
    'guest': 0,
    'user': 1,
    'admin': 2
}

class User(UserMixin, db.Model):
    __tablename__ = 'jzhu72_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    username = db.Column(db.String(30))
    password_hash = db.Column(db.String(128))
    access = db.Column(db.Integer)

    def __init__(self, name, email, username, access=ACCESS['guest']):
        self.id = ''
        self.name = name
        self.email = email
        self.username = username
        self.password_hash = ''
        self.access = access

    def is_admin(self):
        return self.access == ACCESS['admin']

    def is_user(self):
        return self.access == ACCESS['user']

    def allowed(self, access_level):
        return self.access >= access_level

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {0}>'.format(self.username)




@login.user_loader
def load_user(id):
    return User.query.get(int(id))  #if this changes to a string, remove int


### custom wrap to determine access level ###
def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated: #the user is not logged in
                return redirect(url_for('login'))

            #user = User.query.filter_by(id=current_user.id).first()

            if not current_user.allowed(access_level):
                flash('You do not have access to this resource.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator




#### Routes ####

# index
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', pageTitle='Home Page')

# about
@app.route('/about')
def about():
    return render_template('about.html', pageTitle='About page')

# registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',  pageTitle='Register | My Flask App', form=form)

# user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        flash('You are now logged in', 'success')
        return redirect(next_page)
    return render_template('login.html',  pageTitle='Login | My Flask App', form=form)


#logout
@app.route('/logout')
def logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('index'))


################ GUEST ACCESS FUNCTIONALITY OR GREATER ###################

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user = User.query.get_or_404(current_user.id)
    form = AccountDetailForm()

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.set_password(form.password.data)

        db.session.commit()
        flash('Your account has been updated.', 'success')
        return redirect(url_for('account'))

    form.name.data = user.name
    form.email.data = user.email

    return render_template('account_detail.html', form=form, pageTitle='Your Account')
@app.route('/welcome')
def welcome():
    return render_template('welcome.html', pageTitle='Welcome')



################ USER ACCESS FUNCTIONALITY OR GREATER ###################

# Contact_Information
@app.route('/Contact_Information')
def Contact_Information():
    return render_template('Contact_Information.html',pageTitle=' Contact Information')

################ ADMIN ACCESS FUNCTIONALITY ###################
@app.route('/delete_report/<int:InstanceID>',methods=['POST'])
@requires_access_level(ACCESS['admin'])
def delete_report(InstanceID):
    if request.method=='POST':
        report=jzhu72_project.query.get_or_404(InstanceID)
        db.session.delete(report)
        db.session.commit()
        flash('User has been deleted.', 'success')
        return redirect(url_for('database'))
    else:
        return redirect(url_for('database'))

# control panel

@app.route('/control_panel')
@requires_access_level(ACCESS['admin'])
def control_panel():
    all_users = User.query.all()
    return render_template('control_panel.html', users=all_users, pageTitle='Control Panel')

# user details & update
@app.route('/user_detail/<int:user_id>', methods=['GET','POST'])
@requires_access_level(ACCESS['admin'])
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    form = UserDetailForm()
    form.id.data = user.id
    form.name.data = user.name
    form.email.data = user.email
    form.username.data = user.username
    form.access.data = user.access
    return render_template('user_detail.html', form=form, pageTitle='User Details')

# update user
@app.route('/update_user/<int:user_id>', methods=['POST'])
@requires_access_level(ACCESS['admin'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserDetailForm()

    orig_user = user.username # get user details stored in the database - save username into a variable

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data

        new_user = form.username.data

        if new_user != orig_user: # if the form data is not the same as the original username
            valid_user = User.query.filter_by(username=new_user).first() # query the database for the usernam
            if valid_user is not None:
                flash("That username is already taken...", 'danger')
                return redirect(url_for('control_panel'))

        # if the values are the same, we can move on.
        user.username = form.username.data
        user.access = request.form['access_lvl']
        db.session.commit()
        flash('The user has been updated.', 'success')
        return redirect(url_for('control_panel'))

    return redirect(url_for('control_panel'))

# delete user
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@requires_access_level(ACCESS['admin'])
def delete_user(user_id):
    if request.method == 'POST': #if it's a POST request, delete the friend from the database
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted.', 'success')
        return redirect(url_for('control_panel'))

    return redirect(url_for('control_panel'))

# new user
@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    form = NewUserForm()

    if request.method == 'POST' and form.validate_on_submit():
        user = User(name=form.name.data, username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.access = request.form['access_lvl']
        db.session.add(user)
        db.session.commit()
        flash('User has been successfully created.', 'success')
        return redirect(url_for('login'))

    return render_template('new_user.html',  pageTitle='New User | My Flask App', form=form)




if __name__ == '__main__':
    app.run(debug=True)
