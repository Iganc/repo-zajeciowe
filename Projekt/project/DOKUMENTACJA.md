# DOKUMENTACJA TECHNICZNA - MyBudget

## Spis Treści
1. [Architektura Aplikacji](#architektura-aplikacji)
2. [Modele i Relacje](#modele-i-relacje)
3. [Kluczowa Logika Biznesowa](#kluczowa-logika-biznesowa)
4. [AJAX i JavaScript](#ajax-i-javascript)
5. [Komendy Management](#komendy-management)
6. [Testy i Debugowanie](#testy-i-debugowanie)

---

## Architektura Aplikacji
Projekt oparty jest na klasycznym wzorcu Django (MTV) i podzielony na trzy współpracujące aplikacje:
* **`accounts`**: Autentykacja, profile i zarządzanie kontami bankowymi (`Account`).
* **`transactions`**: Operacje finansowe (`Transaction`), kategoryzacja (`Category`) i import danych.
* **`budgets`**: Cele oszczędnościowe (`BudgetGoal`), alokacja środków i raportowanie.

---

## Modele i Relacje

* **Account:** Powiązane z `User` (FK). Przechowuje aktualne, dostępne do wydania `balance`.
* **Category:** Słownik kategorii (np. Jedzenie, Pensja). Posiada typ: `EXPENSE` lub `INCOME`.
* **Transaction:** Centralny punkt aplikacji.
    * Relacje: `Account` (wymagane), `Category` (opcjonalne), `BudgetGoal` (opcjonalne).
    * Zapis transakcji wyzwala automatyczną aktualizację salda powiązanego konta lub celu.
* **BudgetGoal:** Reprezentuje odłożone pieniądze (np. "Wakacje").
    * `allocated_amount`: Początkowa kwota zarezerwowana na cel.
    * `balance`: Środki pozostałe do wydania w ramach tego celu.

---

## Kluczowa Logika Biznesowa

Sercem aplikacji jest mechanizm **separacji salda konta od budżetów celowych**, realizowany w widokach `transactions/views.py` oraz `budgets/views.py`:

1.  **Rezerwacja środków:** Utworzenie `BudgetGoal` na 500 zł natychmiast pomniejsza `balance` powiązanego `Account` o 500 zł. Środki te "przechodzą" do `balance` w modelu `BudgetGoal`.
2.  **Wydatek celowy:** Dodanie transakcji przypisanej do `BudgetGoal` pomniejsza wyłącznie saldo tego celu. Saldo `Account` pozostaje bez zmian (środki zostały pobrane już wcześniej).
3.  **Zwykły wydatek:** Transakcja bez podanego celu zmniejsza (EXPENSE) lub zwiększa (INCOME) bezpośrednio `balance` w `Account`.
4.  **Zarządzanie cyklem życia:** Usunięcie transakcji lub celu budżetowego automatycznie odwraca operację i zwraca odpowiednie środki na konto bazowe.

---

## AJAX i JavaScript

Aplikacja wykorzystuje Vanilla JS i `fetch API` (Endpoint: `GET /transactions/api/budget-goals/?account_id=...`) do poprawy UX w formularzu dodawania transakcji.
* **Działanie:** Wybranie konta z listy rozwijanej dynamicznie ładuje tylko te cele budżetowe, które są przypisane do wskazanego konta i zalogowanego użytkownika, parsując dane z JSON i formatując kwoty (Decimal -> Float).

---

## Komendy Management (CLI)

Zaimplementowano 3 autorskie komendy w Django:
1.  **`import_transactions_csv`:** Przetwarza plik CSV, weryfikuje dane, automatycznie tworzy brakujące kategorie i zbiorczo aktualizuje salda.
2.  **`delete_old_transactions --days N`:** Usuwa wpisy starsze niż *N* dni. Posiada flagę `--dry-run` do bezpiecznego podglądu operacji przed wykonaniem. Koryguje salda podczas usuwania.
3.  **`generate_budget_report`:** Agreguje przychody, wydatki i postępy celów dla wskazanego użytkownika, zwracając wynik w terminalu (`text`) lub generując plik (`csv`).

---

## Testy i Debugowanie

Zestaw 24 testów automatycznych (100% PASS) pokrywających główne moduły.

**Najczęstsze problemy rozwiązane w projekcie:**
* *TypeError (Decimal vs Float):* Rozwiązano poprzez rzutowanie typów podczas obliczeń krzyżowych w logice alokacji bazy danych.
* *Atrybuty Nullable:* Dodano odpowiednią obsługę w szablonach HTML (`{% if %}`) dla starych transakcji nieposiadających przypisanej kategorii (`models.SET_NULL`).
* *Serializacja JSON:* Konwersja pól `Decimal` na `float` w widokach API, aby uniknąć błędów parsowania w po stronie klienta (JavaScript).

---
**Autor:** Ignacy Mróz | **Data:** 24.03.2026 | **Status:** ✅ Complete & Tested