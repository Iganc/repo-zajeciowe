import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, log_loss, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import learning_curve

from utils import generate_music_data, prepare_data

def get_models():
    """Definiuje 5 znacznie różniących się modeli lub konfiguracji parametrów."""
    return {
        "KNN_k5": KNeighborsClassifier(n_neighbors=5),
        "KNN_k15_Manhattan": KNeighborsClassifier(n_neighbors=15, metric='manhattan'), # Eksperyment z parametrami
        "Decision_Tree": DecisionTreeClassifier(max_depth=5, random_state=42),
        "Naive_Bayes": GaussianNB(),
        "Neural_Network_MLP": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
    }

def run_pipeline():
    if not os.path.exists("music_data.csv"):
        generate_music_data()
        
    X_train, X_test, y_train, y_test = prepare_data()
    models = get_models()
    
    print("="*60)
    print("Ewaluacja modeli")
    print("="*60)
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None
        
        acc = accuracy_score(y_test, y_pred)
        loss = log_loss(y_test, y_prob) if y_prob is not None else float('nan')
        
        print(f"\n Model: {name}")
        print(f"   - Test Accuracy: {acc:.4f}")
        print(f"   - Test Loss (Log-Loss): {loss:.4f}")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
        
        cm = confusion_matrix(y_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Rock", "Electronic", "Classical", "Pop"])
        disp.plot(ax=ax1, cmap=plt.cm.Purples, xticks_rotation=45)
        ax1.set_title(f"Confusion Matrix: {name}")
        
        train_sizes, train_scores, test_scores = learning_curve(
            model, np.vstack((X_train, X_test)), np.hstack((y_train, y_test)), 
            cv=5, scoring='accuracy', train_sizes=np.linspace(0.1, 1.0, 5), random_state=42
        )
        ax2.plot(train_sizes, np.mean(train_scores, axis=1), 'o-', color="r", label="Training score")
        ax2.plot(train_sizes, np.mean(test_scores, axis=1), 'o-', color="g", label="Cross-validation score")
        ax2.set_title(f"Learning Curve: {name}")
        ax2.set_xlabel("Training size")
        ax2.set_ylabel("Accuracy")
        ax2.legend(loc="best")
        ax2.grid(True)
        
        plt.tight_layout()
        plot_name = f"wykres_{name}.png"
        plt.savefig(plot_name)
        plt.close()
        print(f"   - Wykresy zapisano jako: {plot_name}")

    print("\n" + "="*60)
    print("PROCES ZAKOŃCZONY. Wszystkie metryki i wykresy zostały wygenerowane.")
    print("="*60)

if __name__ == "__main__":
    run_pipeline()