from flask_restx import Api

from .accounts import api as accounts
from .files import api as files
from .profileInfo import api as profileInfo
from .projects import api as projects
from .verification import api as verification

api = Api(
    title="IETTA Server APIs", version="1.0", description="dont know what to write here"
)

api.add_namespace(accounts)
api.add_namespace(projects)
api.add_namespace(files)
api.add_namespace(profileInfo)
api.add_namespace(verification)
