import os
import hashlib
import re
from db import get_user_by_email, create_user, init_db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))

def make_salt(n: int = 16) -> str:
    return os.urandom(n).hex()

def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def hash_password(password: str, salt: str) -> str:
    # Simple salted SHA-256 per your spec
    return sha256_hex(salt + password)

def try_signup(email: str, name: str, password: str, confirm_password: str):
    init_db()
    if not is_valid_email(email):
        return False, "Please enter a valid email."

    if not name.strip():
        return False, "Name cannot be empty."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if password != confirm_password:
        return False, "Passwords do not match."

    if get_user_by_email(email):
        return False, "An account with this email already exists."

    salt = make_salt()
    pwhash = hash_password(password, salt)
    try:
        create_user(email=email, name=name, salt=salt, password_hash=pwhash)
        return True, "Account created successfully. You can now log in."
    except Exception as e:
        return False, f"Signup failed: {e}"

def try_login(email: str, password: str):
    init_db()
    row = get_user_by_email(email)
    if not row:
        return False, "No account found with that email."
    salt = row["salt"]
    expected = row["password_hash"]
    if hash_password(password, salt) == expected:
        return True, {"id": row["id"], "email": row["email"], "name": row["name"]}
    return False, "Incorrect password."
