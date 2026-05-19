import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

def generate_music_data(filename="music_data.csv", n_samples=800):
    np.random.seed(42)
    genres = np.random.choice([0, 1, 2, 3], size=n_samples)
    
    danceability = np.zeros(n_samples)
    energy = np.zeros(n_samples)
    acousticness = np.zeros(n_samples)
    tempo = np.zeros(n_samples)
    valence = np.zeros(n_samples)
    
    for i, g in enumerate(genres):
        if g == 0:
            danceability[i] = np.random.normal(0.5, 0.1)
            energy[i] = np.random.normal(0.7, 0.1)
            acousticness[i] = np.random.normal(0.1, 0.05)
            tempo[i] = np.random.normal(120, 15)
            valence[i] = np.random.normal(0.5, 0.15)
        elif g == 1:
            danceability[i] = np.random.normal(0.8, 0.08)
            energy[i] = np.random.normal(0.85, 0.08)
            acousticness[i] = np.random.normal(0.05, 0.03)
            tempo[i] = np.random.normal(128, 10)
            valence[i] = np.random.normal(0.6, 0.12)
        elif g == 2:
            danceability[i] = np.random.normal(0.2, 0.1)
            energy[i] = np.random.normal(0.15, 0.08)
            acousticness[i] = np.random.normal(0.85, 0.08)
            tempo[i] = np.random.normal(80, 20)
            valence[i] = np.random.normal(0.25, 0.15)
        else:
            danceability[i] = np.random.normal(0.7, 0.1)
            energy[i] = np.random.normal(0.65, 0.1)
            acousticness[i] = np.random.normal(0.2, 0.1)
            tempo[i] = np.random.normal(115, 12)
            valence[i] = np.random.normal(0.7, 0.1)

    df = pd.DataFrame({
        'danceability': danceability, 'energy': energy, 
        'acousticness': acousticness, 'tempo': tempo, 
        'valence': valence, 'genre': genres
    })
    
    for col in ['danceability', 'energy', 'acousticness', 'valence']:
        df[col] = df[col].clip(0, 1)
        
    for col in ['energy', 'tempo']:
        mask = np.random.rand(len(df)) < 0.04
        df.loc[mask, col] = np.nan
        
    df.to_csv(filename, index=False)

def prepare_data(filename="music_data.csv"):
    df = pd.read_csv(filename)
    X = df.drop(columns=['genre'])
    y = df['genre']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    imputer = SimpleImputer(strategy='mean')
    X_train_imputed = imputer.fit_transform(X_train)
    X_test_imputed = imputer.transform(X_test)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_imputed)
    X_test_scaled = scaler.transform(X_test_imputed)
    
    return X_train_scaled, X_test_scaled, y_train, y_test