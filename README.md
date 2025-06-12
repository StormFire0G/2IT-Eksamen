
# 2IT-Eksamen – Nettbutikk for klokker

Dette prosjektet er en fiktiv nettbutikk bygget med Flask, Jinja2 og MariaDB som database. Det er et fullstack webprosjekt med innlogging, adminpanel, handlekurv, sikkerhet, og fiktiv bestillingssystem.

---
# Prosjektets innhold
## Trello

Du kan følge prosjektets planer og oppgaver på Trello: [2IT-Eksamen](https://trello.com/b/SAroMKd1/2it-eksamen)
# Innhold

- `app.py` Hoved koden som utfører flask 
- `templates/` HTML maler som man bruker i stedet for å lage index.html i python/flask
- `static/` CSS og bilder.
- `orders.log` Log for å skjekke om alt funker
- `env/` Virtuelt Python-miljø som er isolert og ikke påvirker selve maskinen din

---
### Kjøre programmet

### 1. Installer MariaDB


- Last ned og installer MariaDB fra: https://mariadb.org/download/
- Start MariaDB-serveren og opprett en database (f.eks. `user_database`).

### 2. Opprett og aktiver virtuelt miljø (virtualenv)

Virtuelt miljø brukes for å isolere prosjektets Python-pakker slik at de ikke konflikter med andre prosjekter eller systempakker.

\`\`\`bash
pip install virtualenv
virtualenv env
source env/bin/activate 
\`\`\`

### 3. Installer Python-pakker

Installer nødvendige pakker for prosjektet

\`\`\`bash
pip install flask flask_sqlalchemy flask_login flask_wtf flask_bcrypt flask_admin pymysql
\`\`\`

### 4. Konfigurer databasen i \`app.py\`

Endre følgende linje i \`app.py\` til din MariaDB-bruker, passord og database:

\`\`\`python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+pymysql://brukernavn:passord@127.0.0.1/user_database'
\`\`\`

### 5. Initialiser databasene

Kjør Flask shell og opprett databasetabellene:

\`\`\`bash
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
\`\`\`

Dette lager tabellene i MariaDB basert på modellene dine (\`User\`, \`Watch\`, \`Order\`, \`CartItem\`).

---

## Bruke applikasjonen

- Start Flask-serveren:

\`\`\`bash
python3 app.py
\`\`\`

- Åpne nettleseren og gå til \`http://localhost:5000\`.
- Registrer ny bruker, logg inn, se dashboard med klokker.
- Legg varer i handlekurv eller bestill direkte.
- Se handlekurv, fjern varer eller fullfør bestilling.
- Admin-brukere kan se bestillingslogg og administrere databasen via Flask-Admin.

---

## Struktur

\`\`\`
2IT-Eksamen/
├── app.py
├── templates/
├── static/
├── env/                 # virtuelt miljø
├── orders.log           # bestillingslogg (valgfri)
├── .gitignore
└── README.md
\`\`\`
