def error(str):
    CRED = '\033[91m'
    CEND = '\033[0m'
    return print(CRED + str + CEND)

def warn(str):
    CRED = '\033[33m'
    CEND = '\033[0m'
    return print(CRED + str + CEND)

def success(str):
    CRED = '\033[32m'
    CEND = '\033[0m'
    return print(CRED + str + CEND)

def info(str):
    CRED = '\033[34m'
    CEND = '\033[0m'
    return print(CRED + str + CEND)

def debug(str):
    CRED = '\033[35m'
    CEND = '\033[0m'
    return print(CRED + str + CEND)