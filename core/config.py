class Config(object):
    USERNAME = "IETTA_DB"
    PASSWORD = "d5KuZB8Uo3imEkVX"
    DB = "IETTA"
    MONGO_URI = f"mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.utpe8ws.mongodb.net/{DB}?retryWrites=true&w=majority"
    BASE_URL = "http://127.0.0.1:5000"
    FRONT_END_URL = "http://localhost:3000/"
    CORS_HEADERS = "Content-Type"
    PAGE_SIZE = 40
    SECRET_KEY = "bratsucks"
    INVISIBILITY = "fc0fhuzaifanwy0talhaB3BsfDz1vzKgpbA2iMQb8L8="


class MailConfig(Config):
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USERNAME = "ietta.mata@gmail.com"
    MAIL_PASSWORD = "spvdnhqvvmdexvfj"
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True


class DirectoryConfig(Config):
    USER_IMAGES = f"UserImages\\"
    USER_FILES = f"UserFiles\\"
    EXPORTED_PROJECTS = f"UserFiles\\exportedProjects\\"
