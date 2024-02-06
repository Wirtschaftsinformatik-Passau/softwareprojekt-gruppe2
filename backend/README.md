## Readme - Backend
### Ordner Struktur
```
backend/
│
├── backend_tose_venv/ # Virtual environment folder
│ ├── bin/
│ ├── include/
│ ├── lib/
│ └── pyvenv.cfg
│ 
├── tose_backend/ # Alembic folder
│ ├── versions/ # Alembic versions folder
│ ├── env.py 
│ ├── ...
│
├── app/                        # Application source files
│   ├── __init__.py
│   ├── config.py               # Application configuration settings
│   ├── database.py             # Database connection and session management
│   ├── email_sender.py         # Email sending functionality
│   ├── geo_utils.py            # Geolocation utilities
│   ├── hashing.py              # Password hashing utilities
│   ├── logger.py               # Logging configuration
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # SQLAlchemy models
│   ├── oauth.py                # OAuth2 authentication and authorization
│   ├── routers/                # Application routes
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── energieberatende.py
│   │   ├── haushalte.py
│   │   ├── netzbetreiber.py
│   │   ├── solarteure.py
│   │   └── userrs.py
│   ├── schemas.py              # Pydantic models for request and response schemas
│   └── types.py                # Enumerations and custom type definitions
│ 
├── vars/ # Environment variables folder
│   ├── .env                    # Development environment variables
│   └── .env.prod               # Production environment variables
│
├── .gitignore                  # Specifies intentionally untracked files to ignore
├── alembic.ini                 # Alembic configuration file
├── alembic_entrypoint.sh       # Entry point script for running Alembic migrations
├── build_backend.sh            # Script to build and run the Docker container
├── Dockerfile                  # Dockerfile for building the application container
├── Makefile                    # Makefile containing shortcuts for common tasks
├── postgres.sh                 # Script to run a PostgreSQL container
├── README.md                   # Project documentation and setup instructions
├── reqs.txt                    # Python dependencies to be installed
└── setup.sh                    # Script for setting up the development environment

### Wichtiges zum Environment
- /vars/.env datei erstellen im ordner backend
- folgende variablen müssen gesetzt werden:
```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=
ASYNC= 
DEV= 
```
- in [./app/config.py](./app/config.py) seht ihr welche types die Variablen haben müssen


### Wichtiges für die Datenbank
- neues Modell in models.py hinzugefügt?
- Dann aus dem Ordner backend folgendes ausführen:
```
make alembic-revision 
make alembic-upgrade-1
```

- Wenn die Datenbank neu aufgesetzt werden soll:
```
make postgres
make createdb
```

- Wenn die die letze Migration rückgängig gemacht werden soll:
```
make alembic-downgrade-1
```

