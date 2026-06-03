import os
import joblib
import requests
import pandas as pd
from flask import Blueprint, request, jsonify

api_bp = Blueprint('api', __name__, url_prefix='/api')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'exported_models')

# Wczytanie prawidłowych transformatorów
scaler = joblib.load(os.path.join(MODELS_DIR, 'music_scaler.joblib'))
imputer = joblib.load(os.path.join(MODELS_DIR, 'music_imputer.joblib'))

# Wczytanie faktycznie istniejących modeli
AVAILABLE_MODELS = ["Neural_Network_MLP", "KNN_k5", "KNN_k15_Manhattan", "Decision_Tree", "Naive_Bayes"]
ml_models = {}
for m_name in AVAILABLE_MODELS:
    ml_models[m_name] = joblib.load(os.path.join(MODELS_DIR, f"{m_name}.joblib"))

@api_bp.route('/search', methods=['GET'])
def search_track():
    """Wyszukiwanie utworów w zewnętrznym API iTunes (dodatkowa funkcjonalność)"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    try:
        url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&media=music&limit=10"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        output = []
        for item in data.get('results', []):
            output.append({
                'id': str(item.get('trackId')),
                'name': item.get('trackName'),
                'artist': item.get('artistName'),
                'album': item.get('collectionName'),
                'image_url': item.get('artworkUrl100'),
                'preview_url': item.get('previewUrl')
            })
        return jsonify(output)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/classify', methods=['POST'])
def classify_track():
    """Klasyfikacja gatunku na podstawie przesłanych cech audio utworu"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Brak danych wejściowych JSON"}), 400
        
    try:
        selected_model_key = data.get('model', 'Neural_Network_MLP')
        if selected_model_key not in ml_models:
            selected_model_key = 'Neural_Network_MLP'
            
        active_model = ml_models[selected_model_key]
        
        # Pobranie cech przesłanych w JSONIE przez użytkownika/klienta API
        try:
            features = [
                float(data['danceability']),
                float(data['energy']),
                float(data['acousticness']),
                float(data['tempo']),
                float(data['valence'])
            ]
        except KeyError as e:
            return jsonify({"error": f"Brakujący wymagany parametr cechy: {str(e)}"}), 400
        
        # Przygotowanie danych do predykcji (dokładnie tak jak w app.py)
        input_df = pd.DataFrame([features], columns=['danceability', 'energy', 'acousticness', 'tempo', 'valence'])
        features_imputed = imputer.transform(input_df)
        features_scaled = scaler.transform(features_imputed)
        
        prediction = str(active_model.predict(features_scaled)[0]).capitalize()
        
        prob_details = None
        if hasattr(active_model, "predict_proba"):
            probabilities = active_model.predict_proba(features_scaled)[0]
            prob_details = {str(cls).capitalize(): round(float(prob) * 100, 2) for cls, prob in zip(active_model.classes_, probabilities)}
            prob_details = dict(sorted(prob_details.items(), key=lambda item: item[1], reverse=True))
        
        return jsonify({
            "status": "success",
            "model_used": selected_model_key,
            "features_analyzed": {
                "danceability": features[0],
                "energy": features[1],
                "acousticness": features[2],
                "tempo": features[3],
                "valence": features[4]
            },
            "prediction": prediction,
            "probabilities": prob_details
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api_bp.route('/add_custom_track', methods=['POST'])
def add_custom_track():
    """Endpoint dodający nowy rekord utworu bezpośrednio do bazy danych CSV"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Brak danych"}), 400
        
    required = ['name', 'artist', 'genre', 'danceability', 'energy', 'acousticness', 'tempo', 'valence']
    for field in required:
        if field not in data or str(data[field]).strip() == '':
            return jsonify({"error": f"Pole {field} jest wymagane"}), 400

    try:
        # Przygotowanie wiersza dokładnie w takiej kolejności, w jakiej są kolumny w pliku CSV
        name = str(data['name']).strip().replace('"', '""')
        artist = str(data['artist']).strip().replace('"', '""')
        genre_formatted = f"['{data['genre'].strip()}']"
        
        csv_path = os.path.join(BASE_DIR, "Final Dataset.csv")
        
        # Wczytujemy z nagłówka format kolumn, aby wepchnąć wiersz w odpowiedniej budowie
        df_cols = pd.read_csv(csv_path, nrows=0).columns
        new_row_data = {col: "" for col in df_cols}
        
        new_row_data['name'] = name
        new_row_data['artist'] = artist
        new_row_data['genres'] = genre_formatted
        new_row_data['danceability'] = float(data['danceability'])
        new_row_data['energy'] = float(data['energy'])
        new_row_data['acousticness'] = float(data['acousticness'])
        new_row_data['tempo'] = float(data['tempo'])
        new_row_data['valence'] = float(data['valence'])
        
        new_row_df = pd.DataFrame([new_row_data])
        new_row_df.to_csv(csv_path, mode='a', header=False, index=False)
        
        # Prawidłowa aktualizacja pamięci podręcznej w app.py bez wywoływania problemów z importem
        import sys
        # Pobieramy glowny modul (zaleznie czy uruchomiono jako python app.py, czy flask run)
        main_app = sys.modules.get('__main__')
        if not hasattr(main_app, 'music_df'):
            main_app = sys.modules.get('app')
            
        if main_app and hasattr(main_app, 'music_df') and not main_app.music_df.empty:
            runtime_row = {
                'name': str(data['name']).strip(),
                'artist': str(data['artist']).strip(),
                'genres': genre_formatted,
                'danceability': float(data['danceability']),
                'energy': float(data['energy']),
                'acousticness': float(data['acousticness']),
                'tempo': float(data['tempo']),
                'valence': float(data['valence']),
                'genre': data['genre'].strip().capitalize()
            }
            main_app.music_df = pd.concat([main_app.music_df, pd.DataFrame([runtime_row])], ignore_index=True)

        return jsonify({"status": "success", "message": "Utwór został zapisany w bazie danych CSV."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500