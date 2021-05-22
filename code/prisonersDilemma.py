import os
import itertools
import importlib
import numpy as np
import random
import sys

STRATEGY_FOLDERS = ["strats", "strats/extras"]
RESULTS_FILE = "results.txt"
ME = sys.argv[1] if len(sys.argv) > 1 else ''

LENGTH_MULT = 1

pointsArray = [[1,5],[0,3]] # The i-j-th element of this array is how many points you receive if you do play i, and your opponent does play j.
moveLabels = ["D","C"]
# D = defect,     betray,       sabotage,  free-ride,     etc.
# C = cooperate,  stay silent,  comply,    upload files,  etc.


# Returns a 2-by-n numpy array. The first axis is which player (0 = us, 1 = opponent)
# The second axis is which turn. (0 = first turn, 1 = next turn, etc.
# For example, it might have the values
#
# [[0 0 1]       a.k.a.    D D C
#  [1 1 1]]      a.k.a.    C C C
#
# if there have been 3 turns, and we have defected twice then cooperated once,
# and our opponent has cooperated all three times.
def getVisibleHistory(history, player, turn):
    historySoFar = history[:,:turn].copy()
    if player == 1:
        historySoFar = np.flip(historySoFar,0)
    return historySoFar

def strategyMove(move):
    if type(move) is str:
        defects = ["defect","tell truth"]
        return 0 if (move in defects) else 1
    else:
        return move

def runRound(paths, pair):
    moduleA = importlib.import_module(paths[0].replace("/", "."))
    moduleB = importlib.import_module(paths[1].replace("/", "."))
    memoryA = None
    memoryB = None
    
    LENGTH_OF_GAME = LENGTH_MULT * int(200-40*np.log(random.random())) # The games are a minimum of 50 turns long. The np.log here guarantees that every turn after the 50th has an equal (low) chance of being the final turn.
    history = np.zeros((2,LENGTH_OF_GAME),dtype=int)
    
    for turn in range(LENGTH_OF_GAME):
        playerAmove, memoryA = moduleA.strategy(getVisibleHistory(history,0,turn),memoryA)
        playerBmove, memoryB = moduleB.strategy(getVisibleHistory(history,1,turn),memoryB)
        history[0,turn] = strategyMove(playerAmove)
        history[1,turn] = strategyMove(playerBmove)
    
    if ME in pair:
        i = int(pair[1] == ME)
        me = [moduleA, moduleB][i]
        # print(memoryA if pair[0] == ME else memoryB)
        print(" VS", f"{pair[1-i]:<32}", end="\t")# "\taccuracy:", me.correct / me.predictions, "naughtiness:", me.naughtiness)
    return history
    
def tallyRoundScores(history):
    scoreA = 0
    scoreB = 0
    ROUND_LENGTH = history.shape[1]
    for turn in range(ROUND_LENGTH):
        playerAmove = history[0,turn]
        playerBmove = history[1,turn]
        scoreA += pointsArray[playerAmove][playerBmove]
        scoreB += pointsArray[playerBmove][playerAmove]
    return scoreA/ROUND_LENGTH, scoreB/ROUND_LENGTH
    
def outputRoundResults(f, pair, roundHistory, scoresA, scoresB):
    if ME not in pair:
        return
    f.write(pair[0]+" (P1)  VS.  "+pair[1]+" (P2)\n")
    for p in range(2):
        for t in range(roundHistory.shape[1]):
            move = roundHistory[p,t]
            f.write(moveLabels[move]+" ")
        f.write("\n")
    f.write("Final score for "+pair[0]+": "+str(scoresA)+"\n")
    f.write("Final score for "+pair[1]+": "+str(scoresB)+"\n")
    f.write("\n")
    
def runFullPairingTournament(inFolders, outFile):
    print("Starting tournament, reading files from", inFolders)
    print(ME)
    scoreKeeper = {}
    scoreAvgDiff = {}
    strats = []
    for folder in inFolders:
        for file in os.listdir(folder):
            if file.endswith(".py"):
                strats.append((file[:-3], f"{folder}/{file[:-3]}"))
            
    for strategy, _ in strats:
        scoreKeeper[strategy] = 0
        scoreAvgDiff[strategy] = 0
    
    f = open(outFile,"w+")
    j = 0
    for S in itertools.combinations(strats, r=2):
        pair = S[0][0], S[1][0]
        paths = S[0][1], S[1][1]
        if ME in pair:
            j += 1
            print(f" {j:>2}: ", end='')
        roundHistory = runRound(paths, pair)
        scoresA, scoresB = tallyRoundScores(roundHistory)
        if ME in pair:
            i = int(pair[1] == ME)
            s = [scoresA, scoresB]
            print(f"{s[i]:.3}\t", f"{s[i] - s[1-i]:.3}")
        outputRoundResults(f, pair, roundHistory, scoresA, scoresB)
        scoreKeeper[pair[0]] += scoresA
        scoreKeeper[pair[1]] += scoresB
        scoreAvgDiff[pair[0]] += scoresA - scoresB
        scoreAvgDiff[pair[1]] += scoresB - scoresA

    for name, _ in strats:
        scoreAvgDiff[name] /= len(strats)
    S = sorted(scoreAvgDiff.keys(), key=lambda k: scoreAvgDiff[k], reverse=True)

    for name in S:
        print(f"{name:<24}: {scoreAvgDiff[name]}")
        
    scoresNumpy = np.zeros(len(scoreKeeper))
    for i in range(len(strats)):
        scoresNumpy[i] = scoreKeeper[strats[i][0]]
    rankings = np.argsort(scoresNumpy)

    f.write("\n\nTOTAL SCORES\n")
    for rank in range(len(strats)):
        i = rankings[-1-rank]
        score = scoresNumpy[i]
        scorePer = score/(len(strats)-1)
        # f.write("#"+str(rank+1)+": "+pad(strats[i][0]+":",16)+' %.3f'%score+'  (%.3f'%scorePer+" average)\n")
        f.write(f"#{rank + 1:>2} {strats[i][0]:<32} {score:.3f} ({scorePer:.3f} avg)\n")
        
    f.flush()
    f.close()
    print("Done with everything! Results file written to "+RESULTS_FILE)
    
    
runFullPairingTournament(STRATEGY_FOLDERS, RESULTS_FILE)
