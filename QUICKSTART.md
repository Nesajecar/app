# 🚀 Brzi start

## 1. Instalacija

```bash
pip install -r requirements.txt
```

## 2. Pokretanje

### Windows:
```bash
start.bat
```

### Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

### Manualno:
```bash
uvicorn app.main:app --reload
```

## 3. Testiranje

Otvori u browseru: http://localhost:8000/api/docs

## 4. Prvi koraci

1. **Registruj se**: `POST /api/auth/signup`
   ```json
   {
     "email": "test@example.com",
     "password": "test123",
     "full_name": "Test User"
   }
   ```

2. **Prijavi se**: `POST /api/auth/login`
   ```json
   {
     "email": "test@example.com",
     "password": "test123"
   }
   ```
   Sačuvaj `access_token` i `refresh_token`

3. **Prijavi psa**: `POST /api/dogs`
   ```json
   {
     "title": "Pas na ulici",
     "description": "Vidjen pas u centru grada",
     "latitude": 44.7866,
     "longitude": 20.4489
   }
   ```

4. **Upload slike**: `POST /api/dogs/{id}/images`
   - Koristi `multipart/form-data`
   - Polje: `file`

## 5. Admin panel

Za kreiranje admin korisnika, direktno u bazi postavi `is_admin = True` za željenog korisnika.

Ili koristi endpoint (ako već imaš admina):
```
PATCH /api/admin/users/{id}/role?is_admin=true
```
