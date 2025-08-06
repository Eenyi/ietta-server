import datetime
import os

from flask import current_app as app
from flask import jsonify, request
from flask_mail import Mail
from flask_restx import Namespace, Resource
from werkzeug.utils import secure_filename

from core.Emailing_Module import Email_Module
from core.User import User
from core.pyjwt import PyJWT
from Models.DB_Context import DbContext

api = Namespace(
    name="accounts",
    description="Operations related to account management like login and signup",
)

mailedApp = Mail(app)


@api.route("/signup")
class Signup(Resource):
    def post(self):
        file_extension = os.path.splitext(request.files["profileImage"].filename)[
            1
        ]  # Gets the extension of the file
        if [".png", ".jpeg", ".jpg"].count(file_extension) == 0:
            return jsonify({"status": False, "error": "Profile Image Type Invalid"})
        if (
            request.form.get("username").isspace()
            or request.form.get("password").isspace()
        ):
            return jsonify({"status": False, "error": "Empty Spaces are not Allowed"})
        request.files["profileImage"].filename = (
            str(datetime.datetime.now()) + request.files["profileImage"].filename
        )
        user = User(
            username=request.form.get("username"),
            email=request.form.get("email"),
            password=request.form.get("password"),
            img=f"{app.config['USER_IMAGES']+secure_filename(request.files['profileImage'].filename)}",
        )
        isUserExit = DbContext.checkUserExist(request.form.get("email"))
        if isUserExit == False:
            request.files["profileImage"].save(
                app.config["USER_IMAGES"]
                + secure_filename(request.files["profileImage"].filename)
            )
            if DbContext.insertUser(user.__dict__) == True:
                Email_Module.verification_email(mailedApp, user)
                return jsonify({"status": True})
        return jsonify({"status": False, "error": "Email Already Exists"})


@api.route("/login")
class Login(Resource):
    def post(self):
        user = {
            "email": request.form.get("email"),
            "password": request.form.get("password"),
        }
        if DbContext.checkUserExist(user.get("email")):
            userInDb = DbContext.getUser(user.get("email"))
            if not userInDb.get("verfiedStatus"):
                return jsonify({"status": False, "error": "Email not Verified"})
            if user.get("password") == userInDb.get("password"):
                token = PyJWT.encodeToken(userInDb, app.config["MAIL_PASSWORD"])
                return jsonify({"status": True, "auth_token": token})
            else:
                return jsonify({"status": False, "error": "Invalid Password"})
        else:
            return jsonify({"status": False, "error": "Invalid Email"})
