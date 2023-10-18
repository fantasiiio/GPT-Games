
from TokenManager import TokenManager
from flask import Flask, request, render_template
from Database import Database
import jwt
import datetime
import threading
from Connection import Result
import json

class WebApi:
    def __init__(self, user_db, user_collection):
        self.app = Flask(__name__)
        self.database = user_db  # Simulated database
        self.user_collection = user_collection

    def verify_email(self):
        try:
            token = request.args.get('token')
            decoded = TokenManager.decode_token(token)        
            user = self.database.get_user_by_valide_token(self.user_collection, token)
            if decoded["user"] == user["guid"]:
                self.database.set_user_as_verified(self.user_collection, user["guid"])
                return render_template("verification_success.html")
            else:
                return render_template("verification_fail.html")
        except Exception as e:
            return render_template("verification_fail.html")

    def run(self):
        self.app.add_url_rule('/verify', 'verify_email', self.verify_email)
        t = threading.Thread(target=self._run_flask)
        t.start()

    def _run_flask(self):
        self.app.run(debug=False)    

# Usage
# if __name__ == '__main__':
#     web_service = WebApi()

#     # Simulate adding a verification entry
#     web_service.add_verification_entry('xyz123', 'example@example.com')

#     web_service.run()
