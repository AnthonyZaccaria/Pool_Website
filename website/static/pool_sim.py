# Pool Simulator for website
import random
from website.static.HelpfulGraphs import WeightDigraph

#Usable precreated Players.             
John=[7,1.25,30,'John']
Tom=[7,1,10,'Tom']
Anthony=[3.5,2,20,'Anthony']
Alejandro=[5,3,30,'Alejandro']
Joey=[4.25,3.5,25,'Joey']
Laura=[5,2,23,'Laura']
Noe=[5.25,1,18,'Noe']
DomW=[5.5,2,10,'DomW']
Jack=[2.75,3.5,18,'Jack']
Dan=[6,2,15,'Dan']
MikeW=[7,1,15,'MikeW']
Declan=[5.75,1.25,20,'Declan']

# [skill value,consistancy,loss_value,name]

#Notice: each game affects each players base stats until you rerun the program
#This actaully makes sense since this mimics streakiness
def PoolTheGame(P1,P2):
    #print('Welcome to The matchup between',P1[3],'and',P2[3]+'!!!')
    #print('+ Blessed Pier Giorgio Frassati, patron saint of the Mount Pool Tournament, pray for us. Amen. +')
    way='due to skill'
    G=WeightDigraph()
    G,turns,winner,loser=poolSimulator(P1,P2)
    if 8 not in G[winner]:
        way='due to error'
    win_balls = len(G[winner])
    lose_balls = len(G[loser])
    return (winner,loser,turns,way,win_balls,lose_balls)
    #print('Game Results:',G)
    #print(winner,'beat',loser,'in',turns,'turns',way)

def poolSimulator(P1,P2):
    P1[0]=random.uniform(max(2,P1[0]-P1[1]),min(P1[0]+P1[1],10))
    P2[0]=random.uniform(max(2,P2[0]-P2[1]),min(P2[0]+P2[1],10))
    print(P1[0])
    print(P2[0])
    end=False
    lose=False
    win=False
    brk=False
    winner='NA'
    loser='NA'
    A=[P1[0],P1[2],P1[3]]
    B=[P2[0],P2[2],P2[3]]
    n=0
    nA=0 
    nB=0
    goAgain=False
    P = WeightDigraph()
    P.add(P1[3])
    P.add(P2[3])
    for i in range(8):
        P.add(i+1)
    while not end:
        n+=1
        if n==1:
            brk=True
        else:
            brk=False
        P,nA,lose,win,goAgain=simTurn(P,P1[3],A,n,nA,brk)
        if goAgain and not lose and not win:
            while goAgain:
                brk=False
                P,nA,lose,win,goAgain=simTurn(P,P1[3],A,n,nA,brk)
                if lose:
                    winner=P2[3]
                    loser=P1[3]
                    end=True
                    return P,n,winner,loser
                if win:
                    winner=P1[3]
                    loser=P2[3]
                    end=True
                    return P,n,winner,loser
        if lose and not brk:
            winner=P2[3]
            loser=P1[3]
            end=True
            return P,n,winner,loser
        elif lose and brk:
            for i in range(8):
                if (i+1) not in P[P1[3]]:
                    P.add_edge(P1[3],i+1,0)
            winner=P1[3]
            loser=P2[3]
            end=True
            return P,n,winner,loser
        elif win:
            winner=P1[3]
            loser=P2[3]
            end=True
            return P,n,winner,loser
        else:
            brk=False
            P,nB,lose,win,goAgain=simTurn(P,P2[3],B,n,nB,brk)
            if goAgain and not lose and not win:
                while goAgain:
                    P,nA,lose,win,goAgain=simTurn(P,P2[3],B,n,nB,brk)
                    if lose:
                        winner=P1[3]
                        loser=P2[3]
                        end=True
                        return P,n,winner,loser
                    if win:
                        winner=P2[3]
                        loser=P1[3]
                        end=True
                        return P,n,winner,loser            
            if lose:
                winner=P1[3]
                loser=P2[3]
                end=True
                return P,n,winner,loser
            if win:
                winner=P2[3]
                loser=P1[3]
                end=True
                return P,n,winner,loser
            
def simTurn(D,player,att,n,nP,brk):
    lose=False
    win=False
    goAgain=False
    ballsIn=0
    for i in range(8):
        if brk:
            loss=random.randrange(0,1500-round(att[0])*100)
        elif i+1==7:
            loss=random.randrange(0,50)
        else:
            loss=random.randrange(0,100)
        if (i+1) not in D[player]:
            nP+=1
            #print("turn",n,"and player",player)
            #print("nP:",nP)
            hit=random.randrange(0,12)
            if hit>=12-att[0]:
                D.add_edge(player,i+1,nP)
                nP=0
                ballsIn+=1
                goAgain=True
                if loss<att[1]/10:
                    lose=True
                    return D,nP,lose,win,False
                for j in range(7):
                    hit=random.uniform(0,10)
                    if hit>=10-(att[0]/(10**min((ballsIn),2.5))) and i+1+ballsIn<8:
                        D.add_edge(player,i+1+ballsIn,nP)
                        ballsIn+=1
                    elif i+1+ballsIn==8:
                        if hit>=10-(1/att[0])/2:
                            D.add_edge(player,i+1+ballsIn,nP)
                    else:
                        break
                break
            else:
                if loss<att[1]/10:
                    lose=True
                break
    if 8 in D[player] and D[player][8]!=0:
        win=True
    elif 8 in D[player] and D[player][8]==0:
        lose=True
    #print(D)    
    return D,nP,lose,win,goAgain
