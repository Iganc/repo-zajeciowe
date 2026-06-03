# Klasyfikator Gatunków Muzycznych - Projekt 4

**Autor:** Ignacy Mróz (Projekt samodzielny)

---

## O projekcie
Projekt stanowi logiczne połączenie dwóch wcześniejszych zadań zaliczeniowych, realizując sugerowany w wymaganiach schemat stworzenia strony internetowej integrującej model uczenia maszynowego (ML).

1. **Architektura serwerowa i webowa:** Bazuje na frameworku Flask, co stanowi bezpośrednie rozwinięcie i adaptację struktury z Projektu 2.
2. **Silnik analityczny:** Algorytmy uczenia maszynowego (K-Nearest Neighbors, Drzewo Decyzyjne, Naive Bayes oraz Sieć Neuronowa MLP) zostały przeniesione i dostosowane z Projektu 3.

### Główne usprawnienia i nowości:
* **Realny zbiór danych:** Zastosowano znacznie większy, rzeczywisty zbiór danych audio zawarty w pliku "Final Dataset.csv".
* **Probabilistyka:** Modele zostały rozbudowane o obsługę predykcji probabilistycznych (predict_proba) – zamiast jednej sztywnej decyzji, system wylicza pełny rozkład prawdopodobieństwa dla każdego gatunku.
* **Persystencja modeli:** Wszystkie wytrenowane modele wraz z obiektami transformacji danych (StandardScaler, SimpleImputer) są eksportowane za pomocą biblioteki joblib do katalogu "exported_models", skąd aplikacja dynamicznie i wydajnie je wczytuje przy starcie serwera.

---

## Działanie aplikacji webowej (Web App)
Interfejs graficzny przygotowany w szablonach Jinja2 (z dbałością o prawidłowy kontrast i estetykę UI) pozwala na interakcję z modelami na dwa sposoby:

1. **Wyszukiwanie utworów z bazy:** Użytkownik może skorzystać z wyszukiwarki przeszukującej bazę utworów w czasie rzeczywistym. Wybranie piosenki automatycznie ustawia suwaki na rzeczywiste wartości cech audio (taneczność, energia, tempo itp.), umożliwiając natychmiastową weryfikację skuteczności klasyfikatora.
2. **Własne parametry:** Ręczna manipulacja suwakami pozwala badać zachowanie algorytmów przy niestandardowych lub skrajnych kombinacjach cech.
3. **Dodawanie nowych utworów:** Aplikacja posiada wbudowany moduł integracji z polem wyszukiwania iTunes API. Użytkownik może wyszukać dowolny utwór i dodać go na stałe do lokalnej bazy danych (`Final Dataset.csv`). Dodane piosenki zostają zapisane w odpowiednim formacie i natychmiast stają się dostępne do klasyfikacji w wyszukiwarce.
Aplikacja pozwala na wybór jednego konkretnego modelu lub uruchomienie trybu porównania, w którym system wyświetla zestawienie wyników i rozkładów prawdopodobieństwa ze wszystkich algorytmów obok siebie w czytelnej tabeli.

---

## Struktura projektu i API
Projekt został podzielony modułowo zgodnie z zasadami czystego kodu (Clean Code / PEP8):
* `app.py` – główny plik uruchomieniowy serwera Flask.
* `generate_and_export.py` – skrypt odpowiedzialny za pipeline uczenia maszynowego i eksport modeli.
* `blueprints/api_routes.py` – wydzielony moduł (Blueprint) obsługujący publiczne REST API. Pozwala na zdalną klasyfikację za pomocą żądań POST, integruje aplikację z zewnętrzną usługą iTunes API w celu pobierania metadanych utworów oraz obsługuje zapis nowych piosenek bezpośrednio do pliku CSV.
---

## Jak uruchomić aplikację
1. **Instalacja wymaganych pakietów:**
```bash
   pip install -r requirements.txt

```

2. **Uruchomienie serwera Flask:**

```bash
   python app.py

```

---

## Deklaracja wykorzystania AI i wkładu własnego
Zgodnie z wytycznymi projektowymi, poniżej znajduje się opis wkładu własnego oraz narzędzi pomocniczych:

* **Wkład własny:** Architektura katalogów, logika biznesowa backendu, integracja modeli ML z Flaskiem, mechanizm dynamicznego ładowania plików .joblib, implementacja wyszukiwarki utworów w czasie rzeczywistym, struktura routingu.
* **Pomoc AI:** Wsparcie przy projektowaniu i stylowaniu warstwy wizualnej interfejsu (HTML i CSS w szablonach Jinja2), bieżącej weryfikacji, debugowaniu i sprawdzaniu poprawności napisanego kodu. Pomoc również w pisaniu README.
  * *Wykorzystany model:* Gemini 3.1 Pro (Google) - data wykorzystania: maj/czerwiec 2026 r., ostatni dostęp: 03.06.2026



---

## Bibliografia i źródła

### Wykorzystane biblioteki i frameworki:

* **Flask** (wersja podana w requirements.txt) – Pallets Projects (https://flask.palletsprojects.com/)
* **scikit-learn** (wersja podana w requirements.txt) – Pedregosa et al. (https://scikit-learn.org/)
* **pandas** (wersja podana w requirements.txt) – The pandas development team (https://pandas.pydata.org/)
* **joblib** (wersja podana w requirements.txt) – (https://joblib.readthedocs.io/)

### Zbiór danych:

* Dane audio wykorzystane w pliku `Final Dataset.csv` pochodzą z publicznego repozytorium utworów muzycznych.
