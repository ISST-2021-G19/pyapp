import hashlib
import os
import bcrypt

def getEncodedPassword(password: str, salt: bytes) -> str:
    key = bcrypt.hashpw(password.encode(), salt)

    return key 
