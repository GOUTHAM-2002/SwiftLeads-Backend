from Auth.jwt import createJsonWebToken
from Supabase.utils import supabase


def loginProcess(email, password):
    try:
        # Authenticate with Supabase
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        if response.user:
            user_id = response.user.id
            # Create JWT token
            jwt_token = createJsonWebToken(user_id, email)
            return {"jwt_token": jwt_token}, 200

        else:
            return {"error": "Invalid credentials"}, 401

    except Exception as e:
        print(f"Login error: {str(e)}")
        return {"error": str(e)}, 500
