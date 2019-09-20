from micropython import const

DEEPSLEEP_RESET = const(0)

def reset_cause():
    return DEEPSLEEP_RESET

def deepsleep(t=None):
    return