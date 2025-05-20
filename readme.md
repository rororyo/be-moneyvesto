`$env:FLASK_APP = "main.py"`

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```
Delete table by commenting out import in __init__.py
```bash
flask db migrate -m "Remove users table" #create migrations
flask db upgrade #apply migrations
```

Reverting a migration
``` bash
flask db downgrade #revert 1 migration
flask db downgrade <revision_hash > #Revert to specific version hash
flask db downgrade base #revert all the way to base
flask db current #View current version hash
flask db history #view migration history

```