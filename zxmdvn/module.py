from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash , check_password_hash
from datetime import datetime
import os

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

class Admin(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    category = db.Column(db.String(100))
    heading = db.Column(db.String(100))
    descreptions  = db.Column(db.String(100))
    photo = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    photo_id = db.Column(db.Integer , db.ForeignKey('admin.id'))
    text = db.Column(db.String(100))
    user_email = db.Column(db.String(100))  
    user_name = db.Column(db.String(100))   
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reply(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    comment_id = db.Column(db.Integer , db.ForeignKey('comment.id'))
    text = db.Column(db.String(100))
    user_email = db.Column(db.String(100))  
    user_name = db.Column(db.String(100))   
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100))  # User
    photo_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # Kis photo pe
    vote_type = db.Column(db.String(10))  # 'like' or 'dislike'
    

def config_md_maruf(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/upload'
    os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok=True)

    db.init_app(app)
    with app.app_context():
        db.create_all()

def save_to_db(name,email,password):
    if User.query.filter_by(email=email).first():
        return False
    hased = generate_password_hash(password)
    user = User(name=name , email=email , password=hased)
    db.session.add(user)
    db.session.commit()
    return True

def Validate_User(email,password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password , password):
        return user
    return False

def Update_password (email,new_password):
    user = User.query.filter_by(email=email).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return True
    return False

def save_to_admin(category, heading , descreptions , photo_url):
    admin = Admin(category=category , heading=heading , descreptions=descreptions ,  photo=photo_url)
    db.session.add(admin)
    db.session.commit()
    

def save_to_comment(text,photo_id, user_email, user_name):
    comment = Comment(photo_id=photo_id , text=text , user_email=user_email , user_name=user_name)
    db.session.add(comment)
    db.session.commit()

def save_to_reply_db(text,comment_id,user_email, user_name):
    reply = Reply(comment_id=comment_id , text=text ,  user_email=user_email , user_name=user_name)
    db.session.add(reply)
    db.session.commit()


def get_votes(photo_id):
    likes = Vote.query.filter_by(photo_id=photo_id, vote_type='like').count()
    dislikes = Vote.query.filter_by(photo_id=photo_id, vote_type='dislike').count()
    return likes, dislikes
    

