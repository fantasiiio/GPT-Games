from flask import Flask
from werkzeug.serving import make_server
import threading
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
        self.stop_event = threading.Event()  # Add this line

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
        
    def hello(self):
        return "Hello, World!"

    def run(self):
        self.app.add_url_rule('/hello', 'hello', self.hello)
        t = threading.Thread(target=self._run_flask)
        t.daemon = True  # Makes thread exit when main program exits
        t.start()

    def _run_flask(self):
        self.server = make_server('127.0.0.1', 5000, self.app)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown_signal = True

if __name__ == '__main__':
    web_service = WebApi()
    web_service.run()

    try:
        while True:
            pass  # Simulating main loop, replace with actual server logic
    except KeyboardInterrupt:
        print("Ctrl+C detected. Shutting down Flask server.")
        web_service.stop()