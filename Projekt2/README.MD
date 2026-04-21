# Dokumentacja Projektu - PyGit

**Autor:** Ignacy Mróz  
**Temat projektu:** System zarządzania lokalnymi repozytoriami Git  
**Data oddania:** 22.04.2026  

---

## 1. Opis projektu
PyGit to aplikacja webowa służąca do zarządzania lokalnymi repozytoriami Git. Program pozwala na tworzenie nowych projektów, wersjonowanie plików, przeglądanie struktury katalogów oraz śledzenie historii zmian (commitów). Każdy użytkownik posiada wydzieloną przestrzeń roboczą, co zapewnia izolację danych.

## 2. Funkcjonalności systemu
* **Zarządzanie użytkownikami:** Rejestracja i logowanie z bezpiecznym haszowaniem haseł.
* **CRUD Repozytoriów:** Tworzenie, wyświetlanie listy, zmiana nazwy oraz usuwanie repozytoriów z dysku.
* **Eksplorator plików:** Przeglądanie zawartości repozytoriów z obsługą podfolderów i nawigacją okruszkową (breadcrumbs).
* **Integracja z Git:** Automatyczna inicjalizacja repozytoriów (`git init`) oraz wykonywanie commitów przy wgrywaniu plików.
* **Zarządzanie plikami:** Przesyłanie pojedynczych plików oraz całych struktur katalogów do wybranego repozytorium.
* **Historia zmian:** Wyświetlanie listy ostatnich commitów wraz z ich autorami, datami i skróconymi hashami.
* **Eksport danych:** Pobieranie całej zawartości repozytorium w formie spakowanego archiwum ZIP.

## 3. Struktura technologiczna
Projekt został zrealizowany w architekturze modułowej z wykorzystaniem Blueprintów, co pozwala na logiczny podział aplikacji na moduły autoryzacji (`auth`) oraz zarządzania zasobami (`repos`).

### Wykorzystane biblioteki (zgodnie z requirements.txt):
* **Framework:** Flask 3.1.3
* **Baza danych:** Flask-SQLAlchemy 3.1.1 (SQLite)
* **Autoryzacja:** Flask-Login 0.6.3
* **Integracja Git:** GitPython 3.1.46
* **Serwer WSGI:** Werkzeug 3.1.8
* **Silnik szablonów:** Jinja2 3.1.6
* **Frontend:** Bootstrap 5.3.0 (via CDN)

## 4. Obsługa błędów i testy
Aplikacja posiada zaimplementowaną obsługę własnych widoków dla błędów:
* **404:** Strona nie znaleziona.
* **500:** Błąd wewnętrzny serwera.

W folderze `tests/` znajdują się testy jednostkowe weryfikujące poprawność ładowania widoków, mechanizm rejestracji oraz integralność modeli bazy danych.

## 5. Instrukcja uruchomienia
1.  Instalacja wymaganych bibliotek:  
    `pip install -r requirements.txt`
2.  Uruchomienie głównego pliku aplikacji:  
    `python app.py`
3.  Aplikacja automatycznie utworzy plik bazy danych `users.db` oraz katalog `repos/` na dane projektowe przy pierwszym uruchomieniu.
4.  Dostęp do systemu odbywa się pod adresem: `http://127.0.0.1:5000`