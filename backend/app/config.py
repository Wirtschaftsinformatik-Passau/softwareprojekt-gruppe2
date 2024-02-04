from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Klasse zum Laden und Verwalten von Konfigurationseinstellungen aus einer .env-Datei oder anderen Quellen.

    Die Konfigurationseinstellungen werden aus einer .env-Datei mit Standardwerten geladen, falls sie dort nicht gefunden werden.
    Diese Klasse ermöglicht den Zugriff auf die Konfigurationseinstellungen als Klassenattribute.

    Attributes:
        POSTGRES_USER (str): Benutzername für die PostgreSQL-Datenbank.
        POSTGRES_PASSWORD (str): Passwort für die PostgreSQL-Datenbank.
        POSTGRES_DB (str): Name der PostgreSQL-Datenbank.
        POSTGRES_HOST (str): Hostname oder IP-Adresse des PostgreSQL-Servers.
        POSTGRES_PORT (int): Portnummer des PostgreSQL-Servers.
        ASYNC (bool): True, wenn die Anwendung asynchron arbeitet, andernfalls False.
        DEV (bool): True, wenn die Anwendung im Entwicklungsmodus ausgeführt wird, andernfalls False.
        ALGORITHM (str): Das zu verwendende Verschlüsselungsalgorithmus für JWT-Token.
        SECRET_KEY (str): Geheimer Schlüssel für die Erstellung und Überprüfung von JWT-Token.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Gültigkeitsdauer eines JWT-Token in Minuten.
        OS (str): Das Betriebssystem, auf dem die Anwendung ausgeführt wird.
        SMTP_SERVER (str): Der SMTP-Server für E-Mail-Versand.
        SMTP_PORT (int): Der SMTP-Port für den E-Mail-Versand.
        USERNAME (str): Der Benutzername für den SMTP-Server.
        PASSWORD (str): Das Passwort für den SMTP-Server.

    Example:
        settings = Settings()
        print(settings.POSTGRES_USER)  # Gibt den PostgreSQL-Benutzernamen aus der Konfiguration zurück.
    """
    model_config = SettingsConfigDict(env_file='./vars/.env')
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    ASYNC: bool
    DEV: bool
    ALGORITHM: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OS: str
    SMTP_SERVER: str
    SMTP_PORT: int
    USERNAME: str
    PASSWORD: str


settings = Settings()
