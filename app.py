from flask import Flask
from flask import render_template,redirect,request,flash,url_for,request
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,IntegerField,DateField,DecimalField
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
import secrets
import os



#dbuser=os.environ.get('DBUSER')
#dbpass=os.environ.get('DBPASS')
#dbhost=os.environ.get('DBHOST')
#dbname=os.environ.get('DBNAME')
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)
#conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser,dbpass,dbhost,dbname)
# Open database connection
dbhost = secrets.dbhost
dbuser = secrets.dbuser
dbpass = secrets.dbpass
dbname = secrets.dbname


db = pymysql.connect(dbhost, dbuser, dbpass, dbname)

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



app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
db = SQLAlchemy(app)





class jzhu72(db.Model):
    HawkID = db.Column(db.Integer)
    member_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    Temperature  = db.Column(db.DECIMAL(5,2))
    FeelingGood = db.Column(db.String(255))
    ReportDate = db.Column(db.Date)
    NeedHelp = db.Column(db.String(255))
    ContactSickPeople = db.Column(db.String(255))

    def __repr__(self):
        return "HawkID: {0} | id: {1} | first name: {2} | last name: {3} |Temperature : {4} | FeelingGood: {5} | ReportDate: {6} | NeedHelp: {7} | ContactSickPeople: {8}".format( self.HawkID, self.member_id, self.first_name, self.last_name,self.Temperature ,self.FeelingGood,self.ReportDate,self.NeedHelp,self.ContactSickPeople)


class MemberForm(FlaskForm):
    HawkID = IntegerField('HawkID:',validators=[DataRequired()])
    member_id = IntegerField('Member ID')
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    Temperature  = DecimalField('Temperature :',validators=[DataRequired()],)
    FeelingGood = StringField('FeelingGood:', validators=[DataRequired()])
    ReportDate = DateField('ReportDate:', validators=[DataRequired()])
    NeedHelp = StringField('NeedHelp:', validators=[DataRequired()])
    ContactSickPeople = StringField('ContactSickPeople:', validators=[DataRequired()])




@app.route('/')
def index():
    all_members = jzhu72.query.all()
    return render_template('index.html', members=all_members,pageTitle='lakers team member')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        form = request.form
        search_value = form['search_string']
        search = "%{0}%".format(search_value)
        results = jzhu72.query.filter(or_(jzhu72.HawkID.like(search),jzhu72.first_name.like(search),jzhu72.last_name.like(search),jzhu72.Temperature .like(search),jzhu72.FeelingGood.like(search),jzhu72.ReportDate.like(search),jzhu72.NeedHelp.like(search),jzhu72.ContactSickPeople.like(search))).all()
        return render_template('index.html', members=results, pageTitle='lakers team member', legend="Search Results")
    else:
        return redirect('/')








@app.route('/add_member', methods=['GET','POST'])
def add_member():
    form = MemberForm()
    if form.validate_on_submit():
        member = jzhu72(HawkID=form.HawkID.data,first_name=form.first_name.data, last_name=form.last_name.data, Temperature =form.Temperature .data, FeelingGood=form.FeelingGood.data, ReportDate=form.ReportDate.data,NeedHelp=form.NeedHelp.data ,ContactSickPeople=form.ContactSickPeople.data)
        db.session.add(member)
        db.session.commit()
        return redirect('/')
    return render_template('add_member.html', form=form, pageTitle='Add A New Member')

@app.route('/delete_member/<int:member_id>', methods=['GET', 'POST'])
def delete_member(member_id):
    if request.method == 'POST':
        member = jzhu72.query.get_or_404(member_id)
        db.session.delete(member)
        db.session.commit()
        return redirect("/")
    else:
        return redirect("/")

@app.route('/member/<int:member_id>', methods=['GET','POST'])
def get_member(member_id):
    member = jzhu72.query.get_or_404(member_id)
    return render_template('member.html', form=member, pageTitle='Member Details', legend="Member Details")

@app.route('/member/<int:member_id>/update', methods=['GET','POST'])
def update_member(member_id):
    member = jzhu72.query.get_or_404(member_id)
    form = MemberForm()

    if form.validate_on_submit():
        member.HawkID = form.HawkID.data
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.Temperature =form.Temperature .data
        member.FeelingGood=form.FeelingGood.data
        member.ReportDate=form.ReportDate.data
        member.NeedHelp=form.NeedHelp.data
        member.ContactSickPeople=form.ContactSickPeople.data
        db.session.commit()
        return redirect(url_for('get_member', member_id=member.member_id))

    form.HawkID.data = member.HawkID
    form.member_id.data = member.member_id
    form.first_name.data = member.first_name
    form.last_name.data = member.last_name
    form.Temperature .data = member.Temperature
    form.FeelingGood.data = member.FeelingGood
    form.ReportDate.data=member.ReportDate
    form.NeedHelp.data = member.NeedHelp
    form.ContactSickPeople.data=member.ContactSickPeople

    return render_template('update_member.html', form=form, pageTitle='Update Member', legend="Update A Member")


if __name__ == '__main__':
    app.run(debug=True)
