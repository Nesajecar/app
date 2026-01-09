# Dog Rescue API

Sistem za prijavu izgubljenih i nađenih pasa sa potvrdom spašavanja - FastAPI backend aplikacija.

## 📋 Opis

Aplikacija omogućava korisnicima da:
- Prijave psa uočenog na ulici
- Dodaju opis i fotografije
- Postave lokaciju
- Prijave da su psa spasili
- Administrator potvrđuje spašavanje

## 🚀 Brzo pokretanje

### 1. Instalacija

```bash
# Kloniraj repo
git clone <repo-url>
cd dog-rescue-api

# Instaliraj dependencies
pip install -r requirements.txt
```

### 2. Pokretanje

```bash
# Pokreni aplikaciju
uvicorn app.main:app --reload
```

Aplikacija će biti dostupna na: `http://localhost:8000`

### 3. Dokumentacija

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 📁 Struktura projekta

```
app/
├── main.py                 # FastAPI aplikacija
├── core/
│   ├── config.py          # Konfiguracija
│   └── security.py        # JWT, password hashing
├── db/
│   ├── database.py        # SQLAlchemy setup
│   └── models.py          # Database modeli
├── schemas/
│   ├── user.py           # Pydantic schemas za User
│   └── dog.py            # Pydantic schemas za Dog
└── api/
    ├── deps.py           # Dependencies (auth)
    └── api_v1/
        ├── api.py        # Router setup
        └── endpoints/
            ├── auth.py   # Autentifikacija
            ├── dogs.py   # Dog endpoints
            └── admin.py  # Admin endpoints
```

## 🔑 API Endpoints

### Autentifikacija

| Metod | Putanja | Opis |
|-------|---------|------|
| POST | `/api/auth/signup` | Registracija |
| POST | `/api/auth/login` | Prijava, vraća access token |
| POST | `/api/auth/refresh` | Osvežavanje access tokena |
| POST | `/api/auth/logout` | Poništavanje refresh tokena |
| GET | `/api/auth/me` | Informacije o trenutnom korisniku |
| PATCH | `/api/users/me` | Ažuriranje profila |
| DELETE | `/api/users/me` | Brisanje ličnog naloga |

### Psi

| Metod | Putanja | Opis |
|-------|---------|------|
| GET | `/api/dogs` | Lista pasa (sa filterima) |
| GET | `/api/dogs/{id}` | Detalji psa |
| POST | `/api/dogs` | Unos nove prijave psa |
| PUT | `/api/dogs/{id}` | Izmena (samo autor ili admin) |
| DELETE | `/api/dogs/{id}` | Brisanje (admin ili autor) |
| POST | `/api/dogs/{id}/images` | Upload slike (multipart) |
| GET | `/api/dogs/{id}/images` | Lista fotografija psa |
| POST | `/api/dogs/{id}/picked-up` | Označavanje kao spašenog |

### Admin

| Metod | Putanja | Opis |
|-------|---------|------|
| GET | `/api/admin/dogs/pending` | Lista pasa koji čekaju potvrdu |
| POST | `/api/admin/dogs/{id}/confirm` | Potvrda spašavanja |
| POST | `/api/admin/dogs/{id}/reject` | Odbijanje spašavanja |
| PATCH | `/api/admin/users/{id}/role` | Dodela admin prava |
| DELETE | `/api/admin/dog-images/{image_id}` | Brisanje slike |

## 🔐 Statusni ciklus psa

| Status | Značenje | Ko može postaviti |
|--------|----------|-------------------|
| `reported` | Pas je viđen i prijavljen | Reporter / svaki korisnik |
| `pending_admin` | Korisnik je prijavio da je spasio psa, čeka potvrdu | Korisnik |
| `confirmed` | Administrator potvrdio da je pas stvarno spašen | Admin |
| `removed` | Prijava obrisana (lažno, nejasno, duplikat) | Admin |

## 🗄️ Baza podataka

Aplikacija koristi **SQLite** za jednostavno pokretanje i razvoj.

Baza se automatski kreira pri prvom pokretanju aplikacije u fajlu `dog_rescue.db`.

### Tabele

- **users** - Korisnici sistema
- **dogs** - Prijavljeni psi
- **dog_images** - Slike pasa

## 🔒 Bezbednost

- **Lozinke**: Hashirane sa bcrypt
- **JWT tokeni**: Access token (15 min), Refresh token (7 dana)
- **File upload**: Ograničena veličina (5MB), dozvoljeni tipovi (jpg, png, jpeg)
- **Geolokacija**: Validacija (lat ∈ [-90,90], lon ∈ [-180,180])
- **Autentifikacija**: JWT Bearer token u Authorization header

## 📸 Upload slika

Slike se čuvaju lokalno u `uploads/` direktorijumu.

- Maksimalna veličina: 5MB
- Dozvoljeni tipovi: jpg, jpeg, png
- Pristup: `/uploads/{filename}`

## 🌐 Frontend

Kompletan React frontend je dostupan u `frontend/` direktorijumu.

### Pokretanje frontenda

```bash
cd frontend
npm install
npm start
```

Frontend će biti dostupan na: `http://localhost:3000`

Za više informacija, pogledaj [FRONTEND_SETUP.md](FRONTEND_SETUP.md) ili [frontend/README.md](frontend/README.md)

### Frontend funkcionalnosti

- ✅ Registracija i prijava
- ✅ Pregled prijavljenih pasa
- ✅ Prijava novog psa sa geolokacijom
- ✅ Upload fotografija
- ✅ Označavanje psa kao spašenog
- ✅ Admin panel za potvrdu spašavanja
- ✅ Profil korisnika

### Primer React poziva

```javascript
// Login
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { access_token, refresh_token } = await response.json();

// Sa autentifikacijom
const response = await fetch('/api/dogs', {
  headers: { 
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  }
});

// Upload slike
const formData = new FormData();
formData.append('file', file);
const response = await fetch(`/api/dogs/${dogId}/images`, {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${access_token}`
  },
  body: formData
});
```

## ⚙️ Konfiguracija

Kreiraj `.env` fajl (opciono):

```env
# Database
DATABASE_URL=sqlite:///./dog_rescue.db

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# File upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880
ALLOWED_EXTENSIONS=jpg,jpeg,png

# App
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## 🧪 Testiranje

```bash
# Pokreni aplikaciju
uvicorn app.main:app --reload

# Testiraj u Swagger UI
# Otvori: http://localhost:8000/api/docs
```

## 📝 Napomene

- SQLite je dovoljan za MVP verziju
- Za produkciju sa većim opterećenjem, razmotri PostgreSQL
- Refresh tokeni se trenutno ne čuvaju u bazi (za produkciju dodati tabelu)
- HTTPS je obavezan za produkciju

## 🚀 Produkcija

Za produkciju:
1. Promeni `DATABASE_URL` na PostgreSQL
2. Postavi siguran `JWT_SECRET_KEY`
3. Omogući HTTPS
4. Konfiguriši CORS origins
5. Dodaj rate limiting
6. Implementiraj čuvanje refresh tokena u bazi

## 📄 Licenca

MIT
