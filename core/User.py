import random


class User:
    def __init__(self, username, password, email, img):
        self.username = username
        self.password = password
        self.email = email
        self.img = img
        self.verfiedStatus = False
        self.randomId = random.randint(0, 10)
        self.Projects = []
