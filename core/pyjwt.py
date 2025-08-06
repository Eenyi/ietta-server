from typing import Callable, Any
from flask import request, jsonify

import jwt
from cryptography.fernet import (
    Fernet,
)  # for encryption of user object before storing in database

from core.config import Config, MailConfig

key = Fernet(Config.INVISIBILITY.encode())


class PyJWT:
    @classmethod
    def encodeToken(cls, userInDb, key) -> str:
        token = jwt.encode(
            payload={
                "username": userInDb.get("username"),
                "email": userInDb.get("email"),
            },
            key=key,
            algorithm="HS256",
        )
        return token

    @classmethod
    def decodeToken(cls, token, key) -> dict:
        return jwt.decode(token, key, algorithms=["HS256"])


class IettaSecurity:
    @classmethod
    def authorization(cls, token):
        if token == None:
            return False
        else:
            return PyJWT.decodeToken(token, MailConfig.MAIL_PASSWORD)["email"]

    @classmethod
    def encryption(cls, user):
        user.update(
            {
                "username": key.encrypt(user.get("username").encode()),
                "password": key.encrypt(user.get("password").encode()),
            }
        )
        print(user)
        return user

    @classmethod
    def decryption(cls, user):
        user.update(
            {
                "username": key.decrypt(user.get("username")).decode(),
                "password": key.decrypt(user.get("password")).decode(),
            }
        )
        print(user)
        return user

def auth(old_function: Callable) -> Callable:
    def wrapper(*args) -> Any:
        token = request.headers.get("Authorization")
        if token == None:
            return jsonify({"status": False, "error": "Authorization Failed"})
        else:
            userEmail = PyJWT.decodeToken(token, MailConfig.MAIL_PASSWORD).get("email")
            if userEmail == None:
                return jsonify({"status": False, "error": "Invalid Token"})
            else:
                return old_function(*args, userEmail)

    return wrapper
