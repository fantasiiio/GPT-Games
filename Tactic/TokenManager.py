import jwt
import datetime

class TokenManager:
    SECRET_KEY = "supersecretkey"  # Make sure this is the same key used in encoding

    @staticmethod
    def generate_token(email, time_delta):
        return jwt.encode({'user': email, 'exp': datetime.datetime.utcnow() + time_delta}, TokenManager.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def decode_token(token):
        try:
            return jwt.decode(token, TokenManager.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError as e:
            print(f"Token expired: {e}")
            return "Token expired"
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {e}")
            return "Invalid token"
        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred"
        
if __name__ == "__main__":
    encoded = TokenManager.generate_token("test", datetime.timedelta(days=1))
    decoded = TokenManager.decode_token(encoded)
    print(decoded)
        
