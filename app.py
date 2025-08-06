from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object("core.config.Config")
app.config.from_object("core.config.MailConfig")
app.config.from_object("core.config.DirectoryConfig")

cors = CORS(app)
app.app_context().push()
