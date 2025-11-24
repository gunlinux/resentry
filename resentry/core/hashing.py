from dataclasses import dataclass
import bcrypt


@dataclass
class Hasher:
    salt: bytes

    def _generate_hash(self, plain_password: str) -> bytes:
        return bcrypt.hashpw(plain_password.encode("utf-8"), self.salt)

    def generate_hash(self, plain_password: str) -> str:
        return self._generate_hash(plain_password).decode("utf-8")

    def verify_password(self, plain_password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return self.generate_hash(plain_password) == hashed
