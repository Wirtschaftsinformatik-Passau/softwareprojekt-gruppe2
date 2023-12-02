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
├── app/ # Source code folder
│ ├── main.py # Main application file
│ ├── routes/ # Routes of application file
│ └── ...
│ 
├── vars/ # Environment variables folder
│ ├── .env # Environment variables file
│
└── reqs.txt # Requirements file
└── alembic.ini # Alembic configuration file (Here the database connection is configured)
└── setup.sh # Setup file
└── Makefile # Makefile
```

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

