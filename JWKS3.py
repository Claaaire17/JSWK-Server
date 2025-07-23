from flask import Flask, jsonify, request
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from argon2 import PasswordHasher
import base64
import jwt
import datetime
import uuid
import sqlite3
import os

# Creating an instance (app) of Flask class
app = Flask(__name__)

# Database file name
DB_FILE = r"C:\Users\marcl\VSCODE\Project1\CSCE3550_Windows_x86_64 (3)\totally_not_my_privateKey.db"

# AES Encryption functions
def aes_encrypt(data, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    return iv + encryptor.update(data) + encryptor.finalize()

def aes_decrypt(encrypted_data, key):
    iv = encrypted_data[:16]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_data[16:]) + decryptor.finalize()

# Authentication endpoint
@app.route('/auth', methods=['POST'])
def auth():
    ip_address = request.remote_addr
    expired = request.args.get('expired', 'false').lower() == 'true'
    data = request.json
    username = data.get('username')
    password = data.get('password')

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        user = cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()

        if not user:
            return jsonify({"error": "Invalid username or password"}), 401

        user_id, password_hash = user
        ph = PasswordHasher()
        try:
            ph.verify(password_hash, password)
        except:
            return jsonify({"error": "Invalid username or password"}), 401

        # Log authentication request
        cursor.execute("""
            INSERT INTO auth_logs (request_ip, user_id) VALUES (?, ?)
        """, (ip_address, user_id))
        conn.commit()

        # Generate JWT
        exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=-1 if expired else 1)
        token = jwt.encode(
            {"user": username, "exp": int(exp_time.timestamp())},
            os.environ['NOT_MY_KEY'],
            algorithm="HS256"
        )

        response = {
            "token": token,
            "expires_in": -3600 if expired else 3600
        }
        return jsonify(response), 200

# JWKS endpoint
@app.route('/.well-known/jwks.json', methods=['GET'])
def jwks():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        valid_keys = cursor.execute("SELECT key FROM keys WHERE exp > ?", (int(datetime.datetime.utcnow().timestamp()),)).fetchall()

    jwks_keys = []
    for key_row in valid_keys:
        private_key = serialization.load_pem_private_key(
            aes_decrypt(key_row[0], os.environ['NOT_MY_KEY'].encode()),
            password=None
        )
        public_key = private_key.public_key()
        public_numbers = public_key.public_numbers()
        jwks_keys.append({
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "kid": str(uuid.uuid4()),
            "n": base64.urlsafe_b64encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')).decode('utf-8'),
            "e": base64.urlsafe_b64encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, 'big')).decode('utf-8')
        })

    return jsonify({"keys": jwks_keys}), 200

# Initialize the database and run the server
if __name__ == "__main__":
    def init_db():
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS keys(
                    kid INTEGER PRIMARY KEY AUTOINCREMENT,
                    key BLOB NOT NULL,
                    exp INTEGER NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    email TEXT UNIQUE,
                    date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_logs(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_ip TEXT NOT NULL,
                    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)
            conn.commit()

    # Initialize the database
    init_db()

    # Start the server
    app.run(port=8080, debug=True)

