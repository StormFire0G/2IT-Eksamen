
# 2IT-Eksamen – Nettbutikk for klokker

Dette prosjektet er en fiktiv nettbutikk bygget med Flask, Jinja2 og MariaDB som database. Det er et fullstack webprosjekt med innlogging, adminpanel, handlekurv, sikkerhet, og fiktiv bestillingssystem.

---
# Prosjektets innhold
## Trello

Du kan følge prosjektets planer og oppgaver på Trello: [2IT-Eksamen](https://trello.com/b/SAroMKd1/2it-eksamen)
## Innhold

- `app.py` Hoved koden som utfører flask 
- `templates/` HTML maler som man bruker i stedet for å lage index.html i python/flask
- `static/` CSS og bilder.
- `orders.log` Log for å skjekke om alt funker
- `env/` Virtuelt Python-miljø som er isolert og ikke påvirker selve maskinen din

---
# Hvordan starte prosjektet?
## Last ned nødvendige pakker for databasen!
### 1 Last ned homebrew aller først!
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
### 2 Last ned MariaDB
- Last ned og installer MariaDB fra: https://mariadb.org/download/ eller last ned med brew
```bash

brew install mariadb
```
### 3 Start MariaDB som en tjeneste
```bash
mysql.server start
```

### 4 Start MariaDB som en tjeneste
```bash
brew services start mariadb
```

### 5 Start "appen" (bytt root med brukernavn etter vi lager det)
```bash
mariadb -u root
```
### 6 Lage bruker (bytt 'brukernavn' og 'passord' med noe enkelt)
```bash
CREATE USER "brukernavn"@"localhost" IDENTIFIED BY "passord";
```

### 7 Gi bruker tilgang til database
```bash
GRANT ALL PRIVILEGES ON *.* TO "brukernavn"@"localhost";
```

### 8 Lagre endringer
```bash
FLUSH PRIVILEGES;
```
## Lage virituelt miljø for å gjøre prosjektet sine pakker sikkre, og beskytte maskinen hvis feil dukker opp

### Laste ned med pip
```bash 
pip3 / pip install virtualenv
```

### Lage et virituelt miljø på prosjektet
```bash
virtualenv env
```
### Aktivere miljøet
```bash
source env/bin/activate
```

### Installer nødvendige pakker til prosjektet
```bash
pip install Flask Flask_SQLAlchemy Flask_Login Flask_WTF WTForms Flask_Bcrypt Flask_Admin pymysql
```
### Importere database moddelene i MariaDB
```bash
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

### Kjøre programmet 
```bash
python3 app.py
```