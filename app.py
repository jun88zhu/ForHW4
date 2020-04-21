from flask import Flask
from flask import render_template,redirect,request,flash,url_for
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import pymysql
import secrets


conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)

app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
db = SQLAlchemy(app)

class jzhu72(db.Model):
    member_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    uniform_number = db.Column(db.Integer)
    homecountry = db.Column(db.String(255))

    def __repr__(self):
        return "id: {0} | first name: {1} | last name: {2} |uniform_number: {3} | homecountry: {4}".format(self.member_id, self.first_name, self.last_name,self.uniform_number,self.homecountry)


class MemberForm(FlaskForm):
    member_id = IntegerField('Friend ID')
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    uniform_number = StringField('Uniform Number:', validators=[DataRequired()])
    homecountry = StringField('Homecountry:', validators=[DataRequired()])


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
        results = jzhu72.query.filter(or_(jzhu72.first_name.like(search),jzhu72.last_name.like(search),jzhu72.uniform_number.like(search),jzhu72.homecountry.like(search))).all()
        return render_template('index.html', members=results, pageTitle='lakers team member', legend="Search Results")
    else:
        return redirect('/')








@app.route('/add_member', methods=['GET','POST'])
def add_member():
    form = MemberForm()
    if form.validate_on_submit():
        member = jzhu72(first_name=form.first_name.data, last_name=form.last_name.data, uniform_number=form.uniform_number.data, homecountry=form.homecountry.data)
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
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.uniform_number=form.uniform_number.data
        member.homecountry=form.homecountry.data
        db.session.commit()
        return redirect(url_for('get_member', member_id=member.member_id))

    form.member_id.data = member.member_id
    form.first_name.data = member.first_name
    form.last_name.data = member.last_name
    form.uniform_number.data = member.uniform_number
    form.homecountry.data = member.homecountry
    return render_template('update_member.html', form=form, pageTitle='Update Member', legend="Update A Member")


if __name__ == '__main__':
    app.run(debug=True)
