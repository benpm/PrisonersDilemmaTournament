# Meta-detective: the final form

import numpy as np
from enum import Enum

rnd = np.random.random

class Mode(Enum):
    unknown = -1
    anti_joss = 0
    anti_forgive = 1
    anti_t4t = 2
    anti_moral = 3
    dead = 4

def s_def(H: np.ndarray, M): # Always defect
    return 0, M
def s_cop(H: np.ndarray, M): # Always co-op
    return 1, M
def s_t4t(H: np.ndarray, M): # Tit for tat
    return int(not H[1,-1] == 0), M
def s_alt(H: np.ndarray, M): # Alternate
    return 1-H[0,-1], M
def s_al4(H: np.ndarray, M): # Co-op, defect x 3, repeat
    return [1,0,0,0][H.shape[1] % 4], M
def s_la4(H: np.ndarray, M): # Co-op x3, defect, repeat
    return [1,1,1,0][H.shape[1] % 4], M
def s_la3(H: np.ndarray, M): # C D D
    return [1,0,0][H.shape[1] % 3], M
def s_ant(H: np.ndarray, M): # Anti joss, t4t, ftft-like
    if M is None:
        # Test them for forgiveness
        M = Mode.unknown
        return 0, M
    elif M == Mode.unknown:
        if H[1,-1] == 0:
            # They aren't forgiving
            M = Mode.anti_t4t
        else:
            # They are forgiving
            M = Mode.anti_forgive
    
    if H[0,-2] == 0 and H[1,-1] == 1:
        # They cooperated unexpectedly - it's a moral t4t
        M = Mode.anti_moral

    if np.sum(H[1,-3:]) == 0:
        # I triggered a grim something or other
        M = Mode.dead
    
    if M == Mode.anti_t4t:
        if H[0,-2] == 1 and H[1,-1] == 0:
            # They defected unexpectedly - it's a joss-like
            M = Mode.anti_joss
        return 1, M
    elif M == Mode.anti_forgive:
        return s_los(H, M)
    elif M == Mode.anti_joss:
        return s_alt(H, M)
    elif M == Mode.anti_moral:
        return s_la3(H, M)
    elif M == Mode.dead:
        return 0, M
def s_jos(H: np.ndarray, M): # like joss with high probability
    return 0 if (rnd() < 0.15 and H[0,-1]==1) else s_t4t(H,M)[0], M
def s_los(H: np.ndarray, M): # like joss with low probability
    return 0 if (rnd() < 0.02 and H[0,-1]==1) else s_t4t(H,M)[0], M

DEFAULT_STRAT = s_def

TEST_PATTERN = (1,0,0,1,1)
TEST_MODE = True
if TEST_MODE:
    PATTERN_FILE = open("md.txt", "w")
PATTERNS = {
    (1,1,1,0,1): s_alt, # [ftft]
    (1,1,0,0,0): s_def, # [grimTrigger]
    (1,0,1,1,1): s_cop, # some detectives
    (1,1,0,0,1): s_ant, # [joss], [titForTat]
    (1,1,0,1,1): s_def, # [oracle], [simpleton]
    (0,0,0,0,0): s_def, # [alwaysDefect]
    (1,1,1,1,1): s_def, # [alwaysCooperate]
    (1,0,0,1,1): s_la4, # most other detectives
    (1,1,1,1,0): s_la4, # [shortwindow]
}

def strategy(history: np.ndarray, memory):
    turn = history.shape[1]
    if turn < len(TEST_PATTERN):
        return TEST_PATTERN[turn], None
    else:
        R = tuple(history[1,:len(TEST_PATTERN)])

        if TEST_MODE and turn == len(TEST_PATTERN):
            print(R, end="")
            PATTERN_FILE.write(f"({','.join([str(r) for r in R])})\n")
        if R in PATTERNS:
            return PATTERNS[R](history, memory)
        else:
            return s_def(history, memory)
