import hashlib


def md5(s)->str:
    return hashlib.md5(s).hexdigest()

def sha1(s)->str:
    return hashlib.sha1(s).hexdigest()

def md5str(s:str)->str:
    return hashlib.md5(s.encode()).hexdigest()

def sha1str(s:str)->str:
    return hashlib.sha1(s.encode()).hexdigest()
