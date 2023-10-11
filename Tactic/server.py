import bcrypt
import jwt
import datetime
import redis
import json
import socket
import threading
from Connection import Connection, Match, Result
from Database import Database
from config import *

class Server:
    def __init__(self, host, port):
        self.database = Database()
        self.database.connect_mongo('BattleGrid')
        self.active_matches = []  # List of active matches
        self.waiting_list = []  # List of clients waiting for a match
        self.server_conn = Connection(use_singleton=True, host=host, port=port, is_server=True)
        self.port = port
        self.host = host
        self.connected_players = [] 
        self.users = self.database.connect_mongo('users')
        self.SECRET_KEY = 'supersecretkey'



    def hash_password(self, plain_password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return hashed

    def check_password(self,plain_password, hashed_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

    def generate_token(self,username):
        return jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365)}, self.SECRET_KEY)

    def decode_token(self,token):
        try:
            return jwt.decode(token, self.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            return "Token expired"
        except jwt.InvalidTokenError:
            return "Invalid token"

    def add_to_waiting_list(self, connection):
        self.waiting_list.append(connection)

    def create_match(self):
        connection1 = self.waiting_list.pop(0)
        connection2 = self.waiting_list.pop(0)
        new_match = Match()
        new_match.add_connection(connection1)
        new_match.add_connection(connection2)
        self.active_matches.append(new_match)
        new_match.broadcast("new_match_created")

    def check_for_possible_matches(self):
        while len(self.waiting_list) >= 2:
            self.create_match()

    def close_all_connections(self):
        for match in self.active_matches:
            for conn in match.connections:
                conn.close()
        for connection in self.waiting_list:
            connection.close()

    # def load_user_from_database(self, guid):
    #     connection = redis.Redis()
    #     connection.ping()

    def handle_client(self, client_conn, client_sock):
        try:
            #client_conn = self.server_conn.sock
            encryption = self.server_conn.encryption
            client_conn.encryption = encryption
            client_conn.initialize_connection(client_sock, self.host, self.port, False)
            client_conn.perform_handshake(is_server=True)

            # players_json = json.dumps(self.connected_players)
            # client_conn.send_command("player_list", data=players_json)

            # matches_json = json.dumps(self.active_matches)
            # client_conn.send_command("match_list", data=matches_json)

            self.add_to_waiting_list(client_conn)
            self.connected_players.append(client_conn)
            self.check_for_possible_matches()



            while True:
                match = client_conn.match
                command_type, receiver, data = client_conn.receive_command()  # Unpack the receiver as well
                if receiver == 'system':
                    if command_type == "register":
                        message = data
                        username = message['username']
                        plain_assword = message['password']
                        email = message['email']
                        hashed_password = self.hash_password(plain_assword)
                        user = self.database.get_user(self.users, username)
                        if user:
                            result = Result('User already exists', "negative")
                            client_conn.send_command('register', data=result.serialize())
                            #client_conn.close()
                            continue
                        else:
                            new_user = {"username": username, "password": hashed_password, "email": email} 
                            self.database.create_user(self.users, new_user)
                            result = Result('User created', "positive")
                            client_conn.send_command('register', data=result.serialize())
                            #client_conn.close()
                            continue
                    elif command_type == "login":
                        message = data
                        username = message['username']
                        plain_assword = message['password']
                        hashed_password = self.hash_password(plain_assword)
                        user = self.database.get_user(self.users, username)
                    elif command_type == "token":    
                        message = data
                        token = message['token']
                        decoded_token = self.decode_token(token)
                        if decoded_token == "Token expired" or decoded_token == "Invalid token":
                            result = Result(decoded_token, "negative")
                            client_conn.send_command('token', data=result.serialize())
                            client_conn.close()
                            continue
                        else:
                            result = Result(decoded_token, "positive")
                            client_conn.send_command('token', data=result.serialize())
                            continue
                        
                    if user :
                        is_valid = self.check_password(plain_assword, user["password"])
                        if is_valid:
                            token = self.generate_token(username)
                            result = Result(token, "positive")
                            client_conn.send_command('login', data=result.serialize())  
                        else:
                            result = Result('Invalid password', "negative")
                            client_conn.send_command('login', data=result.serialize())
                            client_conn.close()
                            continue
                    else:
                        result = Result('Invalid User', "negative")
                        client_conn.send_command('login', data=result.serialize())                                                  

                elif receiver == 'others':
                    match.broadcast(command_type, receiver=receiver, data=data, exclude_conn=client_conn)

                self.check_for_possible_matches()

        except (ConnectionResetError, BrokenPipeError, Exception) as e:
            print(f"An error occurred or client disconnected: {e}")

            if hasattr(client_conn, 'match') and client_conn.match:
                match = client_conn.match

                # Remove the disconnected client from the match
                match.connections.remove(client_conn)
                self.connected_players.remove(client_conn)
                # Put the remaining player back into the waiting list
                for remaining_conn in match.connections:
                    self.add_to_waiting_list(remaining_conn)
                    remaining_conn.match = None  # Reset match for remaining player

                # Remove the now-empty match from active matches
                self.active_matches.remove(match)

                self.check_for_possible_matches()

        finally:
            match = client_conn._instance.match
            if match:
                match.broadcast("end")



    def middleman_server(self):
        print("Waiting for clients...")
        try:
            while True:
                try:
                    client_conn, client_sock = self.server_conn.wait_for_client(1)                    
                    #client_conn.initialize_connection(client_sock, addr[0], self.port, is_server=True)
                except socket.timeout:
                    continue

                client_thread = threading.Thread(target=self.handle_client, args=(client_conn,client_sock,))
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("Server is shutting down...")
        finally:
            self.close_all_connections()
            print("Server socket closed.")

if __name__ == "__main__":
    server_instance = Server(host='127.0.0.1', port=65432)
    server_instance.middleman_server()
