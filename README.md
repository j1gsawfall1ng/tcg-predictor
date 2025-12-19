# ⚡ TCG Market AI - Pokémon Price Predictor

**Voir la démo en ligne :** https://tcg-predictor-gfmuqkdx8vc6yl8segvmbv.streamlit.app/

## 📝 C'est quoi ce projet ?
C'est une application web d'analyse de prix pour les cartes Pokémon.
N'ayant pas de diplôme mais étant passionné par le code et les TCG (Trading Card Games), j'ai voulu construire un outil concret qui combine les deux.

L'idée : récupérer les infos d'une carte en temps réel et utiliser un algorithme simple pour visualiser une tendance de prix.

## 🚀 Ce que ça fait
* **Recherche API :** Connecté à l'API officielle *Pokémon TCG*. Tu tapes "Pikachu", ça trouve toutes les versions.
* **Données Réelles :** Affiche la vraie date de sortie et le vrai prix du marché actuel (via TCGPlayer).
* **Graphiques Interactifs :** Visualisation de la courbe de prix sur 6 mois ou plus.
* **Prédiction IA :** Un modèle de **Régression Linéaire** (Scikit-Learn) calcule une projection du prix à 30 jours.

## 🛠️ Stack Technique
Ce projet a été codé en Python.
* **Interface :** Streamlit
* **Data :** Pandas & NumPy
* **Machine Learning :** Scikit-Learn
* **API :** Requests

## ⚙️ Tester le projet en local

1. **Cloner le projet :**
   ```bash
   git clone [https://github.com/TON-PSEUDO/tcg-predictor.git](https://github.com/TON-PSEUDO/tcg-predictor.git)
   cd tcg-predictor

2.   **Installer les librairies :**

Bash

pip install -r requirements.txt

3.   **Lancer l'app :**

Bash

streamlit run app.py
