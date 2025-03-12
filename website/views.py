from flask import Blueprint, redirect, flash, json, jsonify, render_template, request, url_for
from flask_login import login_required, current_user
from .models import Note, Reports, Players, Standings, Playoff_Matchups
from . import db
from sqlalchemy import text
from website.static import pool_sim

views = Blueprint('views',__name__)


@views.route('/home',methods=['GET','POST'])
@login_required
def home():
    if request.method=='POST':
        note = request.form.get('note')
        if len(note) < 1:
            flash('Note is too short!',category = 'error')
        else:
            new_note = Note(data=note,user_id = current_user.id) #says who wrote the note
            db.session.add(new_note) #adds to database
            db.session.commit()
            flash('Note added!',category='success')    
    return render_template("home.html",user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the delete.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id or current_user.admin:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/simulator',methods=['GET','POST'])
def simulator():
    cursor = db.session.execute(text('SELECT * FROM Standings'))
    items = cursor.fetchall()
    sim_players = make_sim_ready(items)
    result = ()
    if request.method=='POST':
        #print(sim_players)
        p1 = request.form.get('p1')
        p2 = request.form.get('p2')
        if (p1!=p2):
            player1=[]
            player2=[]
            for i in range(len(sim_players)):
                if p1 == sim_players[i][3]:
                    player1 = sim_players[i]
                elif p2==sim_players[i][3]:
                    player2 = sim_players[i]
            result = pool_sim.PoolTheGame(player1,player2)
            #print(2)
        else:
            flash("Player 1 should not be same as Player 2")
        
        pass
    return render_template("simulator.html",user=current_user,items=sim_players,result=result,n_res = len(result))
def make_sim_ready(players):
    sim_players = []
    sp_sorted = sorted(players,key = lambda x:x[10],reverse=True)
    dm_sorted = sorted(players,key = lambda x:x[11],reverse=True)
    fw_sorted = sorted(players,key = lambda x:x[12],reverse=True)
    for i in range(len(players)):
        sim_players.append([])
    for i in range(len(sim_players)):
        skill = 0
        lose_val = 15
        sp = (players[i][10]-sp_sorted[-1][10]+1)/(sp_sorted[0][10]-sp_sorted[-1][10]+1) # (player sp)/(max sp) with adjustment
        dm = players[i][11]/dm_sorted[0][11]
        fw = players[i][12]/fw_sorted[0][12]
        skill += round((sp+dm+fw)*2+2,2)
        sim_players[i].append(skill)
        sim_players[i].append(1.5)
        if players[i][2]+players[i][3]>0:
            lose_val = ((players[i][7])/(players[i][2]+players[i][3]-(players[i][8]/2)))*100
        sim_players[i].append(lose_val)
        sim_players[i].append(players[i][1])
    return sim_players


@views.route('/')
def standings():
    cursor = db.session.execute(text('SELECT * FROM playoff__matchups'))
    playoffs = cursor.fetchall()
    cursor = db.session.execute(text('SELECT * FROM Standings'))
    items = cursor.fetchall()
    #num_pl is number of people in playoffs
    #num_div is number of divisions
    num_div=max(items,key= lambda x:x[9])[9]
    divs = [i for i in range(1,num_div+1)]
    return render_template("standings.html",user=current_user,items=items,playoffs=playoffs,num_pl=len(playoffs),divs=divs)
'''
@views.route('/add_players')
@login_required
def add_players():
    if request.method=='POST':
        name = request.form.get('name')
        exists = Players.query.filter_by(Name=name).first()
        if exists:
            flash('Player already in tournament')
        else:
            new_player = Players(Name=name)
            db.session.add(new_player)
            db.session.commit()
            new_player = Standings(Player=name,Wins=0,Losses=0,Balls_Pocketed=0,Balls_Allowed=0,Streak='-',Skill_Predictor=0,DifMultiplier=0,Floyd_Warshall=0,Division=1)
            db.session.add(new_player)
            db.session.commit()
            flash('Successful Player add!',category='success')
            #login_user(user, remember=True)
            return redirect(url_for('views.home'))
    return render_template("add_players.html",user=current_user)
'''