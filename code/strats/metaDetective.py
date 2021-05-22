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
def s_m4t(H: np.ndarray, M): # Moral t4t
    return 1 if (H[0,-2] + H[1,-1] == 0 or H[0,-3] + H[1,-2] == 0) else s_t4t(H, M)[0], M
def s_alt(H: np.ndarray, M): # Alternate
    return 1-H[0,-1], M
def s_al4(H: np.ndarray, M): # Co-op, defect x 3, repeat
    return [1,0,0,0][H.shape[1] % 4], M
def s_la4(H: np.ndarray, M): # Co-op x3, defect, repeat
    return [1,1,1,0][H.shape[1] % 4], M
def s_la3(H: np.ndarray, M): # C D D
    return [1,0,0][H.shape[1] % 3], M
def s_ant(H: np.ndarray, M): # Anti joss, t4t, ftft-like
    m = M
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
    if H[0,-3] + H[1,-2] != 0 and H[0,-2] == 1 and H[1,-1] == 0:
        # They defected unexpectedly - it's a joss-like
        M = Mode.anti_joss

    if np.sum(H[1,-4:]) == 0:
        # I triggered a grim something or other
        M = Mode.dead
    
    if TEST_MODE and m != M:
        print(M.name, end=" ")
    
    if M == Mode.anti_t4t:
        return 1, M
    elif M == Mode.anti_forgive:
        if (1 - H[0]).sum() < 4:
            return s_jos(H, M, 0.05)
        else:
            return 1, M
    elif M == Mode.anti_joss:
        return s_alt(H, M)
    elif M == Mode.anti_moral:
        if (1 - H[0]).sum() < 4:
            return s_jos(H, M, 0.05)
        else:
            return 1, M
    elif M == Mode.dead:
        return 0, M
def s_jos(H: np.ndarray, M, P=0.15, per=1): # like joss with high probability
    return 0 if (rnd() < P and (1-H[0,-per:]).sum() == 0) else s_m4t(H,M)[0], M

DEFAULT_STRAT = s_def

TEST_PATTERN = (1,0,0,1,1)
TEST_MODE = False
PATTERNS = {
    (1,1,1,0,1): s_alt, # [ftft]
    (1,1,0,0,0): s_ant, # [grimTrigger]
    (1,0,1,1,1): s_cop, # some detectives
    (1,1,0,0,1): s_ant, # [joss], t4t-likes
    (0,0,1,0,1): s_ant, # [evilTitForTat]
    (1,1,0,1,1): s_ant, # [oracle], [simpleton]
    (0,0,0,0,0): s_def, # [alwaysDefect]
    (1,1,1,1,1): s_alt, # [alwaysCooperate], some types of forgiving t4t
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
        if R in PATTERNS:
            return PATTERNS[R](history, memory)
        else:
            return s_def(history, memory)
