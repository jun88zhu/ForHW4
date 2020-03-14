from flask import Flask
from flask import render_template,redirect,request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
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
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    uniform_number = StringField('Uniform Number:', validators=[DataRequired()])
    homecountry = StringField('Homecountry:', validators=[DataRequired()])


@app.route('/')
def index():
    all_members = jzhu72.query.all()
    return render_template('index.html', members=all_members,pageTitle='lakers team member')

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

if __name__ == '__main__':
    app.run(debug=True)
