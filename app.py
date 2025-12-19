import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="TCG Market Predictor", layout="wide")
st.title("⚡ TCG Market AI : Advanced Analytics")

# --- FONCTION DE RECHERCHE API ---
@st.cache_data # Cette ligne garde les résultats en mémoire pour que ça aille vite
def search_pokemon_cards(pokemon_name):
    # On ajoute une étoile * pour faire une recherche large
    url = f"https://api.pokemontcg.io/v2/cards?q=name:{pokemon_name}*"
    try:
        response = requests.get(url)
        data = response.json()
        return data['data'] if 'data' in data else []
    except:
        return []

# --- SIDEBAR : LE MOTEUR DE RECHERCHE ---
st.sidebar.header("🔍 Recherche de Carte")

# 1. L'utilisateur tape le nom global
name_query = st.sidebar.text_input("1. Tapez un nom (ex: Jolteon)", "Jolteon")

selected_card_data = None

if name_query:
    # 2. On récupère TOUTES les versions de ce Pokémon
    results = search_pokemon_cards(name_query)
    
    if results:
        # 3. On crée une liste propre pour le menu déroulant
        # Format : "Nom (Numéro) - [Set]" -> ex: "Jolteon (153/131) - [Prismatic]"
        card_options = {
            f"{card['name']} ({card.get('number', '?')}/{card.get('set', {}).get('printedTotal', '?')}) - [{card['set']['name']}]": card 
            for card in results
        }
        
        # 4. Le menu déroulant qui permet de filtrer en tapant
        st.sidebar.write("2. Sélectionnez la version exacte :")
        selected_option = st.sidebar.selectbox(
            "Filtrer par numéro (ex: tapez '153')", 
            options=list(card_options.keys())
        )
        
        # On récupère les infos de la carte choisie
        selected_card_data = card_options[selected_option]
        
    else:
        st.sidebar.warning("Aucun résultat trouvé.")

volatility = st.sidebar.slider("Volatilité du marché", 0.1, 1.0, 0.4)

# --- AFFICHAGE PRINCIPAL ---
if selected_card_data:
    # Extraction des données propres
    card_name = selected_card_data['name']
    card_img = selected_card_data['images']['large']
    
    # Gestion du prix (parfois manquant dans l'API)
    try:
        price = selected_card_data['tcgplayer']['prices']['holofoil']['market']
    except:
        try:
            price = selected_card_data['tcgplayer']['prices']['normal']['market']
        except:
            price = None # Prix inconnu

    # Si pas de prix, on met une valeur par défaut pour la démo
    if price is None:
        price = 25.0
        st.warning("Prix de marché introuvable, simulation basée sur une valeur par défaut.")

    # --- VISUEL ---
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(card_img, use_container_width=True)
        st.caption(f"Set : {selected_card_data['set']['name']}")

    with col2:
        st.subheader(f"📊 Analyse Financière : {card_name}")
        st.metric("Prix Actuel (Moyenne TCG)", f"{price} $")

        # --- SIMULATION INTELLIGENTE ---
        # On recrée l'histoire pour arriver à ce prix exact
        days = np.arange(1, 180)
        
        # Logique : Prix de départ aléatoire mais cohérent
        start_price = price * (0.7 + np.random.rand() * 0.5)
        slope = (price - start_price) / 180
        
        # Génération de la courbe
        simulated_prices = start_price + (days * slope) + np.random.normal(0, price * volatility * 0.1, len(days))
        
        df = pd.DataFrame({'Jour': days, 'Prix': simulated_prices})
        st.line_chart(df.set_index('Jour'))

        # --- PREDICTION IA ---
        X = df[['Jour']]
        y = df['Prix']
        model = LinearRegression()
        model.fit(X, y)
        
        future_days = np.arange(180, 210).reshape(-1, 1)
        future_pred = model.predict(future_days)[-1]
        
        delta = round(future_pred - price, 2)
        st.success(f"Prédiction IA à 30 jours : {round(future_pred, 2)} $ ({'+' if delta>0 else ''}{delta} $)")
        
        st.info("Algorithme : Régression Linéaire sur données TCGPlayer (Simulées sur l'historique).")

else:
    st.info("👈 Commencez par taper un nom de Pokémon dans la barre latérale.")
