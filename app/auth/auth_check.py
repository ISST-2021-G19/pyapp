import hashlib
import os
import bcrypt


def getEncodedPassword(password: str, salt: bytes) -> str:
    key = bcrypt.hashpw(password.encode(), salt)

    return key


def getEncodedPasswordback(password: str, salt: bytes) -> str:
    salt = bcrypt.gensalt()
    key = bcrypt.hashpw(password.encode(), salt)

    return key
