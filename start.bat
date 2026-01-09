@echo off
echo 🐕 Dog Rescue API - Pokretanje...

REM Kreiraj uploads direktorijum
if not exist uploads mkdir uploads

REM Pokreni aplikaciju
echo 🚀 Pokretanje FastAPI servera...
echo.
echo ✅ API će biti dostupan na: http://localhost:8000
echo 📚 Dokumentacija: http://localhost:8000/api/docs
echo.
uvicorn app.main:app --reload
