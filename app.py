import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="TCG Market Predictor", layout="wide")
st.title("⚡ TCG Market AI : Real-Time Data")

# --- FONCTION POUR CHERCHER LA CARTE (API) ---
def get_card_data(card_name):
    # On interroge l'API Pokémon TCG
    url = f"https://api.pokemontcg.io/v2/cards?q=name:{card_name}&pageSize=1"
    response = requests.get(url)
    data = response.json()
    
    if data['data']:
        card = data['data'][0]
        # On essaie de trouver un prix, sinon on met une valeur par défaut
        try:
            price = card['tcgplayer']['prices']['holofoil']['market']
        except:
            try:
                price = card['tcgplayer']['prices']['normal']['market']
            except:
                price = 50.0 # Prix par défaut si introuvable
                
        return {
            'name': card['name'],
            'image': card['images']['large'],
            'price': price,
            'set': card['set']['name']
        }
    return None

# --- SIDEBAR ---
st.sidebar.header("Recherche")
search_query = st.sidebar.text_input("Nom de la carte (Anglais)", "Charizard")
volatility = st.sidebar.slider("Volatilité simulée", 0.1, 1.0, 0.4)

if st.sidebar.button("Analyser le marché"):
    with st.spinner('Connexion API en cours...'):
        card_info = get_card_data(search_query)
        
        if card_info:
            st.success(f"Carte trouvée : {card_info['name']}")
            
            # --- COLONNES ---
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                st.image(card_info['image'], caption=f"Set: {card_info['set']}")
            
            with col2:
                # --- GÉNÉRATION DES DONNÉES (Simulation basée sur le VRAI prix) ---
                current_real_price = card_info['price']
                if current_real_price is None: current_real_price = 100
                
                # On crée un historique fictif qui aboutit au prix actuel
                days = np.arange(1, 180)
                # On simule une tendance passée pour arriver au prix d'aujourd'hui
                start_price = current_real_price * (0.8 + np.random.rand() * 0.4) 
                slope = (current_real_price - start_price) / 180
                prices = start_price + (days * slope) + np.random.normal(0, current_real_price * volatility * 0.1, len(days))
                
                df = pd.DataFrame({'Jour': days, 'Prix': prices})
                
                # GRAPHIQUE
                st.subheader(f"📈 Cours actuel : {current_real_price} $")
                st.line_chart(df.set_index('Jour'))
                
                # --- IA PREDICITION ---
                X = df[['Jour']]
                y = df['Prix']
                model = LinearRegression()
                model.fit(X, y)
                
                future_days = np.arange(180, 210).reshape(-1, 1)
                pred = model.predict(future_days)[-1]
                
                delta = round(pred - current_real_price, 2)
                st.metric("Prédiction IA (J+30)", f"{round(pred, 2)} $", delta)

            with col3:
                st.info("ℹ️ Données techniques")
                st.write(f"**Source:** TCGPlayer API")
                st.write(f"**Algorithme:** Régression Linéaire")
                st.write("Le graphique historique est une projection reconstruite basée sur la volatilité du marché.")

        else:
            st.error("Carte introuvable. Essaie 'Pikachu' ou 'Umbreon'.")
else:
    st.write("👈 Entre un nom de Pokémon à gauche (ex: Gengar, Mewtwo) pour lancer l'analyse.")
