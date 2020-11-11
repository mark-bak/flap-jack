##Some code to simulate an odd card game with different play strategies
import random
from itertools import permutations
import matplotlib.pyplot as plt

class Game():

    def __init__(self,player):
        self.player = player

    def start(self):
        self.player.reset()
        self.c = Cards()
        self.c.shuffle()
        self.finished = False

    def play(self):
        while not self.finished:
            p = self.step()
        return p

    def step(self):
        
        #check if cards remaining or player is bust
        if self.c.cards_left == False or self.player.score>25:
            p = self.end_game(self.player)
        else:
            #see what palyer wants to do, stick or get new card dealt
            decision = self.player.decide()
            if decision == 'stick':
                p = self.end_game(self.player)
            else:
                card,value = self.c.deal()
                self.player.update(card,value)
        if self.finished == True:
            return p 

    def end_game(self,player):
        if player.score >25 or player.score <16:
            points = 10
        else:
            points = 25-player.score
        self.finished = True
        #print(self.cards_remaining)
        #print('cards: '+str(player.cards_dealt))
        #print("score: "+str(player.score))
        #print('points :'+str(points))
        return points


class Cards():
    ##Deck of cards used in game, with shuffle and deal funtions##
    def __init__(self):
        #list of cards in game
        self.cards = {
            "rA":-1,
            "r2":-2,
            "r3":-3,
            "r4":-4,
            "r5":-5,
            "r6":-6,
            "r7":-7,            
            "r8":-8,
            "r9":-9,
            "r10":-10,
            "rJ":-10,
            "rQ":-10,
            "rK":-10,

            "b2":2,
            "b3":3,
            "b4":4,
            "b5":5,
            "b6":6,
            "b7":7,            
            "b8":8,
            "b9":9,
            "b10":10,
            "bJ":10,
            "bQ":10,
            "bK":10,
            "bA":11,
        }
        self.order = list(self.cards.keys())
        self.n = 0
        self.cards_left = True

    def shuffle(self):
        random.shuffle(self.order)    

    def deal(self):
        #deals next card, returns name and nominal value
        if self.n+1==len(self.order): # check cards left
            self.cards_left = False
        card = self.order[self.n]
        value = self.cards[self.order[self.n]]
        self.n += 1
        return card,value

class SimplePlayer():
    
    def reset(self):
        self.cards_dealt ={}
        self.score = 0
        c = Cards()
        self.cards_remaining = c.cards

    def decide(self):
        #always draw and therefore always lose
        return 'draw'

    def update(self,card,value):
        self.cards_remaining.pop(card)
        self.cards_dealt[card] = value
        self.score+=value

class StickPlayer(SimplePlayer):
    def __init__(self,stick_val):
        self.stick_val = stick_val

    def decide(self):
        if self.score>=self.stick_val:
            return 'stick'
        else:
            return 'draw'

class ProbPlayer(SimplePlayer):
    def __init__(self,stick_val,depth):
        self.stick_val = stick_val
        self.depth=depth

    def decide(self):
        n_rem_cards = len(self.cards_remaining)
        if self.score>15 and n_rem_cards<=self.depth:

            perms = list(permutations(self.cards_remaining.values(),n_rem_cards))
            permslist = [list(t) for t in perms]
            cumulative_score = self.cumulative_score(permslist,n_rem_cards)
            s_ex = self.determine_prob(cumulative_score,n_rem_cards)
            #print('expected: '+str(s_ex))
            #print('current: ' + str(25-self.score))
            if s_ex>25-self.score:
                return 'stick'
            #else:
            #    print('hit me')
        if self.score>=self.stick_val and n_rem_cards>self.depth:
            return 'stick'
        else:
            return 'draw'

    def cumulative_score(self,lis,d):
        for i in range(0,len(lis)):
            lis[i][0] += self.score 
            for j in range(1,d):
                lis[i][j] += lis[i][j-1]
        return lis

    def determine_prob(self,c_s,d):
        #bust_ind =[]
        #bet_ind = []
        scores =[]

        check_ind = []
        check_ind_next = list(range(0,len(c_s)))
        #worse_ind =[]
        for j in range(0,d):
            check_ind = check_ind_next[:]
            check_ind_next.clear()
            #check whether lines are bust or winning
            for i in check_ind:
                if c_s[i][j]>25:
                    #bust_ind.append(i)
                    scores.append(10)
                elif c_s[i][j]>15 and c_s[i][j]<=25:
                    #bet_ind.append(i)
                    scores.append(25-c_s[i][j])
                else:
                    check_ind_next.append(i)

        scores = scores+[10]*len(check_ind)
        base_prob = 1/len(c_s)

        score_exp = sum(scores)*base_prob
        return score_exp

def play_games(player,no_games):
    game = Game(player)
    points = []
    for i in range(0,no_games):
        game.start()
        points.append(game.play())
    return points



def test_stick(no_games,vals):
    results =[]
    for v in vals:
        player = StickPlayer(v)
        results.append(play_games(player,no_games))
    return results

def test_prob(no_games,vals,depth):
    results =[]
    for d in depth:
        player = ProbPlayer(vals,d)
        results.append(play_games(player,no_games))
    return results

n_g = 100000

#plot optimal stick value
vals = [16,17,18,19,20,21,22,23,24,25]
valstr = [str(v) for v in vals]
res = test_stick(n_g,vals)
res_ave =[]

for i in range(0,len(res)):
    res_ave.append(sum(res[i])/len(res[i]))

plt.figure(1)
plt.bar(valstr,res_ave)

#plot comparison of prob player and best stick player
d = [8]
dstr = [str(x) for x in d]
resP = test_prob(n_g,19,d)
resP_ave =[]

for i in range(0,len(resP)):
    resP_ave.append(sum(resP[i])/len(resP[i]))

resP_ave.append(res_ave[3])
dstr.append('stick')
print(resP_ave)
plt.figure(2)
plt.bar(dstr,resP_ave)
plt.show()
print('done')