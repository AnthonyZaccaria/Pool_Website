# Anthony Zaccaria
# Capstone
# Scheduling
from website.static.HelpfulGraphs import WeightDigraph
from copy import deepcopy
from math import sqrt
from random import shuffle
import heapq


# updates the streak section for standings
# streak: string that indicates a player's current win/loss streak
# event: boolean value where True means win and False means loss
# returns a string that is the updated player's streak
def update_streak(streak,event):
    updated = ""
    if event:
        try:
            if streak[0] =='W':
                num = int(streak[1:]) +  1
                updated = 'W' + str(num)
            else:
                updated = 'W1'
        except:
            updated = 'W1'
    else:
        try:
            if streak[0] =='L':
                num = int(streak[1:]) +  1
                updated = 'L' + str(num)
            else:
                updated = 'L1'
        except:
            updated = 'L1'
            
    return updated

# randomly creates division break_up
def rand_divisions(players,num_div):
    # Randomly creates divisions
    divisions = []
    for i in range(num_div):
        divisions.append([])
    playerList = deepcopy(players) #Copy to preserve original list
    shuffle(playerList)
    div = num_div - 1
    for p in playerList:
        divisions[div].append(p)
        div -= 1
        if div < 0:
            div = num_div - 1
    return divisions

# partitions the players into divisions
# num_div: int that is the number of divisions to partition players into
# fact_skill: boolean. True if skill is factored into division creation; False otherwise
# players: List of tuples. Each tuple is of the following format ("name of player",skill_value,)
def create_divisions(players,num_div = 1,fact_skill=False):
    if fact_skill: #if skill is factored in
        chosen = [] #list of chosen nodes
        for i in range(10): #up to 10 random restarts
            divisions = rand_divisions(players,num_div) #random restart
            d = (node_value(divisions),deepcopy(divisions)) #vertex; It's a tuple (value of node,division breakup)
            heap = [d]
            stop = False
            while not stop: #only want to go if the current value is < previous value
                prev_value = d[0]
                neighbors = generate_neighbors(d[1])
                for n in neighbors:
                    heapq.heappush(heap,n) #adds the neighbors to the heap
                d = heapq.heappop(heap)
                if d[0] >= prev_value or d[0] == 0:
                    stop = True
            chosen.append(d)
            if chosen[-1][0] == 0: #if perfect division breakup, then stop
                return chosen[-1][1]
        return min(chosen)[1] #returns chosen node with minimum value

    else: #return random break up if skill is not factored
        divisions = rand_divisions(players,num_div)
        return divisions 


# generates neighbors of a division break up
# returns a set of the neighbors
def generate_neighbors(divisions):
    neighbors = [] 
    cop_divisions = deepcopy(divisions) #copy so we don't change original
    for i in range(len(cop_divisions)-1): #goes through divisions (except last one)
        for j in range(len(cop_divisions[i])): #goes through players in divisions
            for k in range(i+1,len(cop_divisions)): #idea is to swap i,j with jth elements in rest of divisions
                for m in range(len(cop_divisions[i])): #goes through players in other divisions
                    neib = deepcopy(cop_divisions) #a single neighbor
                    temp = neib[i][j]
                    neib[i][j]=neib[k][m]
                    neib[k][m] = temp
                    tup = (node_value(neib),neib) #tuple with value and division breakup
                    if tup not in neighbors: #don't add duplicates (maybe I shouldn't include this part)
                        neighbors.append(tup)
    return neighbors

# gets value of a division break up 
# value is variance of skill totals
def node_value(divisions):
    tot = []
    avg = 0 #will contain the average
    for i in range(len(divisions)): #gets each division
        tot.append(0)
        for p in divisions[i]: #gets each player in division i
            tot[i] += p[2] #adds skill value to division total
        avg += tot[i]
    avg /= len(divisions)
    var = 0 #will contain variance at the end
    for t in tot:
        var += (t-avg)**2
    return var


# creates a schedules for the players
# num_games: int that is number of games each players will play against each other in the division
# divisions: 2D list which contains the divisions players are in
def create_schedule(divisions,num_games = 1):
    return True


'''
index key:
wins = 2
losses = 3
BP = 4
BA = 5
'''

# Updates the skill value of a given player
# player: tuple with name of player we are updating, and his necessary stats
def update_skill(player):
    return True


# Updates the skill predictor value of a given player
# player: tuple with name of player we are updating, and his necessary stats
def update_skill_predictor(player):
    sp = 0
    sp = ((player[2]-player[3])/sqrt(player[2]+player[3])) + ((player[4]-player[5])/(player[2]+player[3]))

    return round(sp,2)


# Updates the DifMultiplier value of a given player
# player: tuple with name of player we are updating, and his necessary stats
def update_difMult(player):
    dm = 0
    if player[5] != 0 and player[3] != 0:
        dm = sqrt(100*(player[4]/player[5])*(player[2]/player[3]))
        return round(dm,2)
    else:
        return None


#gets weighted difference matrix
#param: adj_mat - adjacency matrix
#returns weighted difference matrix (mat[i][j]-mat[j][i])/(mat[i][j]+mat[j][i]) i.e. (([wins-losses]/games_played))
def weightedDifference(adj_mat):
    nMat = deepcopy(adj_mat)
    for i in range(1,len(adj_mat)):#rows
        for j in range(1,len(adj_mat)):#columns
            if nMat[i][j] == 'inf':
                nMat[i][j]=float('inf')    
            else:
                nMat[i][j]=float(adj_mat[i][j])
    for i in range(1,len(nMat)):#rows
        for j in range(1,len(nMat)):#columns
            if i==j:
                continue
            elif nMat[i][j] == float('inf') and nMat[j][i] == float('inf') or nMat[i][j]+nMat[j][i] == 0:
                continue
            elif nMat[i][j] == float('inf') and nMat[j][i] != float('inf'): #if i never beat j but j beat i
                #print('i:',i,'; j:',j)
                nMat[j][i] = 1 #weighted Difference for j,i should be 1
                nMat[i][j] = -1 #weighted Difference for i.j should be -1
            elif nMat[i][j] != float('inf') and nMat[j][i] == float('inf'): #if j never beat i but i beat j
                #print('j:',j,'; i:',i,)
                nMat[i][j] = 1 #weighted difference for i,j should be 1
                nMat[j][i] = -1 #weighted Difference for j,i should be -1
            else:
            #if nMat[i][j] != float('inf') and nMat[j][i] != float('inf'): 
                nMat[i][j] = (float(adj_mat[i][j])-float(adj_mat[j][i]))/(float(adj_mat[i][j])+float(adj_mat[j][i]))
    return nMat

# performs Floyd Warshall algorithm on an adjacency matrix
# param: M - adjacency matrix. Should be weighted difference matrix
# returns adjacency matrix with updated values
def pool_floyd_warshall(M):
    small = 0
    # gets minimum value in matrix and converts every value to a float
    for i in range(1,len(M)):
        for j in range(1,len(M)):
            M[i][j] = float(M[i][j])
            if i==j:
                continue
            if M[i][j] < small:
                small = M[i][j]
    # Makes necessary adjustment if small < 0
    if small<0:
        for i in range(1,len(M)):
            for j in range(1,len(M)): 
                if i==j or M[i][j]==float('inf'):
                    continue
                M[i][j] += 0-small+.5

    # actual Floyd-Warshall Algorithm
    for i in range(1,len(M)):
        for j in range(1,len(M)):
            for k in range(1,len(M)):
                if M[j][k] > M[j][i] + M[i][k]:
                    #print(True,j,k,i)
                    #print('i,j,k:',i,j,k)
                    M[j][k] = float(M[j][i]) + float(M[i][k])

    return M




'''
Testing create_divisions:

players = [(1,"anth",3),(2,"john",7),(3,"Tom",9),(4,"noah",5.5),(5,"Dan",6),(6,"Joey",4.5),(7,"Laura",5),(8,"Alexa",2)]
divs = rand_divisions(players,3)
divs
hi = generate_neighbors(divs)
for i in range(len(hi)):
    print(i,':',hi[i])
hello = create_divisions(players,num_div=3,fact_skill = True)
hello
'''