from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hashing:
    """
    Eine Hilfsklasse zur Verschlüsselung und Überprüfung von Passwörtern.

    Methods:
        hash_password(password: str) -> str:
            Verschlüsselt ein Passwort und gibt den verschlüsselten Hash zurück.

        verify_password(plain_password: str, hashed_password: str) -> bool:
            Überprüft, ob ein gegebenes Passwort mit einem verschlüsselten Hash übereinstimmt.

    Example:
        hashing = Hashing()
        hashed_password = hashing.hash_password("geheimes_passwort")
        is_valid = hashing.verify_password("geheimes_passwort", hashed_password)
    """
    @staticmethod
    def hash_password(password):
        """
        Verschlüsselt ein Passwort und gibt den verschlüsselten Hash zurück.

        Args:
            password (str): Das zu verschlüsselnde Passwort.

        Returns:
            str: Der verschlüsselte Hash des Passworts.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """
        Überprüft, ob ein gegebenes Passwort mit einem verschlüsselten Hash übereinstimmt.

        Args:
            plain_password (str): Das zu überprüfende Passwort im Klartext.
            hashed_password (str): Der verschlüsselte Hash des gespeicherten Passworts.

        Returns:
            bool: True, wenn das Passwort korrekt ist, andernfalls False.
        """
        return pwd_context.verify(plain_password, hashed_password)
