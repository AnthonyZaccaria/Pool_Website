from flask import Blueprint, redirect, render_template, request, flash, url_for
from .models import Reports, Standings, User, Players, Playoff_Matchups
from werkzeug.security import generate_password_hash, check_password_hash
# for hashin passwords (still not too secure but better than plain text)
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import text
from website.static import Scheduling
from threading import Lock
from website.static.table import AdjacencyMatrix

auth = Blueprint('auth',__name__)

csv_file = "matrix.csv"

lock = Lock() # lock for login
lock1 = Lock() # lock for sign up
lock2 = Lock() # lock for report scores
lock3 = Lock() # lock for validate scores
lock4 = Lock() # lock for add players



@auth.route('/login', methods=['GET','POST'])
def login():
    lock.acquire()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                lock.release()
                return redirect(url_for('views.home')) #If logged in successfully
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('username does not exist.', category='error')

    data = request.form
    #print(data)
    lock.release()
    return  render_template("login.html",user=current_user,text="Testing",boolean = True)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.standings'))

@auth.route('/sign_up', methods=['GET','POST'])
def sign_up():
    lock1.acquire()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
        elif len(username)<2:
            flash('Username must be at least 2 characters.',category='error')
        elif len(password)<8:
            flash('Password must be at least 8 characters.',category='error')
        else:
            admin = False
            if len(username)>6 and username[-6:] == "*admin":
                admin = True #allows people to be admin
            #add user to database
            new_user = User(username=username,password=generate_password_hash(
                password, method='pbkdf2:sha256'),admin=admin)
            num = User.query.order_by(-User.id).first()
            if num.id < 120: #If the max player number is < 120, add the player to the league
                db.session.add(new_user)
                db.session.commit()
                flash('Successful sign-up!',category='success')
            #login_user(user, remember=True)
            else:
                flash('Talk to a league admin about signing up')
            lock1.release()
            return redirect(url_for('views.standings'))
    lock1.release()    
    return  render_template("sign_up.html",user=current_user)

@auth.route('/score_report', methods=['GET','POST'])
@login_required
def score_report():
    lock2.acquire()
    cursor = db.session.execute(text('SELECT * FROM Players'))
    items = cursor.fetchall()
    if request.method == 'POST':
        winner = request.form.get('winner')
        #print('winner = ',winner)
        loser = request.form.get('loser')
        try:        
            win_balls = int(request.form.get('ballW'))
            lose_balls = int(request.form.get('ballL'))
            if win_balls >8 or lose_balls >8 or win_balls <0 or lose_balls <0 or (win_balls == 8 and lose_balls == 8):
                flash("Invalid number of balls entered")
            elif winner == loser:
                flash("Same winner and loser!")
            else: #Only add to validate scores if score is okay and winner is not the same as the loser
                num = User.query.order_by(-User.id).first()
                if num.id < 1000: #Only runs if < 1000 scores are left unvalidated
                    error = int(request.form.get('error'))
                    if (error != 0 and error != 3) and (win_balls == 8 or lose_balls ==8) or (error == 0 and (win_balls != 8 and lose_balls !=8)) or (error == 2 and lose_balls != 7) or (error == 3 and lose_balls != 8):
                        flash("Score not possible with error type")
                    else:                                                                      
                        report = Reports(Winner = winner,Loser = loser,Win_BP = win_balls,Lose_BP = lose_balls,Error = error)
                        db.session.add(report)
                        db.session.commit()
                else:
                    flash("Too many reported scores, talk to league admin!")
        except:
            flash('invalid input')
    lock2.release()
    return render_template("score_report.html",user=current_user,items=items)

@auth.route('/validate_scores', methods=['GET','POST'])
@login_required
def validate_scores():
    if current_user.admin == True: #Makes sure only admins can access this page
        lock3.acquire()
        cursor = db.session.execute(text('SELECT * FROM Reports'))
        items = cursor.fetchall()
        if request.method == 'POST':
            r_id = request.form.get('id') 
            a = request.form.get('accept_delete')
            if a == "Accept":
                #print(r_id)
                winner = request.form.get('winner')
                #print(winner)
                loser = request.form.get('loser')
                #print(loser)
                win_balls = int(request.form.get('ballW'))
                lose_balls = int(request.form.get('ballL'))
                error = int(request.form.get('error'))
                user_w = Players.query.filter_by(Name=winner).first() #gets the winner from players table (also makes sure it is in table)
                user_l = Players.query.filter_by(Name=loser).first() #gets the loser from players table  (also makes sure it is in table)
                if (user_w and user_l):
                    user_w = Standings.query.filter_by(Player=winner).first()
                    user_w.Wins = user_w.Wins + 1
                    user_w.Balls_Pocketed = user_w.Balls_Pocketed+win_balls
                    user_w.Balls_Allowed = user_w.Balls_Allowed +lose_balls
                    user_w.Streak = Scheduling.update_streak(user_w.Streak,True)
        
                    if win_balls < 8: #if win is due to error
                        user_w.WDE = user_w.WDE + 1
                    db.session.add(user_w)
                #if (user_l):
                    user_l = Standings.query.filter_by(Player=loser).first()
                    user_l.Losses += 1
                    user_l.Balls_Pocketed += lose_balls
                    user_l.Balls_Allowed += win_balls
                    user_l.Streak = Scheduling.update_streak(user_l.Streak,False)
                    if win_balls < 8 or lose_balls >= 8: #if loss is due to error
                        user_l.LDE = user_l.LDE + 1
                        if error == 1:
                           user_l.Early_8 = user_l.Early_8 + 1
                        elif error == 2:
                            user_l.Wrong_Pocket = user_l.Wrong_Pocket + 1 
                        elif error == 3:
                           user_l.Scratch_on_8 = user_l.Scratch_on_8 + 1
                        else:
                           user_l.Off_Table = user_l.Off_Table + 1
                    db.session.add(user_l)
                    db.session.commit()
                    # adjust adjacency matrix
                    cursor = db.session.execute(text('SELECT Name FROM Players'))
                    players = cursor.fetchall()
                    Adj_Mat = AdjacencyMatrix(csv_file,players) #Right now, when it stores, it adds onto the current adj_mat
                    Adj_Mat.adjust_matrix(user_w.id,user_l.id)
                    Adj_Mat.store()

                    cursor = db.session.execute(text('SELECT * FROM Standings'))
                    players = cursor.fetchall()
                    user_w.Skill_Predictor = Scheduling.update_skill_predictor(players[user_w.id-1])
                    user_w.DifMultiplier = Scheduling.update_difMult(players[user_w.id-1])
                    user_l.Skill_Predictor = Scheduling.update_skill_predictor(players[user_l.id-1])
                    user_l.DifMultiplier = Scheduling.update_difMult(players[user_l.id-1])   
                    adjust_Floyd_Warshall(Adj_Mat.get_adjacency_matrix())

                else:# winner or loser not in database
                    flash("winner or loser not in tournament")

            report = Reports.query.filter_by(id = r_id).first()
            #If the report is still in the database
            if report:
                #delete the report
                db.session.delete(report)
                db.session.commit()
                if a == "Delete":
                    flash("Score Report Deleted")
                else:
                    flash("Score Report Accepted")
            lock3.release()
            return redirect(url_for('views.standings'))
        else:
            pass
        lock3.release()
        return  render_template("validate_scores.html",user=current_user, items=items)

    else:
        return redirect(url_for('views.standings'))

@auth.route('/add_players', methods=['GET','POST'])
@login_required
def add_players():
    if current_user.admin == True: #Makes sure only admins can access this page
        lock4.acquire()
        if request.method=='POST':
            name = request.form.get('name')
            p = Players.query.filter_by(Name=name)
            #print(name)
            exists = Players.query.filter_by(Name=name).first()
            #print(exists)
            if exists:
                flash('Player already in tournament')
            else:
                new_player = Players(Name=name,Skill = 0.0)
                db.session.add(new_player)
                db.session.commit()
                new_player_s = Standings(Player=name,Wins=0,Losses=0,Balls_Pocketed = 0,Balls_Allowed=0,Streak = "-",LDE=0,WDE=0,Skill_Predictor=0,DifMultiplier=0,Floyd_Warshall=0,Division=1)
                db.session.add(new_player_s)
                db.session.commit()
                cursor = db.session.execute(text('SELECT Name FROM Players'))
                players = cursor.fetchall()
                Adj_Mat = AdjacencyMatrix(csv_file,players)
                Adj_Mat.store()
                flash('Successful Player add!',category='success')
                #login_user(user, remember=True)
                lock4.release()
                return redirect(url_for('views.standings'))
        lock4.release()
        return render_template("add_players.html",user=current_user)
    else:
        return redirect(url_for('views.standings'))

@auth.route('/create_divisions', methods=['GET','POST'])
@login_required
def create_divisions():
    if current_user.admin == True: #Makes sure only admins can access this page
        if request.method=='POST':
            try:
                num_div = int(request.form.get('num_div'))
                #print(num_div)
                skill = request.form.get("skill") #True if skill is factored in. False otherwise
                if skill == 'yes':
                    skill = True
                else:
                    skill = False
                #print(skill)
                cursor = db.session.execute(text('SELECT * FROM Players'))
                players = cursor.fetchall()
                if num_div < 1 or num_div > len(players)//3:
                    flash("Enter a Positive Integer! Need at least three players in each division")
                else:
                    #print(1)
                    divs = Scheduling.create_divisions(players,num_div,skill) #division breakup
                    #print(2)
                    for i in range(len(divs)): #goes through divisions
                        #print('len(divs):',len(divs))
                        #print('divs',divs)
                        for j in range(len(divs[i])): #geos through players in each division
                            player = Standings.query.filter_by(id=divs[i][j][0]).first() #gets player by his id
                            #print(3)
                            player.Division = i+1 #assigns player correct division
                            db.session.add(player)
                            db.session.commit()
                    #print(4)
                return redirect(url_for('views.standings'))
            except:
                flash("Enter a Positive Integer")
            
        return render_template("create_divisions.html",user=current_user)
    else:
        return redirect(url_for('views.standings'))

#generates who is in playoffs and the first round matchups
@auth.route('/generate_playoffs', methods=['GET','POST'])
@login_required
def generate_playoffs():
    if current_user.admin == True: #Makes sure only admins can access this page
        playoffs = []
        matchups = []
        if request.method=='POST':
            db.session.query(Playoff_Matchups).delete()
            try:
                cursor = db.session.execute(text('SELECT * FROM Standings'))
                players = cursor.fetchall()
                #print(players)
                req_games = int(request.form.get('req_games')) #required number of games played
                max_teams = int(request.form.get('max_teams')) #maximum teams in playoffs
                divs_matter = request.form.get('divs') #whether or not divisions matter
                players.sort(key= lambda x:x[-1]) #sort by power rankings
                num_div = 1
                if divs_matter == 'yes':
                    num_div = max(players,key=lambda x:x[9])[9] #gets number of divisions
                    if max_teams < 1000:
                        max_frm_div = (max_teams//num_div)+1 
                    else:
                        max_frm_div = (len(players)//num_div)+1
                else: #no divisions
                    max_frm_div = max_teams

                by_div = [] #2d list with player in each division
                for i in range(num_div):
                    by_div.append([])
                for i in range(len(players)):
                    if players[i][2]+players[i][3] >= req_games:
                        if divs_matter == 'yes':
                            by_div[players[i][9]-1].append(players[i]) 
                            if len(by_div[players[i][9]-1]) <= max_frm_div: #if not too many player from that division
                                playoffs.append(players[i])
                        else:
                            playoffs.append(players[i])
                        if len(playoffs) >= max_teams:
                            break #if playoffs have enough teams, then stop adding teams to it

                min_power_of_2 = 0
                while 2**min_power_of_2 <= len(playoffs):
                    min_power_of_2 += 1
                min_power_of_2 -= 1
                size = len(playoffs)
                seed=1 #playoff seed
                for i in range(size-(2**min_power_of_2)): #gives best players a bye if necessary
                    p1 = (seed,)+tuple(playoffs[0])
                    matchups.append((p1,None))
                    playoffs.pop(0) #removes from top
                    seed += 1
                while len(playoffs)>0:
                    p1 = (seed,)+tuple(playoffs[0]) #adds seed to tuple
                    p2 =  (size,)+tuple(playoffs[-1]) #adds seed to tuple
                    matchups.append((p1,p2)) #Keeps Matching up best and worst players
                    seed += 1 #increase seed of better player
                    size -= 1 #decrease seed of worse player
                    playoffs.pop(0) #removes from top
                    playoffs.pop() #removes from end
                for m in matchups:
                    #print(m)
                    if m[1] != None:
                        matchup = Playoff_Matchups(P1seed = m[0][0],Player1 = m[0][2],Player1_score=0,P2seed=m[1][0],Player2 = m[1][2],Player2_score=0)
                    else:
                        matchup = Playoff_Matchups(P1seed = m[0][0],Player1 = m[0][2],Player1_score=1)
                    db.session.add(matchup)
                    db.session.commit()
            except:
                flash("Not enough players qualify")

        return render_template("generate_playoffs.html",user=current_user)
    else:
        return redirect(url_for('views.standings'))
# adjusts floyd warshall value for each player
# in here so we can access and update database easier
# adj_mat: wins adjacency matrix
# return True when done
def adjust_Floyd_Warshall(adj_mat):
    #print("accessed")
    mat = Scheduling.weightedDifference(adj_mat) 
    #print(mat)
    new_mat = Scheduling.pool_floyd_warshall(mat)
    #print(new_mat)
    # updates Floyd Warshall value for each player
    for i in range(1,len(new_mat)):
        player = Standings.query.filter_by(id=i).first() 
        # loop gets sum of row i
        tot = 0
        tot_col = 0
        for j in range(1,len(new_mat[i])):
            if i==j: #if same player, then continue
                continue
            elif new_mat[i][j] == float('inf'):
                if new_mat[j][i] != float('inf'):
                    tot_col += new_mat[j][i]
            else:
                tot += new_mat[i][j]
                tot_col += new_mat[j][i] 
        player.Floyd_Warshall = round(tot/tot_col,2)
        db.session.add(player)
        db.session.commit()
        
    return True

@auth.route('/get_power_rankings', methods=['GET','POST'])
@login_required
def get_power_rankings():
    if current_user.admin == True: #Makes sure only admins can access this page
        if request.method=='POST':
            cursor = db.session.execute(text('SELECT * FROM Standings'))
            players = cursor.fetchall()
            sp_sorted = sorted(players,key = lambda x:x[10],reverse=True)
            dm_sorted = sorted(players,key = lambda x:x[11],reverse=True)
            fw_sorted = sorted(players,key = lambda x:x[12],reverse=True)
            for i in range(len(players)):
                sp = 0
                dm = 0
                fw = 0
                for j in range(len(sp_sorted)):
                    if players[i][0] == sp_sorted[j][0]:
                        sp = j
                    if players[i][0] == dm_sorted[j][0]:
                        dm = j
                    if players[i][0] == fw_sorted[j][0]:
                        fw = j
                players[i]=tuple(players[i])+(sp+dm+fw,)
            #print(players)
            ranked_players = sorted(players,key=lambda x:x[-1])
            for i in range(len(ranked_players)):
                player = Standings.query.filter_by(id=ranked_players[i][0]).first() #gets player by his id
                player.Power_Ranking = i+1 #assigns player correct power ranking
                db.session.add(player)
                db.session.commit()
            return redirect(url_for('views.standings'))
            
        return render_template("get_power_rankings.html",user=current_user)
    else:
        return redirect(url_for('views.standings'))
