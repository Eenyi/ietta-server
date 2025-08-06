import json

from flask_mail import Message
from core.config import Config


class Email_Module:
    # def __init__(self, mail: Mail, user) -> None:
    #     self.mail = mail
    #     self.user = user
    @classmethod
    def verification_email(cls, mail, user) -> None:
        msg = Message(
            "Email Verification", sender="ietta.mata@gmail.com", recipients=[user.email]
        )
        verificationLink = f"{Config.BASE_URL}/verification/verify_email?user_name={user.email}&user_id={user.randomId}"
        #                   {_____________________}
        #                               |_____________>  this part of the url
        # I used a button for redirection in the msg.html, we *might* not need this part of the url.
        msg.html = f'<div style="background-color: white; border-radius: 0.5rem; color: black; font-family:Arial, Helvetica, sans-serif; padding: 10px;"><h1 style="text-align: left;"><strong>IETTA here 😊</strong></h1><hr style="border: 1px solid #ff8a1e; width: 300px;margin:0px;" /><p style="font-weight: 600;font-family:Arial, Helvetica, sans-serif;font-size:medium;">Hi <span style="color: #ff8a1e;"> {user.username}</span> ...<br />I am happy to see you signing up for me. <br />Kindly verify your email to start your annotation journey with me.</p><a href="{verificationLink}"><button style="background-color: #ff8a1e;color:black;border:none;border-radius:30px;padding:15px;margin:10px;cursor:pointer;font-weight:600;font-size:16px;" type="submit">Verify Email</button></a><p style="text-align: left;"><span style="color: #ff8a1e;">If you do not recognize this activity simply ignore this mail</span></p><p>Kind Regards, <span style="color: #ff8a1e;"><strong>IETTA™</strong></span></p></div>'
        mail.send(msg)
