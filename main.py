from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    year = db.Column(db.String(120), nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    time = db.Column(db.String(120), nullable=False)
    comment = db.Column(db.String(500), nullable=False)


db.create_all()


## PART ONE ##
@app.route('/')
def home():
    # just simple page for fast test
    return render_template("index.html")


@app.route('/users')
def get_all_users():
    users = User.query.all()
    output = user_to_dict(users)
    return output


@app.route('/user/<name>')
def get_one_user(name):
    user = User.query.filter(User.name == name)
    output = user_to_dict(user)
    return output


def user_to_dict(users):
    output = json.dumps([{"id": user.id, "name": user.name, "birth year": user.year} for user in users])
    return output


@app.route('/add-user/<name>/<year>')
def add_user(name, year):
    new_user = User(
        name=name,
        year=year,
    )
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        print("User already exists")
    return redirect(url_for("get_all_users"))


@app.route('/edit-users/<user>/<new_name>/<new_year>')
def edit_user(user, new_name, new_year):
    try:
        user_to_edit = User.query.get(user)
        user_to_edit = User.query.filter(User.name == user)[0]
        user_to_edit.name = new_name
        user_to_edit.year = new_year
        db.session.commit()
    except:
        pass
    return redirect(url_for("home"))


@app.route('/delete-user/<user>')
def delete_user(user):
    try:
        user_to_delete = User.query.filter(User.name == user)[0]
        comments_to_delete = Comment.query.filter(Comment.user_id == user_to_delete.id).all()
        for comment in comments_to_delete:
            db.session.delete(comment)
        db.session.delete(user_to_delete)
        db.session.commit()
    except:
        pass
    return redirect(url_for("get_all_users"))


@app.route('/comments')
def get_all_comments():
    comments = Comment.query.all()
    output = comments_to_dict(comments)
    return output


@app.route('/comment/<index>')
def get_one_comment(index):
    comment = Comment.query.filter(Comment.id == index)
    output = comments_to_dict(comment)
    return output


def comments_to_dict(comments):
    output = json.dumps(
        [{"id": comment.id, "user name": comment.user_name, "time": comment.time, "comment": comment.comment} for
         comment in comments])
    return output


@app.route('/create-comment/<name>/<comment>')
def create_comment(name, comment):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    new_comment = Comment(
        user_id=User.query.filter(User.name == name)[0].id,
        user_name=name,
        time=current_time,
        comment=comment
    )
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for("get_all_comments"))


@app.route('/edit-comment/<index>/<comment>')
def edit_comment(index, comment):
    try:
        comment_to_edit = Comment.query.get(index)
        comment_to_edit.comment = comment
        db.session.commit()
    except:
        pass
    return redirect(url_for("get_all_comments"))


@app.route("/delete-comment/<index>")
def delete_comment(index):
    try:
        comment_to_delete = Comment.query.get(index)
        db.session.delete(comment_to_delete)
        db.session.commit()
    except:
        pass
    return redirect(url_for("get_all_comments"))


## PART TWO ##
@app.route('/random-animal')
def get_animal():
    url = "https://zoo-animal-api.herokuapp.com/animals/rand"
    response = requests.get(url)
    data = response.json()
    name = data["name"]
    latin_name = data["latin_name"]
    output = json.dumps([{"name": name, "latin name": latin_name}])
    return output


if __name__ == "__main__":
    app.run(debug=True)
