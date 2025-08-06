import json
from bson import json_util
from flask import current_app as app
from flask_pymongo import PyMongo

mongo = PyMongo(app)


class DbContext:
    MONGO = ""
    USERS = ""

    @classmethod
    def initializeCollections(cls):
        cls.USERS = cls.MONGO.Users

    @classmethod
    def insertUser(cls, user) -> bool:
        # user = IettaSecurity.encryption(user)
        cls.USERS.insert_one(user)
        return True
        # return False

    @classmethod
    def deleteUsers(cls) -> bool:
        # cls.USERS.delete_many({})
        return True

    @classmethod
    def getUser(cls, email):
        if email:
            user = cls.convertBsonToJson(cls.USERS.find_one({"email": email}))
            # user = IettaSecurity.decryption(user)
            return user

    @classmethod
    def checkUserExist(cls, email) -> bool:
        if email:
            return True if cls.USERS.find_one({"email": email}) != None else False

    @classmethod
    def verifyUser(cls, id, email) -> bool:
        user = cls.getUser(email)
        if int(id) == int(user["randomId"]):
            where = {"email": email}
            update = {"$set": {"verfiedStatus": True}}
            cls.USERS.update_one(where, update)
            return True
        return False

    @classmethod
    def getProjects(cls, email) -> list:
        user = cls.getUser(email)
        if user is not None:
            return user.get("Projects")
        else:
            return []

    @staticmethod
    def convertBsonToJson(data):
        return json.loads(
            json_util.dumps(data)
        )  # converts the bson returned data to json

    @classmethod
    def createProject(cls, userEmail, project) -> dict:
        user = cls.getUser(userEmail)
        if user is None:
            return {
                "status": False,
                "error": "User Not Found/Session Expired",
            }  # either the session has expired or the user no longer exists
        if len(user.get("Projects")) >= 10:
            return {
                "status": False,
                "error": "Project Creation's Limit Reached",
            }  # the maximum number of projects for a user is 50 (10 set for testing)
        if project["name"].isspace():
            return {"status": False, "error": "Empty Spaces not Allowed"}
        for pro in user.get("Projects"):
            if project["name"] == pro["name"]:
                return {
                    "status": False,
                    "error": "Project Already Exists",
                }  # a project with the same name already exists before
        user.get("Projects").append(
            {
                "name": project["name"],
                "tags": project["tags"],
                "files": project["files"],
            }
        )
        where = {"email": userEmail}
        update = {"$set": {"Projects": user.get("Projects")}}
        cls.USERS.update_one(where, update)
        return {
            "status": True,
            "description": "Project Added Successfully",
        }  # project creation successfull

    @classmethod
    def uploadFile(cls, userEmail, projectName, fileToSave) -> dict:
        # getting the user from database
        user = cls.getUser(userEmail)

        # either the session has expired or the user no longer exists
        if user is None:
            return {"status": False, "error": "User Not Found/Session Expired"}

        # if user exists
        for project in user.get("Projects"):
            # finding the project with the name specified
            if project["name"] == projectName:
                # file name must be different
                if fileToSave in project["files"]:
                    return {"status": False, "error": "Use a Different Name"}
                else:
                    # file name appended in the files list of the project
                    project["files"].append(fileToSave)

                    # updates the user in the database with updated project
                    where = {"email": userEmail}
                    update = {"$set": {"Projects": user.get("Projects")}}
                    cls.USERS.update_one(where, update)

                    # project updation with filename successfull hence returned
                    return {"status": True, "uploadedFile": fileToSave}

        # At this point no project with given name was found so no file was appended
        return {"status": False, "error": "No Project with name specified"}

    @classmethod
    def updateProjects(cls, userEmail, updatedProject) -> dict:
        # getting the user from database
        user = cls.getUser(userEmail)

        # either the session has expired or the user no longer exists
        if user is None:
            return {"status": False, "error": "User Not Found/Session Expired"}

        # if user exists
        for project in user.get("Projects"):
            # finding the project with the name specified
            if project["name"] == updatedProject["name"]:
                # tags updated in the specified project
                project["tags"] = updatedProject["tags"]

                # updates the user in the database with updated project
                where = {"email": userEmail}
                update = {"$set": {"Projects": user.get("Projects")}}
                cls.USERS.update_one(where, update)

                # project updation with new tags successfull hence returned
                return {"status": True}

        # At this point no project with given name was found so no file was appended
        return {"status": False, "error": "No Project with name specified"}

    @classmethod
    def getImagePath(cls, email):
        user = cls.getUser(email)
        return user["img"]

    @classmethod
    def getTags(cls, userEmail, projectName):
        userProjects = cls.getProjects(userEmail)
        for userProject in userProjects:
            if projectName == userProject["name"]:
                return userProject["tags"]
        # At this point no project with given name as found
        return False

    @classmethod
    def getProjectTagsStat(cls, userEmail):
        userProjects = cls.getProjects(userEmail)
        stats = []
        for userProject in userProjects:
            stats.append(
                {"ProjectName": userProject["name"], "tags": len(userProject["tags"])}
            )
        return stats

    @classmethod
    def getProjectFileStats(cls, userEmail):
        userProjects = cls.getProjects(userEmail)
        stats = []
        for userProject in userProjects:
            stats.append(
                {"ProjectName": userProject["name"], "files": len(userProject["files"])}
            )
        return stats

    @classmethod
    def deleteProject(cls, userEmail, projectName):
        userProjects = cls.getProjects(userEmail)
        for userProject in userProjects:
            if userProject["name"] == projectName:
                userProjects.remove(userProject)
                where = {"email": userEmail}
                update = {"$set": {"Projects": userProjects}}
                cls.USERS.update_one(where, update)
                return True
        return False


DbContext.MONGO = mongo.db
DbContext.initializeCollections()
