class AdjacencyMatrix():
    __a_mat__ = [] #The actual adjacency matrix  [row][column]
    __csv_file__ = '' #name of the csv file we are storing the matrix as
    __players__=[]
    #Contructor
    # param: csv_file: String that is the name of the .csv file we will grab the adjacency matrix from
    def __init__(self,csv_file,players):
        self.__players__ = players
        self.build(csv_file,players)


    # Idea of this method is to build the adjacency matrix from the csv
    def build(self,csv_file,players):
        self.__csv_file__ = csv_file
        #If the file already exists, I just want to append what is needed.
        self.__a_mat__ = [] #clears the adjacency matrix
        try: #if file exists
            text = open(self.get_csv_file()).read().split("\n") #opens the file and turns it into a list of Strings 
            text = text[:-1] #gets rid of blank row
            for t in text: #goes through each row in the text list
                row = t.split(",")
                self.__a_mat__.append(row)
            for p in players: #Note* each player is a tuple ("name of player",nothing)
                if p[0] not in self.__a_mat__[0]: #if a player in the tournament is not in the adjancency matrix
                    self.__a_mat__[0].append(str(p[0])) #adds player to the first row
                    for i in range(1,len(self.__a_mat__)):
                        self.__a_mat__[i].append('inf') #goes through the rows and appends 0
                    new_row = [p[0]]
                    for i in range(1,len(self.__a_mat__[0])-1): #goes through columns (except last column)
                        new_row.append('inf') #adds infinity into new row
                    new_row.append('0') #adds 0 since this is where last player plays last player.
                    self.__a_mat__.append(new_row) #adds new row into matrix

        except: #else create the csv file
            self.first_time(csv_file,players)
    
    # Idea of this method is to store the adjacency matrix as a csv
    def store(self):
        mat = self.get_adjacency_matrix()
        with open(self.get_csv_file(), "w") as f:
            for r in range(len(mat)):
                row = mat[r] #gets row of adjacency matrix
                #print("row:",row)
                f.write(','.join(row)+'\n')
                
    # creates the csv for the first time from a list of players. Also creates the initial a_mat
    # only use this method when creating the csv/adjacency matrix for the first time
    # param: csv_file- String that is the name of the .csv file we will save the thing to
    # players: a list of players in the tournament
    def first_time(self,csv_file,players):
        new_players = [] #list of players
        for p in players:
            new_players.append(str(p[0]))
        text = '-,'+','.join(new_players)
        self.__a_mat__.append(text.split(','))
        for i in range(len(new_players)):
            new_row = new_players[i] #string that will contain row that is being added to the csv/matrix
            #text += '\n'+players[i]
            for j in range(len(new_players)):
                if i==j:
                    new_row += ',0' #adds 0 since this is where player plays himself
                else:
                    new_row += ',inf' #adds infinity into new row
                #text += ',0'
            text += '\n'+new_row
            self.__a_mat__.append(new_row.split(','))
        with open(csv_file, "w") as f:
            f.write(text)

    # idea of this method is to update the matrix after a loss
    # param: winner_id- int that is the winner's id in the Players Table
    # param: loser_id- int that is the loser's id in the Players Table
    def adjust_matrix(self,winner_id,loser_id):
        if self.get_adjacency_matrix()[winner_id][loser_id] == 'inf':
            entryW = 1
        else:
            entryW = int(self.get_adjacency_matrix()[winner_id][loser_id])    
            entryW += 1
        self.__a_mat__[winner_id][loser_id] = str(entryW)    
    
    # Adds player to the adjacency matrix 
    def add_player(self,player):
        row = [player] #list that is the new row
        self.__a_mat__[0].append(player) #adds a column
        for i in range(1,len(self.get_adjacency_matrix())):
            self.__a_mat__[i].append('0') #makes new column 0s
            row.append('0') #makes new row 0s
        row.append('0') #needs this to make row have same size as other ones
        self.__a_mat__.append(row)
        self.__players__.append(player) #adds player to list of players
    
    # clears the adjacency matrix and the csv
    def clear(self):
        self.__a_mat__ = []
        with open(self.get_csv_file(), "w") as f:
            f.write('')        
        pass
    
    # getter methods
    def get_adjacency_matrix(self):
        return self.__a_mat__
    
    def get_csv_file(self):
        return self.__csv_file__
