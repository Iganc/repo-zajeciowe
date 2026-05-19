# Projekt III: Klasyfikator Gatunków Muzycznych (ML)

## Opis Projektu
Projekt realizuje zadanie wieloklasowej klasyfikacji gatunków muzycznych (*Rock, Electronic, Classical, Pop*) na podstawie zestawu pięciu cech numerycznych audio: *danceability, energy, acousticness, tempo, valence*.

## Wykorzystane Elementy Techniczne
1. **Pre-processing danych:** - Obsługa brakujących wartości (`SimpleImputer` ze strategią uzupełniania średnią).
   - Skalowanie i normalizacja cech za pomocą `StandardScaler`.
2. **Użyte Modele (5 konfiguracji):**
   - K-Najbliższych Sąsiadów (k=5)
   - K-Najbliższych Sąsiadów (k=15, metryka Manhattan) - eksperyment z hiperparametrami
   - Drzewo Decyzyjne (max_depth=5)
   - Naiwny Klasyfikator Bayesowski (GaussianNB)
   - Wielowarstwowa Sieć Neuronowa (MLPClassifier)

## Wybór Najlepszego Modelu i Uzasadnienie
Najwyższą skutecznością na zbiorze testowym (Test Accuracy: 95.00%) charakteryzują się ex aequo **Naiwny Klasyfikator Bayesowski (GaussianNB)** oraz **Wielowarstwowa Sieć Neuronowa (MLPClassifier)**. 

Jako ostatecznie najlepszy model wskazany zostaje **Naiwny Klasyfikator Bayesowski**, ponieważ:
1. Osiągnął niższy błąd straty (**Test Loss: 0.1224** w porównaniu do 0.1683 w przypadku sieci neuronowej).
2. Jest algorytmem stabilnym probabilistycznie dla tego zbioru danych, podczas gdy sieć MLP przy 500 iteracjach optymalizatora stochastycznego zgłaszała ostrzeżenia o braku pełnej zbieżności (ConvergenceWarning), co wymagałoby dalszego podnoszenia kosztownych obliczeniowo hiperparametrów (np. `max_iter`).

### Specyfikacja Bibliotek
* Python 3.13 (Standard Library)
* scikit-learn (Implementacja algorytmów ML i metryk ewaluacji)
* pandas & numpy (Przetwarzanie macierzowe i analiza danych)
* matplotlib (Generowanie wykresów)