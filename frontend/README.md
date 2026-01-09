# Dog Rescue Frontend

React frontend aplikacija za Dog Rescue sistem - koristi Vite za brzo pokretanje.

## 🚀 Pokretanje

### 1. Instalacija (samo prvi put)

```bash
cd frontend
npm install
```

### 2. Pokretanje

```bash
npm start
# ili
npm run dev
```

Aplikacija će se automatski otvoriti na: `http://localhost:3000`

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

Backend API je konfigurisan u `vite.config.js`:
- Proxy za `/api` pozive ide na `http://localhost:8000`

## 📦 Build za produkciju

```bash
npm run build
```

Build fajlovi će biti u `dist/` direktorijumu.

## 🎨 Stilovi

Aplikacija koristi jednostavan CSS bez eksternih biblioteka. Sve stilove možete prilagoditi u:
- `src/App.css` - Glavni stilovi
- `src/components/Navbar.css` - Navigacija
- Komponentni stilovi su inline ili u App.css

## 🔐 Autentifikacija

Tokeni se automatski čuvaju u `localStorage` i dodaju se u sve API pozive. Refresh token se automatski koristi kada access token istekne.

## ⚡ Vite

Ovaj projekat koristi [Vite](https://vitejs.dev/) umesto create-react-app:
- **Brže pokretanje** - instant server start
- **Brži HMR** - instant hot module replacement
- **Jednostavnija konfiguracija**
- **Manje dependencies**