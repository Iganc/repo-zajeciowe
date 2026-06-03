import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier

def get_models():
    return {
        "KNN_k5": KNeighborsClassifier(n_neighbors=5),
        "KNN_k15_Manhattan": KNeighborsClassifier(n_neighbors=15, metric='manhattan'),
        "Decision_Tree": DecisionTreeClassifier(max_depth=5, random_state=42),
        "Naive_Bayes": GaussianNB(),
        "Neural_Network_MLP": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
    }

def train_and_export():
    print("Przygotowywanie danych do trenowania...")
    try:
        df = pd.read_csv("Final Dataset.csv")
    except FileNotFoundError:
        print("Błąd: Brak pliku 'Final Dataset.csv'. Umieść go w katalogu projektu.")
        return
        
    df['genre'] = df['genres'].apply(lambda x: str(x).strip("[]'\" ").split(',')[0].strip(" '\"").capitalize())
    df = df[df['genre'] != 'Unknown']
    top_genres = df['genre'].value_counts().head(5).index.tolist()
    df = df[df['genre'].isin(top_genres)]
    df = df.groupby('genre').head(1000)
    
    X = df[['danceability', 'energy', 'acousticness', 'tempo', 'valence']]
    y = df['genre']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    imputer = SimpleImputer(strategy='mean')
    X_train_imputed = imputer.fit_transform(X_train)
    X_test_imputed = imputer.transform(X_test)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_imputed)
    X_test_scaled = scaler.transform(X_test_imputed)
    
    os.makedirs("exported_models", exist_ok=True)
    
    joblib.dump(scaler, "exported_models/music_scaler.joblib")
    joblib.dump(imputer, "exported_models/music_imputer.joblib")
    print("Zapisano scaler i imputer do folderu 'exported_models/'.\n")
    
    models = get_models()
    
    print("="*60)
    print("Trenowanie i eksport modeli")
    print("="*60)
    
    for name, model in models.items():
        print(f"Trenowanie modelu: {name}...")
        model.fit(X_train_scaled, y_train)
        
        acc = model.score(X_test_scaled, y_test)
        print(f"  - Dokładność (Accuracy): {acc:.4f}")
        
        model_filename = f"exported_models/{name}.joblib"
        joblib.dump(model, model_filename)
        print(f"  - Model zapisany jako: {model_filename}\n")

    print("="*60)
    print("PROCES ZAKOŃCZONY. Wszystkie modele wyeksportowane!")
    print("="*60)

if __name__ == "__main__":
    train_and_export()