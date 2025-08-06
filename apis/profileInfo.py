from flask import current_app as app
from flask import jsonify, request, send_file
from flask_restx import Namespace, Resource

from core.pyjwt import IettaSecurity, auth
from Models.DB_Context import DbContext

api = Namespace(
    name="profileInfo",
    description="Operations related to fetching user profile information",
)


@api.route("/get_profile")
class Profile(Resource):
    def get(self):
        userEmail = IettaSecurity.authorization(request.args.get("img"))
        if userEmail is False:
            return jsonify({"status": False, "error": "Authorization Failed"})
        return send_file(DbContext.getImagePath(userEmail))


@api.route("/get_stats")
class Stats(Resource):
    @auth
    def get(self, userEmail: str):
        return jsonify(
            [
                DbContext.getProjectFileStats(userEmail),
                DbContext.getProjectTagsStat(userEmail),
            ]
        )
