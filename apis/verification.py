from flask import current_app as app
from flask import jsonify, redirect, request
from flask_restx import Namespace, Resource

from Models.DB_Context import DbContext

api = Namespace(
    name="verification", description="Operations related verification of user account"
)


@api.route("/verify_email")
class Verification(Resource):
    def get(self):
        id = request.args.get("user_id")
        userEmail = request.args.get("user_name")
        isVerified = DbContext.verifyUser(id, userEmail)
        if isVerified:
            return redirect(app.config["FRONT_END_URL"])
        else:
            return jsonify(
                {
                    "status": False,
                    "error": "Invalid ID. Verification Link Altered/Corrupted",
                }
            )
