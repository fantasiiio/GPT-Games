from flask import Flask, request
from Database import Database
import jwt
import datetime
import threading

class WebService:
    def __init__(self, user_db, user_collection):
        self.app = Flask(__name__)
        self.database = user_db  # Simulated database
        self.user_collection = user_collection

    def verify_email(self):
        try:
            token = request.args.get('token')
            decoded = self.decode_token(token)        
            user = self.database.get_user_by_valide_token(self.user_collection, token)
            email = user["email"]
            if decoded == f"validation-{email}":
                return True
            else:
                return False
        except Exception as e:
            raise(e)

    def run(self):
        self.app.add_url_rule('/verify', 'verify_email', self.verify_email)
        t = threading.Thread(target=self._run_flask)
        t.start()

    def _run_flask(self):
        self.app.run(debug=False)

    def generate_token(self,email):
        return jwt.encode({'user': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365)}, self.SECRET_KEY)

    def decode_token(self,token):
        try:
            return jwt.decode(token, self.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            return "Token expired"
        except jwt.InvalidTokenError:
            return "Invalid token"        

# Usage
# if __name__ == '__main__':
#     web_service = WebService()

#     # Simulate adding a verification entry
#     web_service.add_verification_entry('xyz123', 'example@example.com')

#     web_service.run()
