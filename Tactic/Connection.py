import requests
import json
import os
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import algorithms, modes
from cryptography.hazmat.backends import default_backend
import socket
import struct
from Encryption import Encryption

class Match:
    def __init__(self):
        self.connections = []

    def add_connection(self, conn):
        self.connections.append(conn)
        conn.match = self

    def broadcast(self, command_type, data=None, exclude_conn=None):
        for conn in self.connections:
            if conn is not exclude_conn:
                conn.send_command(command_type, data=data)

    def get_others(self, exclude_conn):
        others = []
        for other_conn in self.connections:
            if other_conn is not exclude_conn:
                others.append(other_conn)
        return others

class Connection:
    _instance = None

    def __init__(self, sock=None, host=None, port=None, is_server=False, use_singleton=True):
        if use_singleton:
            if Connection._instance is None:
                # If this is the first instance, initialize it
                self.initialize_connection(sock, host, port, is_server)
                Connection._instance = self
            else:
                self.encryption = None
                pass
                # If an instance already exists, update it
                #Connection._instance.initialize_connection(sock, host, port, is_server)
        else:
            # If singleton is not used, just initialize as normal
            self.initialize_connection(sock, host, port, is_server)

    def connect(self):
        self.sock.connect((self.host, self.port))
        self.perform_handshake(is_server=False)

    def initialize_connection(self, sock, host, port, is_server):
        self.is_connected = False
        self.encryption = Encryption()  # Assuming Encryption is some class you've defined
        self.sock = sock
        self.is_server = is_server
        self.match = None
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.is_server:
            self.sock.bind((host, port))
            self.sock.listen()
        elif host and port:
            #self.sock.connect((host, port))
            self.is_connected = True

    def flush_buffer(self):
        try:
            # Set the socket to non-blocking mode
            self.sock.setblocking(0)
            
            while True:
                data = self.sock.recv(1024)
                if not data:
                    break
        except BlockingIOError:
            # No more data to read
            pass
        finally:
            # Set the socket back to blocking mode
            self.sock.setblocking(1)

    def get_country(ip_address):
        try:
            response = requests.get(f"https://ipinfo.io/{ip_address}/json")
            js = response.json()
            country = js.get("country")
            return country
        except Exception as e:
            print(f"Could not get country: {e}")
            return None

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
        print("Connection closed.")
        self.is_connected = False 


    def get_ping_time(self):
        return ping(host)

    def wait_for_client(self, time_out):
        if not self.is_server:
            raise Exception("This method can only be called from a server-side Connection")
        # print("Waiting for a new client...")
        self.sock.settimeout(time_out)
        client_sock, addr = self.sock.accept()
        #self.sock = client_sock
        
        print(f"Accepted connection from {addr}")
        new_conn = Connection(sock=client_sock, is_server=False)
        return new_conn, client_sock
    
    def send_command(self, command_type, **kwargs):
        message = {
            'type': command_type,
            'data': kwargs
        }
        message_str = json.dumps(message)
        self.send_data(message_str)

    def receive_command(self):
        message_str = self.receive_data()
        message = json.loads(message_str)
        command_type = message.get('type')
        data = message.get('data')
        return command_type, data

    def send_data(self, data):
        if self.encryption.aes_key is None:
            raise Exception("AES key not established")

        # Generate a random IV for AES encryption
        iv = os.urandom(16)
        
        cipher = Cipher(
            algorithms.AES(self.encryption.aes_key),
            modes.CFB(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        byte_data = data.encode('utf-8')
        ciphertext = encryptor.update(byte_data) + encryptor.finalize()

        # Send the length of the ciphertext, the IV, and then the ciphertext
        self.sock.sendall(struct.pack('!I', len(ciphertext)) + iv + ciphertext)

    def receive_data(self):
        # Receive the length of the data
        data_len_bytes = self.sock.recv(4)
        if len(data_len_bytes) != 4:
            raise Exception("Failed to receive data length")

        data_len = struct.unpack('!I', data_len_bytes)[0]

        # Receive the IV
        iv = self.sock.recv(16)
        if len(iv) != 16:
            raise Exception("Failed to receive IV")

        # Receive the actual data
        chunks = []
        bytes_received = 0
        while bytes_received < data_len:
            chunk = self.sock.recv(min(data_len - bytes_received, 2048))
            if chunk == b'':
                continue
                #print("Connection closed")
               # raise Exception("Connection closed")
            chunks.append(chunk)
            bytes_received += len(chunk)
        
        ciphertext = b''.join(chunks)

        # Initialize AES Cipher for decryption
        cipher = Cipher(
            algorithms.AES(self.encryption.aes_key),
            modes.CFB(iv),
            backend=default_backend()
        )

        # Decrypt the data
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Convert decrypted bytes to string
        try:
            received_data = plaintext.decode('utf-8')
        except UnicodeDecodeError:
            raise Exception("Failed to decode data")

        return received_data

    def perform_handshake(self, is_server=True):
        
        if is_server:
            # Server sends its public key and receives the client's public key
            serialized_public_key = Encryption.serialize_public_key(self.encryption.public_key)
            self.sock.sendall(struct.pack('!I', len(serialized_public_key)) + serialized_public_key)
            
            other_public_key_len = struct.unpack('!I', self.sock.recv(4))[0]
            other_public_key_bytes = self.sock.recv(other_public_key_len)
            other_public_key = Encryption.deserialize_public_key(other_public_key_bytes)
            
            # Generate and encrypt AES key, then send
            self.encryption.aes_key = Encryption.generate_aes_key()
            encrypted_aes_key = self.encryption.encrypt_with_public_key(other_public_key, self.encryption.aes_key)
            self.sock.sendall(struct.pack('!I', len(encrypted_aes_key)) + encrypted_aes_key)
            
        else:
            # Client receives the server's public key and sends its own public key
            other_public_key_len = struct.unpack('!I', self.sock.recv(4))[0]
            other_public_key_bytes = self.sock.recv(other_public_key_len)
            other_public_key = Encryption.deserialize_public_key(other_public_key_bytes)
            
            serialized_public_key = Encryption.serialize_public_key(self.encryption.public_key)
            self.sock.sendall(struct.pack('!I', len(serialized_public_key)) + serialized_public_key)
            
            # Receive and decrypt AES key
            encrypted_aes_key_len = struct.unpack('!I', self.sock.recv(4))[0]
            encrypted_aes_key = self.sock.recv(encrypted_aes_key_len)
            self.encryption.aes_key = self.encryption.decrypt_with_private_key(encrypted_aes_key)
