# 🚀 Brzi start - Frontend

## Instalacija i pokretanje

### 1. Instaliraj dependencies (samo prvi put)

```bash
cd frontend
npm install
```

### 2. Pokreni backend

U drugom terminalu, pokreni backend:

```bash
# U root direktorijumu
uvicorn app.main:app --reload
```

### 3. Pokreni frontend

```bash
# U frontend direktorijumu
npm start
```

Frontend će se automatski otvoriti na `http://localhost:3000`

## 📋 Funkcionalnosti

### Za sve korisnike:
- ✅ Pregled prijavljenih pasa
- ✅ Detalji psa
- ✅ Registracija i prijava

### Za prijavljene korisnike:
- ✅ Prijava novog psa
- ✅ Upload fotografija
- ✅ Označavanje psa kao spašenog
- ✅ Ažuriranje profila

### Za administratore:
- ✅ Admin panel
- ✅ Potvrda/odbijanje spašavanja
- ✅ Pregled pasa koji čekaju potvrdu

## 🔧 Konfiguracija

Backend API je automatski konfigurisan u `vite.config.js`:
- Proxy za `/api` pozive ide na `http://localhost:8000`
- Nema potrebe za `.env` fajlom (osim ako ne želiš da promeniš URL)

## 📱 Struktura

- **Home** (`/`) - Početna stranica
- **Login** (`/login`) - Prijava
- **Signup** (`/signup`) - Registracija
- **Dogs List** (`/dogs`) - Lista pasa
- **Dog Detail** (`/dogs/:id`) - Detalji psa
- **Create Dog** (`/dogs/create`) - Prijava novog psa
- **Profile** (`/profile`) - Profil korisnika
- **Admin Panel** (`/admin`) - Admin panel

## 🎨 Stilovi

Aplikacija koristi jednostavan CSS bez eksternih biblioteka. Sve stilove možete prilagoditi u:
- `src/App.css` - Glavni stilovi
- `src/components/Navbar.css` - Navigacija
- Komponentni stilovi su inline ili u App.css

## 🔐 Autentifikacija

Tokeni se automatski čuvaju u `localStorage` i dodaju se u sve API pozive. Refresh token se automatski koristi kada access token istekne.

## ⚡ Vite

Ovaj projekat koristi **Vite** umesto create-react-app:
- ✅ **Brže pokretanje** - instant server start
- ✅ **Brži HMR** - instant hot module replacement  
- ✅ **Jednostavnija konfiguracija**
- ✅ **Manje dependencies**
- ✅ **Nema problema sa webpack konfiguracijom**

## 🐛 Troubleshooting

### CORS greške
Proveri da li je backend pokrenut i da li je CORS konfigurisan za `http://localhost:3000`

### API greške
Proveri da li je backend pokrenut na `http://localhost:8000`

### Slike se ne prikazuju
Proveri da li su slike uploadovane i da li backend servira `/uploads` direktorijum

### Port 3000 je zauzet
Promeni port u `vite.config.js`:
```js
server: {
  port: 3001, // ili neki drugi port
}
```