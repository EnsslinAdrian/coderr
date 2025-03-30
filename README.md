# 🛠️ Freelance Plattform – Backend API

Dies ist das Backend einer Freelance-Plattform, entwickelt mit **Django** und **Django REST Framework**.

## 🚀 Features

- 🔐 Registrierung & Login mit Token-Authentifizierung  
- 👥 Zwei Benutzerrollen: `customer` und `business`  
- 📦 Erstellung und Verwaltung von Angeboten (`Offers`) durch `business`-User  
- ⭐ Bewertungen & Bestellungen  
- 🔍 Filter-, Such- und Sortierfunktionen für Angebote  
- 🔒 Rollenbasierte Berechtigungen für bestimmte Aktionen  

---

## 📦 Projekt Setup (lokal)

### Voraussetzungen

- Python (Version 3.9 oder höher empfohlen)  
- pip (Python Package Installer)  
- virtualenv *(optional, aber empfohlen)*  
- Git (um das Projekt zu klonen)  
- SQLite (standardmäßig verwendet, keine extra Installation nötig)  

---

### 🔧 Schritt-für-Schritt Anleitung

1. **Repository klonen**
   ```bash
   git clone git@github.com:EnsslinAdrian/coderr.git
   cd coderr
   ```

2. **Virtuelle Umgebung erstellen & aktivieren**
   ```bash
   python -m venv env
   source env/bin/activate  # Linux/macOS
   env\Scripts\activate     # Windows
   ```

3. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Datenbank migrieren**
   ```bash
   python manage.py migrate
   ```

5. **Superuser erstellen (optional, für Admin-Zugang)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Server starten**
   ```bash
   python manage.py runserver
   ```

7. **API aufrufen**
   - API Root: [http://localhost:8000/api/](http://localhost:8000/api/)
   - Admin Panel: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 🔐 Authentifizierung

Die API verwendet **Token-Authentifizierung**.  
Nach dem Login erhält man ein Auth-Token, das bei nachfolgenden Requests im Header übergeben werden muss:

```
Authorization: Token dein_token
```

---

## 🧪 Beispiel-Endpoints

| Methode | Endpoint             | Beschreibung                              |
|---------|----------------------|-------------------------------------------|
| POST    | `/api/registration/` | Registrierung                             |
| POST    | `/api/login/`        | Login (Token erhalten)                    |
| GET     | `/api/offers/`       | Alle Angebote auflisten                   |
| POST    | `/api/offers/`       | Neues Angebot erstellen (nur für business)|
| POST    | `/api/orders/`       | Bestellung aufgeben                       |
| POST    | `/api/reviews/`      | Bewertung abgeben                         |

---

## 🗂️ Projektstruktur

```
freelance-backend/
│
├── auth_app/            # Authentifizierung und Profile
├── coderr_main/         # Hauptprojekt / Settings
├── market_app/          # Angebote / Bestellungen / Reviews
├── requirements.txt     # Python-Abhängigkeiten
├── manage.py
└── README.md
```
