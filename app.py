import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="TCG Market Predictor", layout="wide")

st.title("⚡ TCG Market AI : Prédiction de prix")
st.markdown("Analyse de tendance et prédiction algorithmique pour cartes de collection.")

# --- BARRE LATÉRALE (Inputs) ---
st.sidebar.header("Paramètres de la Carte")
card_name = st.sidebar.text_input("Nom de la carte", "Dracaufeu Base Set 1st Ed.")
current_price = st.sidebar.number_input("Dernier prix vendu (€)", value=3500)
volatility = st.sidebar.slider("Volatilité du marché", 0.1, 1.0, 0.3)

# --- GÉNÉRATION DE DONNÉES SIMULÉES (DATA MOCK) ---
# On crée un historique fictif de 6 mois pour montrer qu'on sait gérer de la data
np.random.seed(42)
days = np.arange(1, 180)
# Formule pour créer une courbe réaliste avec du bruit aléatoire
prices = 2000 + (days * 15) + np.random.normal(0, 200 * volatility, len(days))

df = pd.DataFrame({'Jour': days, 'Prix': prices})

# --- PARTIE INTELLIGENCE ARTIFICIELLE (Machine Learning) ---
# Préparation des données pour le modèle
X = df[['Jour']]
y = df['Prix']

# Entraînement du modèle (Régression Linéaire)
model = LinearRegression()
model.fit(X, y)

# Prédiction pour les 30 prochains jours
future_days = np.arange(180, 210).reshape(-1, 1)
future_prices = model.predict(future_days)

# --- VISUALISATION ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📊 Analyse : {card_name}")
    st.line_chart(df.set_index('Jour'))

with col2:
    st.subheader("🤖 Prédiction IA (30 jours)")
    
    # Calcul de la tendance
    trend = "HAUSSIÈRE 📈" if future_prices[-1] > prices[-1] else "BAISSIÈRE 📉"
    predicted_val = round(future_prices[-1], 2)
    
    st.metric(label="Prix prédit à J+30", value=f"{predicted_val} €", delta=trend)
    
    st.write("Le modèle de régression linéaire analyse l'historique pour projeter la tendance future. "
             "Outil d'aide à la décision pour investisseurs TCG.")

# --- FOOTER ---
st.markdown("---")
st.caption("Développé avec Python (Pandas, Scikit-Learn, Streamlit) par [TON NOM]")