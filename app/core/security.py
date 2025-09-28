"""
Utilidades de seguridad para JWT y contraseñas
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar una contraseña en texto plano contra su hash
    """
    # Si es un hash SHA256 (fallback), verificar directamente
    if hashed_password.startswith("sha256:"):
        import hashlib
        expected_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        return f"sha256:{expected_hash}" == hashed_password
    
    # Si es bcrypt, usar pwd_context
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"❌ SECURITY: Error verifying password: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Generar hash de una contraseña
    """
    print(f"🔍 SECURITY: Hashing password: '{password}'")
    print(f"🔍 SECURITY: Password type: {type(password)}")
    print(f"🔍 SECURITY: Password length: {len(password)}")
    print(f"🔍 SECURITY: Password bytes length: {len(password.encode('utf-8'))}")
    
    # Asegurar que la contraseña sea string
    if isinstance(password, bytes):
        password = password.decode('utf-8')
        print(f"🔍 SECURITY: Converted from bytes to string")
    
    # Limpiar la contraseña de caracteres problemáticos
    password = password.strip()
    
    # Verificar que no esté vacía
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Truncar si es necesario (aunque no debería serlo con contraseñas normales)
    if len(password.encode('utf-8')) > 72:
        print(f"⚠️ SECURITY: Password too long, truncating")
        password = password[:72]
    
    try:
        # Intentar con bcrypt primero
        hashed = pwd_context.hash(password)
        print(f"✅ SECURITY: Password hashed successfully with bcrypt")
        return hashed
    except Exception as e:
        print(f"❌ SECURITY: Error with bcrypt: {e}")
        # Fallback a hashlib si bcrypt falla
        import hashlib
        hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
        print(f"✅ SECURITY: Password hashed successfully with SHA256 fallback")
        return f"sha256:{hashed}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear un token JWT de acceso
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Verificar y decodificar un token JWT
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_from_token(token: str) -> str:
    """
    Obtener el email del usuario desde el token
    """
    payload = verify_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    return email
