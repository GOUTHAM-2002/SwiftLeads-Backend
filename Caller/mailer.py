from extensions import mail
from flask_mail import Message


def send_email(data):
    try:
        msg = Message(
            subject="You have a hotlead",
            recipients=["karthik.pv77@gmail.com,goutham3336@gmail.com"],
            body=data,
        )
        mail.send(msg)
        return True

    except Exception as e:
        print(f"Email sending error: {e}")
        return False
