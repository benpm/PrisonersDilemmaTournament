# Meta-detective: the final form

import numpy as np
from enum import Enum

rnd = np.random.random

def s_def(H: np.ndarray, M): # Always defect
    return 0, None
def s_cop(H: np.ndarray, M): # Always co-op
    return 1, None
def s_t4t(H: np.ndarray, M): # Tit for tat
    return int(not H[1,-1] == 0), None
def s_alt(H: np.ndarray, M): # Alternate
    return 1-H[0,-1], None
def s_al4(H: np.ndarray, M): # Co-op, defect x 3, repeat
    return [1,0,0,0][H.shape[1] % 4], None
def s_la4(H: np.ndarray, M): # Co-op x3, defect, repeat
    return [1,1,1,0][H.shape[1] % 4], None
def s_ant(H: np.ndarray, M): # Anti-joss with tiny bit of defection
    if M is None:
        M = 1
    elif H[1,-1] == 0:
        M = 0
    if M == 1:
        return M, M
    else:
        return s_alt(H,M)
def s_jos(H: np.ndarray, M): # Joss with high probability
    return 0 if (rnd() < 0.15 and H[0,-1]==1) else s_t4t(H,M)[0], None
def s_jos(H: np.ndarray, M): # Joss with low probability
    return 0 if (rnd() < 0.0 and H[0,-1]==1) else s_t4t(H,M)[0], None

DEFAULT_STRAT = s_def

TEST_PATTERN = (1,0,0,1,1)
TEST_MODE = False
if TEST_MODE:
    PATTERN_FILE = open("md.txt", "w")
PATTERNS = {
    (1,1,1,0,1): s_alt, # [ftft]
    (1,1,0,0,0): s_def, # [grimTrigger]
    (1,0,1,1,1): s_cop, # some detectives
    (1,1,0,0,1): s_ant, # [joss], [titForTat]
    (1,1,0,1,1): s_jos, # [oracle], [simpleton]
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
            PATTERN_FILE.write(f"({','.join([str(r) for r in R])})\n")
        if R in PATTERNS:
            return PATTERNS[R](history, memory)
        else:
            return s_def(history, memory)
