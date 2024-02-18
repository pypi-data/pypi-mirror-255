import bcrypt

def bcryptHash(password:str)->str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def bcryptCheck(inputPassword:str,dbPassword:str)->bool:
    return bcrypt.checkpw(inputPassword.encode(), dbPassword.encode())

