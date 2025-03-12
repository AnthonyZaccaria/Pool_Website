from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    #allows us to store a note with a user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # one to many relationship 


#UserMixin is because we are using Flask_login
class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(150),unique=True)
    password = db.Column(db.String(150))
    admin = db.Column(db.Boolean)
    notes = db.relationship('Note')

class Standings(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    Player = db.Column(db.String(100))
    Wins = db.Column(db.Integer)
    Losses = db.Column(db.Integer)
    Balls_Pocketed = db.Column(db.Integer)
    Balls_Allowed = db.Column(db.Integer)
    Streak = db.Column(db.String(5))
    LDE = db.Column(db.Integer)
    WDE = db.Column(db.Integer)
    Division = db.Column(db.Integer)
    Skill_Predictor = db.Column(db.Float)
    DifMultiplier = db.Column(db.Float)
    Floyd_Warshall = db.Column(db.Integer)
    Power_Ranking = db.Column(db.Integer)
    Early_8 = db.Column(db.Integer)
    Wrong_Pocket = db.Column(db.Integer)
    Scratch_on_8 = db.Column(db.Integer)
    Off_Table = db.Column(db.Integer)

class Reports(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    Winner = db.Column(db.String(100))
    Loser = db.Column(db.String(100))
    Win_BP = db.Column(db.Integer)
    Lose_BP = db.Column(db.Integer)
    Error = db.Column(db.Integer)
    

class Players(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(100))
    Skill = db.Column(db.Float)
    
class Playoff_Matchups(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    P1seed = db.Column(db.Integer)
    Player1 = db.Column(db.String(100))
    Player1_score = db.Column(db.Integer)
    P2seed = db.Column(db.Integer)
    Player2 = db.Column(db.String(100))
    Player2_score = db.Column(db.Integer)
    
    