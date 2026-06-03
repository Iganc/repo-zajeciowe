from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import os
from blueprints.api_routes import api_bp  # Importujemy blueprint

app = Flask(__name__)

# Rejestracja blueprintu API
app.register_blueprint(api_bp)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "exported_models")

scaler = joblib.load(os.path.join(MODELS_DIR, "music_scaler.joblib"))
imputer = joblib.load(os.path.join(MODELS_DIR, "music_imputer.joblib"))

DATASET_PATH = os.path.join(BASE_DIR, "Final Dataset.csv")
try:
    music_df = pd.read_csv(DATASET_PATH, usecols=['name', 'artist', 'genres', 'danceability', 'energy', 'acousticness', 'tempo', 'valence'])
    music_df = music_df.drop_duplicates(subset=['name', 'artist']).fillna(0)
    music_df['genre'] = music_df['genres'].apply(lambda x: str(x).strip("[]'\" ").split(',')[0].strip(" '\"").capitalize())
except Exception as e:
    music_df = pd.DataFrame()

AVAILABLE_MODELS = {
    "Neural_Network_MLP": "Sieć Neuronowa (MLP)",
    "KNN_k5": "K-Nearest Neighbors (k=5)",
    "KNN_k15_Manhattan": "K-Nearest Neighbors (k=15, Manhattan)",
    "Decision_Tree": "Drzewo Decyzyjne",
    "Naive_Bayes": "Naiwny Klasyfikator Bayesa"
}

models = {name: joblib.load(os.path.join(MODELS_DIR, f"{name}.joblib")) for name in AVAILABLE_MODELS.keys()}

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    probabilities = None
    all_predictions = None
    true_genre = None
    song_name = None
    selected_model_name = "Neural_Network_MLP"
    
    if request.method == "POST":
        try:
            danceability = float(request.form.get("danceability", 0.5))
            energy = float(request.form.get("energy", 0.5))
            acousticness = float(request.form.get("acousticness", 0.5))
            tempo = float(request.form.get("tempo", 120))
            valence = float(request.form.get("valence", 0.5))
            
            selected_model_name = request.form.get("model_choice", "Neural_Network_MLP")
            evaluate_all = request.form.get("evaluate_all") == "on"
            true_genre = request.form.get("true_genre", "")
            song_name = request.form.get("song_name", "")
            
            input_data = pd.DataFrame([[danceability, energy, acousticness, tempo, valence]], 
                                      columns=['danceability', 'energy', 'acousticness', 'tempo', 'valence'])
            
            input_imputed = imputer.transform(input_data)
            input_scaled = scaler.transform(input_imputed)
            
            if evaluate_all:
                all_predictions = {}
                for m_name, m_inst in models.items():
                    p_raw = str(m_inst.predict(input_scaled)[0])
                    p_clean = p_raw.capitalize()
                    
                    m_probs = None
                    if hasattr(m_inst, "predict_proba"):
                        raw_probs = m_inst.predict_proba(input_scaled)[0]
                        prob_dict = {str(cls).capitalize(): round(prob * 100, 1) for cls, prob in zip(m_inst.classes_, raw_probs)}
                        m_probs = dict(sorted(prob_dict.items(), key=lambda item: item[1], reverse=True))
                    
                        max_prob = max(m_probs.values())
                        top_genres = [genre for genre, prob in m_probs.items() if prob == max_prob]
                        p_clean = " / ".join(top_genres)
                        
                    all_predictions[AVAILABLE_MODELS[m_name]] = {
                        "prediction": p_clean,
                        "probabilities": m_probs
                    }
            else:
                model = models.get(selected_model_name, models["Neural_Network_MLP"])
                pred_raw = str(model.predict(input_scaled)[0])
                prediction = pred_raw.capitalize()
                
                if hasattr(model, "predict_proba"):
                    probs = model.predict_proba(input_scaled)[0]
                    prob_dict = {str(cls).capitalize(): round(prob * 100, 1) for cls, prob in zip(model.classes_, probs)}
                    probabilities = dict(sorted(prob_dict.items(), key=lambda item: item[1], reverse=True))
                    
                    max_prob = max(probabilities.values())
                    top_genres = [genre for genre, prob in probabilities.items() if prob == max_prob]
                    prediction = " / ".join(top_genres)
            
        except Exception as e:
            prediction = f"Wystąpił błąd: {str(e)}"
            
    return render_template("index.html", 
                           prediction=prediction, 
                           probabilities=probabilities,
                           all_predictions=all_predictions,
                           true_genre=true_genre,
                           song_name=song_name,
                           available_models=AVAILABLE_MODELS, 
                           selected_model_name=selected_model_name)

@app.route("/api/search_song", methods=["GET"])
def search_song():
    query = request.args.get("q", "").strip()
    if not query or music_df.empty:
        return jsonify([])

    match = music_df[music_df['name'].str.contains(query, case=False, na=False, regex=False)]
    
    results = []
    for _, row in match.head(5).iterrows():
        results.append({
            "name": row['name'],
            "artist": row['artist'],
            "genre": row['genre'],
            "danceability": float(row['danceability']),
            "energy": float(row['energy']),
            "acousticness": float(row['acousticness']),
            "tempo": float(row['tempo']),
            "valence": float(row['valence'])
        })
        
    return jsonify(results)

@app.route("/add-track", methods=["GET"])
def add_track_page():
    """Podstrona służąca do wyszukiwania w iTunes i dodawania piosenek do CSV"""
    return render_template("add_track.html")

if __name__ == "__main__":
    app.run(debug=True)