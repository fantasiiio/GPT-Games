from ping3 import ping, verbose_ping
import requests
import json
import os
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import algorithms, modes
from cryptography.hazmat.backends import default_backend
import socket
import struct
from Encryption import Encryption

class Result:
    def __init__(self, message, success):
        self.message = message
        self.success = success

    def serialize(self):
        return json.dumps(self.to_dict)

    @property
    def to_dict(self):
        return {
            "message": self.message,
            "success": self.success
        }   
class Match:
    def __init__(self):
        self.connections = []

    def add_connection(self, conn):
        self.connections.append(conn)
        conn.match = self

    def broadcast(self, command_type, data=None, exclude_conn=None, receiver="others"):
        for conn in self.connections:
            if conn is not exclude_conn:
                conn.send_command(command_type, receiver = receiver, data=data)

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

    def connect_to_server(self):
        self.sock.connect((self.host, self.port))
        self.perform_handshake(is_server=False)
        self.is_connected = True
        connection_test = self.connection_test()

    def initialize_connection(self, sock, host, port, is_server):
        self.host = host
        self.port = port
        if not is_server:
            country = self.get_country(self.host)
            self.country = "CA" if country is None else country
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

    def get_country(self, ip_address):
        try:
            response = requests.get(ip_address)
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


    def get_ping_time(self, host):
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
        new_conn.host = addr[0]
        return new_conn, client_sock
    
    def send_command(self, command_type, receiver="others", data=None):
        message = {
            'type': command_type,
            'receiver': receiver,  # Include the receiver in the message
            'data': data
        }
        message_str = json.dumps(message)
        self.send_data(message_str)

    def receive_command(self):
        try:
            message_str = self.receive_data()
            message = json.loads(message_str)
            command_type = message.get('type')
            receiver = message.get('receiver', "others")  # Default to "others" if receiver is not specified
            data = message.get('data')
            return command_type, receiver, data
        except Exception as e:
            print(f"Failed to receive command")
            raise e

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
        print(f"Data to send: {data}")
        byte_data = data.encode('utf-8')
        ciphertext = encryptor.update(byte_data) + encryptor.finalize()

        # Prepare the complete message to send
        # Send the length of the ciphertext, the IV, and then the ciphertext
        complete_message = struct.pack('!I', len(ciphertext)) + iv + ciphertext
        bytes_sent = self.sock.sendall(complete_message)
        
        if bytes_sent is not None and bytes_sent < len(complete_message):
            print(f"Warning: Only {bytes_sent} out of {len(complete_message)} bytes were sent.")
        print(f"Sent {bytes_sent} bytes")

    def connection_test(self):
        try:
            self.sock.send(b"")
            return True
        except socket.error:
            print("Socket is not connected")
            return False

    def receive_data(self):
        try:
            print("Receiving data...")
            # Receive the length of the data
            data_len_bytes = self.sock.recv(4)
            if len(data_len_bytes) != 4:
                raise Exception("Failed to receive data length")
            print(f"Data Length Bytes: {data_len_bytes}")
            data_len = struct.unpack('!I', data_len_bytes)[0]

            # Receive the IV
            iv = self.sock.recv(16)
            if len(iv) != 16:
                raise Exception("Failed to receive IV")
            print(f"IV: {iv}")
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

            # Before trying to decode, log the essential components
            print(f"Data Length: {data_len}")
            print(f"IV: {iv}")
            print(f"Received Ciphertext: {ciphertext}")
            print(f"Decrypted Plaintext: {plaintext}")

            try:
                received_data = plaintext.decode('utf-8')
                print(f"Received data: {received_data}")
            except UnicodeDecodeError:
                print(f"Failed to decode data: {plaintext}")
                raise Exception("Failed to decode data")

            return received_data
        except Exception as e:
            print(f"Failed to receive data: {e}")
            raise e
    

    def perform_handshake(self, is_server=True):
        print("Performing handshake...")
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
            # After AES key is generated or decrypted
            print(f"Generated/Decrypted AES Key: {self.encryption.aes_key.hex()}")
            # Before sending and after receiving encrypted AES key
            print(f"Encrypted AES Key Length Sent: {len(encrypted_aes_key)}")
            print(f"Encrypted AES Key Sent: {encrypted_aes_key.hex()}")            
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
            # After AES key is generated or decrypted
            print(f"Generated/Decrypted AES Key: {self.encryption.aes_key.hex()}")
            # Before sending and after receiving encrypted AES key
            print(f"Encrypted AES Key Length Received: {len(encrypted_aes_key)}")
            print(f"Encrypted AES Key Received: {encrypted_aes_key.hex()}")               
            
        print("Handshake complete")