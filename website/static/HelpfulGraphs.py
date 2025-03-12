
class WeightDigraph(dict):
    def add(self, v):
        if v not in self:
            self[v] = {}

    def add_edge(self, u, v, weight):
        self[u][v]=weight

    def losers(self,v):
        losers=0
        vert=[]
        for d in self:
            vert.append(d)
        flag=False
        i=0
        while not flag:
            if len(self[vert[i]])>0:
                for w in self[vert[i]]:
                    if v==w:
                        losers+=self[vert[i]][w]
            if i<len(vert)-1:
                i+=1
            else:
                flag=True
        return losers

    def isBest(self,Player):
        best=False
        if self.losers(Player)==0:
            best=True
        return best

    def isWorst(self,Player):
        worst=False
        if len(self[Player])==0:
            worst=True
        return worst