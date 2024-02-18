import string
import random
letters = string.ascii_letters + string.digits
letterUpper = string.ascii_uppercase + string.digits
letterLower = string.ascii_lowercase + string.digits

def rand(size=32)->str:
    return ''.join(random.choice(letters) for _ in range(size))

def randLower(size=32)->str:
    return ''.join(random.choice(letterLower) for _ in range(size))

def randUpper(size=32)->str:
    return ''.join(random.choice(letterUpper) for _ in range(size))

def randAscii(size=32)->str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(size))

def randInt(size=6)->str:
    return ''.join(random.choice(string.digits) for _ in range(size))