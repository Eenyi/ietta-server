import json
import os
import shutil
from zipfile import ZipFile

from flask import current_app as app
from flask import jsonify, request, send_file
from flask_restx import Namespace, Resource

from core.pyjwt import auth
from Models.DB_Context import DbContext

api = Namespace(
    name="projects",
    description="Operations related to user projects management like project creation"
    "fetching projects data, import/export, adding tags, deleting projects",
)


@api.route("/project")
class Project(Resource):
    @auth
    def post(self, userEmail: str):
        project = request.json["project"]
        response = DbContext.createProject(userEmail, project)
        return jsonify(response)

    @auth
    def get(self, userEmail: str):
        projects = DbContext.getProjects(userEmail)
        return jsonify(projects)


@api.route("/add_tags")
class AddTag(Resource):
    @auth
    def post(self, userEmail: str):
        # Getting project object.
        updatedProject = request.json["project"]

        # See in DBContext.py about how response is formed
        response = DbContext.updateProjects(userEmail, updatedProject)

        # return response after jsonifying
        return jsonify(response)


@api.route("/import_export")
class ImportExport(Resource):
    @auth
    def get(self, userEmail: str):
        path = app.config["EXPORTED_PROJECTS"]
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path, exist_ok=True)
        # Getting project object.
        projectName = request.args.get("projectName")
        projectTags = DbContext.getTags(userEmail, projectName)
        if projectTags is False:
            return jsonify({"failure": False})
        with open(
            app.config["USER_FILES"] + f"{projectName}-tags.json", "w"
        ) as fileForTags:
            fileForTags.write(json.dumps(projectTags))
        with ZipFile(
            app.config["EXPORTED_PROJECTS"] + projectName + ".zip", "w"
        ) as zip_object:
            for folder_name, sub_folders, file_names in os.walk(
                app.config["USER_FILES"] + f"{userEmail}\\" + f"{projectName}"
            ):
                for filename in file_names:
                    file_path = os.path.join(folder_name, filename)
                    zip_object.write(file_path, os.path.basename(file_path))
            zip_object.write(
                app.config["USER_FILES"] + f"{projectName}-tags.json",
                os.path.basename(app.config["USER_FILES"] + f"{projectName}-tags.json"),
            )
        os.remove(app.config["USER_FILES"] + f"{projectName}-tags.json")
        os.rename(
            app.config["EXPORTED_PROJECTS"] + projectName + ".zip",
            app.config["EXPORTED_PROJECTS"] + projectName + ".iettax",
        )
        return send_file(
            app.config["EXPORTED_PROJECTS"] + projectName + ".iettax", mimetype="zip"
        )

    @auth
    def post(self, userEmail: str):
        # Checking if the file is a zip
        if os.path.splitext(request.files["project"].filename)[1] != ".iettax":
            return jsonify(
                {"status": {"status": False, "error": "Not an Ietta Project File"}}
            )
        projectName = os.path.splitext(request.files["project"].filename)[0]
        projectPath = app.config["USER_FILES"] + f"{userEmail}" + f"\\{projectName}\\"
        os.makedirs(projectPath, exist_ok=True)
        request.files["project"].save(projectPath + projectName + ".zip")
        try:
            with ZipFile(projectPath + projectName + ".zip", "r") as zip:
                zip.extractall(projectPath)
            files = []
            for folder_name, sub_folders, file_names in os.walk(
                app.config["USER_FILES"] + f"{userEmail}\\" + f"{projectName}"
            ):
                for filename in file_names:
                    if len(os.path.splitext(filename)) == 2:
                        if os.path.splitext(filename)[1] == ".txt":
                            files.append(filename)
            with open(
                projectPath + f"{projectName}-tags.json", "r", encoding="utf-8"
            ) as jsonTags:
                tags = list(json.load(jsonTags))
            importedProject = {"name": projectName, "tags": tags, "files": files}
            response = DbContext.createProject(userEmail, importedProject)
            os.remove(projectPath + projectName + ".zip")
            os.remove(projectPath + projectName + "-tags.json")
            return jsonify({"status": response, "project": importedProject})
        except:
            return jsonify(
                {"status": {"status": False, "error": "Import Operation Failed"}}
            )


@api.route("/delete_project")
class DeleteProject(Resource):
    @auth
    def get(self, userEmail: str):
        projectName = request.args.get("projectName")
        response = DbContext.deleteProject(userEmail, projectName)
        try:
            if response:
                path = app.config["USER_FILES"] + f"{userEmail}\\"
                path = os.path.join(path, projectName)
                shutil.rmtree(path, ignore_errors=True)
                return jsonify(
                    {"status": True, "description": "Project Deleted Successfully"}
                )
            else:
                return jsonify({"status": False, "error": "Delete Operation Failed"})
        except FileNotFoundError as e:
            return jsonify({"status": False, "error": "Delete Operation Failed"})
