## Readme - Backend

Wichtiges für die Datenbank
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

