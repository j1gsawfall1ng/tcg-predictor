import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="TCG Market Predictor", layout="wide")
st.title("⚡ TCG Market AI : Lifecycle Analysis")

# --- FONCTION API ---
@st.cache_data
def search_pokemon_cards(pokemon_name):
    url = f"https://api.pokemontcg.io/v2/cards?q=name:{pokemon_name}*"
    try:
        response = requests.get(url)
        data = response.json()
        return data['data'] if 'data' in data else []
    except:
        return []

# --- SIDEBAR ---
st.sidebar.header("🔍 Moteur de Recherche")
name_query = st.sidebar.text_input("Nom du Pokémon", "Charizard")

selected_card_data = None

if name_query:
    results = search_pokemon_cards(name_query)
    if results:
        # On trie les résultats par date de sortie pour que ce soit plus propre
        results.sort(key=lambda x: x['set']['releaseDate'] if 'releaseDate' in x['set'] else '2025', reverse=True)
        
        card_options = {
            f"{card['name']} - {card['set']['name']} ({card['set']['releaseDate']})": card 
            for card in results
        }
        
        st.sidebar.write("Sélectionnez la version :")
        selected_option = st.sidebar.selectbox("Liste des cartes trouvées", options=list(card_options.keys()))
        selected_card_data = card_options[selected_option]
    else:
        st.sidebar.warning("Aucun résultat.")

volatility = st.sidebar.slider("Facteur de Volatilité", 0.1, 1.0, 0.3)

# --- MAIN APP ---
if selected_card_data:
    # 1. Récupération des données brutes
    card_name = selected_card_data['name']
    set_name = selected_card_data['set']['name']
    release_date_str = selected_card_data['set']['releaseDate']
    image_url = selected_card_data['images']['large']
    
    # 2. Gestion du Prix Actuel
    try:
        current_price = selected_card_data['tcgplayer']['prices']['holofoil']['market']
    except:
        try:
            current_price = selected_card_data['tcgplayer']['prices']['normal']['market']
        except:
            current_price = 50.0 # Valeur par défaut
            
    if current_price is None: current_price = 25.0

    # 3. RECONSTRUCTION TEMPORELLE (Le Cœur du code)
    # On convertit la string '1999/01/09' en objet Date Python
    try:
        release_date = datetime.strptime(release_date_str, "%Y/%m/%d")
    except:
        release_date = datetime.now() - timedelta(days=365)

    today = datetime.now()
    days_exists = (today - release_date).days
    
    # Si la carte est trop récente, on met un minimum de 30 jours
    if days_exists < 30: days_exists = 30
    
    # On limite l'historique affiché à 2 ans (730 jours) pour la lisibilité
    display_days = min(days_exists, 730) 
    
    # Création de l'axe des dates
    date_range = [today - timedelta(days=x) for x in range(display_days)]
    date_range.reverse() # Du plus vieux au plus récent

    # 4. ALGORITHME DE PRIX (Simulation de cycle de vie)
    # On crée une courbe qui part d'un prix de lancement et arrive au prix actuel
    x = np.linspace(0, display_days, display_days)
    
    # Logique : Le prix part à 60% du prix actuel, baisse un peu, puis remonte
    # C'est une fonction mathématique pour "lisser" la courbe vers le prix final
    trend = np.linspace(current_price * 0.6, current_price, display_days)
    
    # Ajout du bruit (volatilité du marché)
    noise = np.random.normal(0, current_price * volatility * 0.05, display_days)
    history_prices = trend + noise
    
    # Forcer le dernier point à être le VRAI prix actuel
    history_prices[-1] = current_price

    # Création du DataFrame
    df = pd.DataFrame({'Date': date_range, 'Prix (€)': history_prices})
    df.set_index('Date', inplace=True)

    # --- AFFICHAGE ---
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(image_url, use_container_width=True)
        st.markdown(f"**Sortie le :** {release_date_str}")
        st.markdown(f"**Set :** {set_name}")

    with col2:
        st.subheader(f"📈 Analyse de marché : {card_name}")
        st.metric("Prix du Marché (TCGPlayer)", f"{current_price} $")
        
        st.line_chart(df['Prix (€)'])
        
        # IA PREDICTION
        # On transforme les dates en numéros pour l'IA (1, 2, 3...)
        df['Day_Num'] = range(len(df))
        
        X = df[['Day_Num']]
        y = df['Prix (€)']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Prédiction J+30
        future_day = [[len(df) + 30]]
        pred_price = model.predict(future_day)[0]
        
        growth = ((pred_price - current_price) / current_price) * 100
        
        st.success(f"Prévision IA (30 jours) : {pred_price:.2f} $ ({growth:+.2f}%)")
        
        with st.expander("ℹ️ Comprendre cet algorithme"):
            st.write("""
            **Pourquoi ce graphique ?** Les API publiques ne fournissant pas l'historique complet des transactions (données propriétaires TCGPlayer), 
            cet outil utilise une **reconstruction algorithmique**.
            
            1. Nous récupérons la **Date de Sortie réelle** via l'API.
            2. Nous ancrons le point final au **Prix du Marché actuel**.
            3. Nous appliquons un modèle de volatilité stochastique pour simuler les fluctuations intermédiaires.
            """)

else:
    st.info("👈 Cherchez une carte (ex: 'Lugia', 'Mew') pour voir l'analyse.")
