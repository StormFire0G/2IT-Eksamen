
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
### 1 Last ned homebrew aller først!
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
### 1.1 Last ned MariaDB
- Last ned og installer MariaDB fra: https://mariadb.org/download/ eller last ned med brew
```bash

brew install mariadb
```
## Start MariaDB som en tjeneste
```bash
mysql.server start
```

## Start MariaDB som en tjeneste
```bash
brew services start mariadb
```

## Start "appen" (bytt root med brukernavn etter vi lager det)
```bash
mariadb -u root
```

# DEL 2: Oppretting av bruker
## Lage bruker (bytt 'brukernavn' og 'passord' med noe enkelt)
```bash
CREATE USER "brukernavn"@"localhost" IDENTIFIED BY "passord";
```

## Gi bruker tilgang til database
```bash
GRANT ALL PRIVILEGES ON *.* TO "brukernavn"@"localhost";
```

## Lagre endringer
```bash
FLUSH PRIVILEGES;
```
