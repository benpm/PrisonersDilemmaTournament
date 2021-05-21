# Meta-detective: the final form

import numpy as np

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
def s_ant(H: np.ndarray, M): # Anti-joss
    if M is None:
        M = 1
    elif H[1,-1] == 0:
        M = 0
    if M == 1:
        return M, M
    else:
        return s_alt(H,M)
def s_jos(H: np.ndarray, M): # Joss with high probability
    return 0 if np.random.random() < 0.15 else s_t4t(H,M)[0], None

DEFAULT_STRAT = s_def
X_T4T = s_ant

TEST_PATTERN = (1,0,0,1,1)
PATTERN_FILE = open("md.txt", "w")
TEST_MODE = True
PATTERNS = {
    (1,1,0,1,1): s_jos, # simpleton
    (1,1,1,0,1): s_alt, # ftft
    # ?                 # random
    (1,1,0,0,0): s_def, # grimTrigger
    (1,0,1,1,1): s_cop, # detective
    (1,1,0,0,1): X_T4T, # joss
    (1,1,0,0,1): X_T4T, # titForTat
    (1,1,0,1,1): s_jos, # oracle
    (0,0,0,0,0): s_def, # alwaysDefect
    (1,1,1,1,1): s_def, # alwaysCooperate
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
