import json
import linecache
import math
import os

from flask import current_app as app
from flask import jsonify, request
from flask_restx import Namespace, Resource
from werkzeug.utils import secure_filename

from core.PDF_Extraction import pdfParser
from core.pyjwt import auth
from Models.DB_Context import DbContext

api = Namespace(
    name="files",
    description="Operations related to user files management like uploading,"
    "annotation handling, pdf parsing and pagination",
)


@api.route("/file")
class File(Resource):
    @auth
    def post(self, userEmail: str):
        # Checking if the file is only PDF or TXT, also If the entered name is not empty spaces.
        file_extension = os.path.splitext(request.files["fileToUpload"].filename)[
            1
        ]  # Gets the extension of the file.
        if [".txt", ".pdf"].count(file_extension) == 0:
            return jsonify(
                {"status": False, "error": "Uploaded File Type Invalid"}
            )  # return False if file is not PDF or TXT.
        if request.form.get("fileName").isspace():
            return jsonify(
                {"status": False, "error": "Empty Spaces are not Allowed"}
            )  # return False if filename is empty spaces.

        # Project Name to check with which project the file is associated
        projectName = request.form.get("projectName")

        # If file is PDF, setting flag to trigger PDF_Extraction Module
        if os.path.splitext(request.files["fileToUpload"].filename)[1] == ".pdf":
            isPDF = True
        else:
            isPDF = False

        # Formulating the name to save it in UserFiles and Database.
        request.files["fileToUpload"].filename = (
            request.form.get("fileName") + ".txt"
        )  # replacing the original name with whats given by user
        fileToSave = (
            app.config["USER_FILES"]
            + f"{userEmail}"
            + f"\\{projectName}\\"
            + secure_filename(request.files["fileToUpload"].filename)
        )  # making the name safe to be stored in directory

        # See in DBContext.py about how response is formed
        response = DbContext.uploadFile(
            userEmail,
            projectName,
            secure_filename(request.files["fileToUpload"].filename),
        )

        # Only when the file was placed correctly in database, it will be saved in the folder
        if response["status"] == True:
            os.makedirs(
                app.config["USER_FILES"] + f"{userEmail}" + f"\\{projectName}\\",
                exist_ok=True,
            )
            if isPDF:
                savedPdfFile = (
                    app.config["USER_FILES"]
                    + f"{userEmail}"
                    + f"\\{projectName}\\"
                    + secure_filename(request.form.get("fileName") + ".pdf")
                )
                request.files["fileToUpload"].save(savedPdfFile)
                filename = secure_filename(request.form.get("fileName") + ".pdf")
                storageLocation = (
                    app.config["USER_FILES"] + f"{userEmail}" + f"\\{projectName}\\"
                )
                _pdfParser = pdfParser(filename, storageLocation)
                parsed = _pdfParser.convertToText()
                if not parsed:
                    return jsonify({"status": False, "error": "PDF Extraction Failed"})
                with open(fileToSave, "r", encoding="utf-8") as fp:
                    c_generator = _pdfParser.countLines(fp.read)
                    # count each \n
                    count = sum(buffer.count("\n") for buffer in c_generator)
                    metaData = {"totalLines": count + 1}
                    with open(
                        storageLocation
                        + secure_filename(request.form.get("fileName") + ".txt")
                        + "-metaData.json",
                        "w",
                        encoding="utf-8",
                    ) as file:
                        file.write(json.dumps(metaData))
            else:
                request.files["fileToUpload"].save(fileToSave)
                _pdfParser = pdfParser(
                    secure_filename(request.files["fileToUpload"].filename),
                    app.config["USER_FILES"] + f"{userEmail}" + f"\\{projectName}\\",
                )
                with open(fileToSave, "r", encoding="utf-8") as fp:
                    c_generator = _pdfParser.countLines(fp.read)
                    # count each \n
                    count = sum(buffer.count("\n") for buffer in c_generator)
                    metaData = {"totalLines": count + 1}
                    with open(
                        fileToSave + "-metaData.json", "w", encoding="utf-8"
                    ) as file:
                        file.write(json.dumps(metaData))
            _pdfParser = pdfParser(
                secure_filename(request.files["fileToUpload"].filename),
                app.config["USER_FILES"] + f"{userEmail}" + f"\\{projectName}\\",
            )
            annotationFileCreated = _pdfParser.createAnnotationFile(
                app.config["USER_FILES"]
                + f"{userEmail}"
                + f"\\{projectName}\\"
                + secure_filename(request.files["fileToUpload"].filename)
            )
            if not annotationFileCreated:
                return jsonify({"status": False, "msg": "Failed"})
        return jsonify(response)

    @auth
    def get(self, userEmail: str):
        filePath = (
            app.config["USER_FILES"]
            + f"{userEmail}"
            + f'\\{request.args.get("projectName")}'
            + f'\\{request.args.get("fileName")}'
        )
        pageNumber = int(request.args.get("pageNumber"))
        if pageNumber < 0:
            return jsonify({"status": False, "error": "Invalid Page Number"})
        try:
            startLine, lastLine = (pageNumber * app.config["PAGE_SIZE"]) + 1, (
                (pageNumber + 1) * app.config["PAGE_SIZE"]
            ) + 1
            lines, tagLines = [], []
            with open(filePath + "-metaData.json") as linesJson:
                totalLines = json.load(linesJson)["totalLines"]
                totalPages = totalLines / app.config["PAGE_SIZE"]
            linecache.checkcache(filename=r"" + filePath[: len(filePath) - 3] + "ietta")
            for i in range(startLine, lastLine):
                tag = linecache.getline(
                    r"" + filePath[: len(filePath) - 3] + "ietta", i
                ).strip()
                line = linecache.getline(r"" + filePath, i).strip()
                lines.append(line), tagLines.append(tag)
            return jsonify(
                {
                    "success": {"lines": lines, "tagLines": tagLines},
                    "totalPages": math.ceil(totalPages),
                }
            )
        except FileNotFoundError as e:
            return jsonify({"status": False, "error": "File Not Found"})


@api.route("/update_annotations")
class UpdateAnnotations(Resource):
    @auth
    def post(self, userEmail: str):
        projectName = request.args.get("projectName")
        fileName, pageNumber = request.args.get("fileName"), int(
            request.args.get("pageNumber")
        )
        annotationToSave = request.json["updatedAnnotations"]
        startLine = (pageNumber * app.config["PAGE_SIZE"]) + 1
        filePath = (
            app.config["USER_FILES"]
            + f"{userEmail}"
            + f"\\{projectName}"
            + f"\\{fileName}"
        )
        with open(
            filePath[: len(filePath) - 3] + "ietta", "r", encoding="utf-8"
        ) as file:
            prevAnnotation = file.readlines()
        totalLines = len(prevAnnotation)
        for line in annotationToSave:
            if startLine > totalLines:
                break
            prevAnnotation[startLine - 1] = line + "\n"
            startLine += 1
        with open(
            filePath[: len(filePath) - 3] + "ietta", "w", encoding="utf-8"
        ) as file:
            file.writelines(prevAnnotation)
        return True
