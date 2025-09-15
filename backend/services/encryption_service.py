from cryptography.fernet import Fernet
import base64
import hashlib
import os

class EncryptionService:
    @staticmethod
    def generate_key_from_password(password: str, salt: bytes = None) -> bytes:
        """Generate encryption key from password"""
        if salt is None:
            salt = os.urandom(16)
        
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return base64.urlsafe_b64encode(key), salt
    
    @staticmethod
    def encrypt_data(data: str, password: str) -> dict:
        """Encrypt data with password"""
        key, salt = EncryptionService.generate_key_from_password(password)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())
        
        return {
            'encrypted_data': base64.b64encode(encrypted_data).decode(),
            'salt': base64.b64encode(salt).decode()
        }
    
    @staticmethod
    def decrypt_data(encrypted_data: str, salt: str, password: str) -> str:
        """Decrypt data with password"""
        try:
            salt_bytes = base64.b64decode(salt.encode())
            key, _ = EncryptionService.generate_key_from_password(password, salt_bytes)
            fernet = Fernet(key)
            
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception:
            raise ValueError("Invalid password or corrupted data")