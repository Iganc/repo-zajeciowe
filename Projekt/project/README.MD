# MyBudget 

**Autor:** Ignacy Mróz | **Ostatnia aktualizacja:** 24.03.2026

## 🛠 Technologie
* **Backend:** Python 3.13.12, Django 6.0.3
* **Baza Danych:** SQLite
* **Frontend:** HTML5, CSS3, Bootstrap 5.3.0

---

## 🚀 Szybki Start

Instrukcja uruchomienia projektu w środowisku lokalnym:

```bash
# 1. Klonuj projekt i wejdź do folderu
cd myProject

# 2. Stwórz i aktywuj wirtualne środowisko
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Zainstaluj zależności
pip install django djangorestframework

# 4. Wykonaj migracje bazy danych
python manage.py migrate

# 5. Uruchom serwer testowy
python manage.py runserver
# Aplikacja będzie dostępna pod adresem: [http://127.0.0.1:8000](http://127.0.0.1:8000)
```

---

## ✨ Kluczowe Funkcjonalności

* **Multi-Account:** Możliwość zarządzania wieloma kontami bankowymi w ramach jednego profilu użytkownika.
* **Inteligentny Budżet:** System rezerwacji środków na cele (np. "Wakacje"). Alokacja automatycznie koryguje dostępne saldo konta.
* **Kategoryzacja i CRUD:** Pełne zarządzanie transakcjami (przychody/wydatki) z dynamicznym filtrowaniem.
* **Narzędzia Danych (CSV):** Import transakcji z plików CSV (wraz z automatycznym tworzeniem kategorii) oraz generator raportów finansowych.
* **Bezpieczeństwo:** Rejestracja, logowanie i ochrona widoków (`@login_required`). Użytkownik ma dostęp wyłącznie do własnych danych.

---

## 💰 Logika Alokacji Budżetu

Głównym mechanizmem wyróżniającym aplikację jest inteligentna separacja salda głównego od funduszy celowych:

* **1. Planowanie celu:** Utworzenie celu „Wakacje” (np. na 5000 zł) określa docelową kwotę, ale nie blokuje jej natychmiastowo. Saldo główne pomniejsza się sukcesywnie tylko o realnie wpłacane na ten cel raty lub nadwyżki.
* **2. Wydatki celowe:** Transakcja powiązana z celem „Wakacje” pomniejsza wyłącznie zgromadzony budżet tego celu, nie wpływając na bieżące saldo operacyjne (środki zostały zabezpieczone wcześniej).
* **3. Anulowanie:** Usunięcie celu budżetowego powoduje automatyczny zwrot wszystkich dotychczas przypisanych do niego środków z powrotem na saldo główne konta.

---

## 💻 Komendy CLI (Management Commands)

Aplikacja zawiera autorskie komendy ułatwiające zarządzanie danymi:

* **Import transakcji:**
  ```bash
  python manage.py import_transactions_csv plik.csv --user username
  ```
* **Czyszczenie historii** (usuwanie transakcji starszych niż 30 dni, wspiera `--dry-run`):
  ```bash
  python manage.py delete_old_transactions --days 30
  ```
* **Generowanie raportów** (dostępne formaty: `text`, `csv`):
  ```bash
  python manage.py generate_budget_report --user username --format csv --output raport.csv
  ```

---

## 📁 Struktura Aplikacji

Projekt został podzielony na 3 główne moduły (Django Apps) zgodnie z dobrymi praktykami:

```text
myProject/
├── accounts/      # Autentykacja, profile i zarządzanie kontami (saldami)
├── transactions/  # Kategorie, operacje finansowe (CRUD) oraz import CSV
├── budgets/       # Cele oszczędnościowe, płatności cykliczne i raporty
└── templates/     # Globalne szablony HTML (base.html, błędy 404/500)
```

---

## 🧪 Testy Automatyczne

Projekt posiada 100% pokrycia dla kluczowych procesów biznesowych (modele, widoki, walidacja formularzy, logika alokacji).

```bash
# Uruchomienie wszystkich 24 testów
python manage.py test
```
## ✅ Realizacja Wymagań Projektowych

Poniżej zestawienie spełnionych wymagań technicznych dla projektu:

### Wymagania Podstawowe:
* **Przynajmniej 5 podstron:** Zrealizowano (Dashboard, Logowanie, Rejestracja, Lista Transakcji, Dodawanie Transakcji, Lista Budżetów, Szczegóły Celu).
* **Komunikacja z bazą danych (CRUD):** Zrealizowano dla modeli `Transaction` oraz `BudgetGoal`.
* **Widoki:** Wykorzystano zarówno FBV (Function-based views, np. do prostych formularzy), jak i CBV (Class-based views, np. autentykacja).
* **Modele i relacje:** Zrealizowano 5 modeli danych: `User` (Django auth), `Account`, `Category`, `Transaction`, `BudgetGoal`. Relacje `ForeignKey` (OneToMany) łączą użytkownika z kontami, a transakcje z kontami i kategoriami.
* **Formularze:** Zrealizowano m.in. `TransactionForm`, `BudgetGoalForm`, formularze rejestracji.
* **Obsługa błędów 404 i 500:** Stworzono niestandardowe szablony `404.html` i `500.html`.
* **Samodzielne polecenia `manage.py` (3 sztuki):** 1. `import_transactions_csv` - import bazy z pliku CSV.
  2. `delete_old_transactions` - usuwanie przedawnionych logów (obsługuje `--dry-run`).
  3. `generate_budget_report` - generowanie raportów do pliku.
* **Testy:** Zaimplementowano 24 testy sprawdzające m.in. alokację salda (plik `tests.py`).

### Wymagania Dodatkowe (Zrealizowano minimum 3):
1. **Stylizacja z wykorzystaniem CSS/frameworka:** Aplikacja używa **Bootstrap 5.3.0** do budowy interfejsu (grid, przyciski, tabele, responsywność).
2. **Możliwość tworzenia kont przez użytkowników oraz logowania:** Zaimplementowano pełny system uwierzytelniania w aplikacji `accounts`.
3. **Zaawansowane Opcje:** Możliwość generowania raportów w plikach csv.

---