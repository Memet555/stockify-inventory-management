import sqlite3
from database.db import get_connection, hash_password

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    
    cursor.execute("""
        SELECT username, role 
        FROM users 
        WHERE username = ? AND password_hash = ?
    """, (username, password_hash))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "username": user["username"],
            "role": user["role"]
        }
    return None
