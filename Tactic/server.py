import socket
import threading
from Connection import Connection, Match



class Server:
    def __init__(self, host, port):
        self.active_matches = []  # List of active matches
        self.waiting_list = []  # List of clients waiting for a match
        self.server_conn = Connection(use_singleton=True, host=host, port=port, is_server=True)
        self.port = port
        self.host = host
        

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

    def handle_client(self, client_conn, client_sock):
        try:
            #client_conn = self.server_conn.sock
            encryption = self.server_conn.encryption
            client_conn.encryption = encryption
            client_conn.initialize_connection(client_sock, self.host, self.port, False)
            client_conn.perform_handshake(is_server=True)

            self.add_to_waiting_list(client_conn)
            self.check_for_possible_matches()


            while True:
                match = client_conn.match
                data = client_conn.receive_data()
                if match:
                    match.broadcast(data, "client_data", exclude_conn=client_conn)
                else:
                    self.check_for_possible_matches()

        except (ConnectionResetError, BrokenPipeError, Exception) as e:
            print(f"An error occurred or client disconnected: {e}")

            if hasattr(client_conn, 'match') and client_conn.match:
                match = client_conn.match

                # Remove the disconnected client from the match
                match.connections.remove(client_conn)

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
