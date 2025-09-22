from passlib.context import CryptContext

# Initialize Passlib context with bcrypt as the hashing scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password (str): The plaintext password to be hashed.

    Returns:
        str: A secure hashed representation of the password.
    """
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plaintext password against its hashed version.

    Args:
        plain (str): The plaintext password provided by the user.
        hashed (str): The hashed password stored in the database.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain, hashed)
