import jwt, os
import datetime
from dotenv import load_dotenv

load_dotenv()

jwt_secret_key = os.getenv("JWT_SECRET")


def createJsonWebToken(user_id, email):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }
    access_token = jwt.encode(payload, jwt_secret_key, algorithm="HS256")
    return access_token  # Return just the token string, not a dict


def verifyJsonWebToken(token):
    try:
        payload = jwt.decode(token, jwt_secret_key, algorithms=["HS256"])
        return {"user_id": payload["user_id"], "email": payload["email"]}, 200
    except Exception as e:
        return {"error": "Unauthorised"}, 403